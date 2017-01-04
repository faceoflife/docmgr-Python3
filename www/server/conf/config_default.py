#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# default config, 开发环境的配置

configs = {
	'db': {
		'host': '127.0.0.1',
		'port': 3306,
		'user': 'root',
		'password': 'xiaowei',
		'database': 'python3_webapp'
	},
	'admin': {
		'email': 'xiaowei@126.com',
		'passwd': '123456',
		'name': 'xiaowei'
	},
	'cookie': {
		'name': 'awesession'
	},
	'session': {
		'secret': 'AwEsOmE'
	}
}