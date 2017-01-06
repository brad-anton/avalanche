import json

from collections import deque

class Plugin(object):
	def __init__(self):
		pass

	@staticmethod
	def get_attribute(info, key, key_type=unicode(), default=None):
		"""Parses 'info' to check if the key attribute exists
		and is of type 'type'. If not, return default.

		Keyword Arguments:
		info -- dictionary containing plugin information
		key -- dictionary key to check
		type -- class that info[key] should be
		default -- default value to use if parsing fails
		"""

		if not isinstance(info, dict):
			return default
        
		if 'attributes' in info:
			if key in info['attributes'] and info['attributes'][key]:
				if isinstance(info['attributes'][key], type(key_type)):
					return info['attributes'][key]

		return default


	def run(self, node):
		while True:
			data = node.input.recv()
			message = json.loads(data)

			output = self.process_message(message)
			
			if output is None:
				continue

			if isinstance(output, list):
				for msg in output:
					node.output.send_json(msg)
			else:
				node.output.send_json(output)

	def process_message(self, message):
		return message  

class PluginRack(Plugin):
	def __init__(self):
		self.plugins = list()

	def run(self, node):
		while True:

			data = node.input.recv()
			message = json.loads(data)

			input_messages = deque()
			input_messages.append(message)

			output_messages = deque()

			for plugin in self.plugins:

				while len(input_messages) > 0:
					msg = input_messages.popleft()
					output = plugin.process_message(msg)

					if output is None:
						continue
					elif isinstance(output, list):
						output_messages.extend(output)
					else:
						output_messages.append(output)

				input_messages, output_messages = output_messages, input_messages

			while len(input_messages) > 0:
				node.output.send_json(input_messages.popleft())

