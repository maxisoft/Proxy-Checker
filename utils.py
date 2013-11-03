import re

PROXY_REGEX = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b:\d{2,5}"


def getPublicIp(opener):
	"""original idea from http://stackoverflow.com/a/6453053"""
	data = opener.open('http://checkip.dyndns.com:8245/').read()
	return re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)


def get_all_proxy(s):
	return re.findall(PROXY_REGEX, s)