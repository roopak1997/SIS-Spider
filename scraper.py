from flask import Flask, redirect, render_template, request, session, url_for,jsonify
import json
import subprocess
import os
import sys
import scrapy
import json
import scrapy
import scrapy.crawler as crawler
from multiprocessing import Process, Queue
from twisted.internet import reactor
import base64
import random
import string


class SIS_Spider(scrapy.Spider):
	name = 'sis'
	login_url = 'http://parents.msrit.edu/index.php'
	base_url = 'http://parents.msrit.edu/'
	start_urls = [login_url]
	att_data = list()
	mark_data = list()
	write_file = ''	
	
	def parse(self, response):
		usn = USN
		token = response.xpath('//input[@value="1"]/@name')[0].extract()
		password = ''
		for c in DOB:
			password = password + c + ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase+ string.digits) for _ in range(2))

		password = base64.b64encode(password.encode()).decode("utf-8")

		data = {
		'username': usn,
		'password': password,
		'remember': 'No',
		'submit.x': '15',
		'submit.y': '23',
		'passwd':password,
		'option': 'com_user',
		'task':'login',
		'return':'�w^Ƙi',
		token : '1'
		}
        
		self.write_file = data['username']+'.json'
	
		yield scrapy.FormRequest(url=self.login_url, formdata=data, callback=self.parse_quotes)

	def parse_quotes(self, response):

		print('logged in ')
		eachsubject = list()

		details  = response.xpath('//div[@class="tname2"]/text()').extract()
	
		json.dump(details,open('data_'+self.write_file,'w'))
		eachsubject2 = response.css('a[title=Attendence]::attr(href)').extract()
		
		eachsubject = [x for x in set(eachsubject2)]
		print('attendance links are   - ', len(eachsubject))
		
		for link in eachsubject:
			request = scrapy.Request(url = self.base_url+link, callback = self.attendance_data)
			
			yield request

		eachsubject2 = response.xpath('//div[@class="cie"]/a/@href').extract()
		
		eachsubject = [x for x in set(eachsubject2)]
		print('cie links are   - ', len(eachsubject))
		
		for link in eachsubject:	
			request = scrapy.Request(url = self.base_url+link, callback = self.marks_data)
			yield request

	def attendance_data(self, response):
		att = dict()
		att['code'] = response.xpath('//div[@class="courseCode"]/text()')[0].extract()
		att['name'] = response.xpath('//div[@class="coursename"]/text()')[0].extract()
		att['percentage'] = response.xpath('//div[@class="att"]/a/text()')[0].extract()
		att['teacher'] = response.xpath('//div[@class="tname"]/text()')[0].extract()
		#print(' p = ',att['teacher'])
		att['present'] = response.xpath('//div[@class="progress-bar progress-bar-success"]/@title')[0].extract().split(':')[1]
		att['absent'] = response.xpath('//div[@class="progress-bar progress-bar-danger"]/@title')[0].extract().split(':')[1]

		try:
			att['remaining'] = response.xpath('//div[@class="progress-bar progress-bar-warning"]/@title')[0].extract().split(':')[1]
		except:
			att['remaining'] = '0'

		even = response.xpath('//tr[@class="even"]/td/text()').extract()
		odd = response.xpath('//tr[@class="odd"]/td/text()').extract()

		
		present = list()
		absent = list()

		for e in range(0,len(even),4):
			day = dict()
			# or try this future
			day['index'] = ' '.join(even[e].split())
			day['date'] = ' '.join(even[e+1].split())
			day['time'] = ' '.join(even[e+2].split())
			day['status'] = ' '.join(even[e+3].split())
			
			if(day['status'] == 'Present'):
				present.append(day)
			else:	
				absent.append(day)
			
		for e in range(0,len(odd),4):
			day = dict()
			day['index'] = ' '.join(odd[e].split())
			day['date'] = ' '.join(odd[e+1].split())
			day['time'] = ' '.join(odd[e+2].split())
			day['status'] = ' '.join(odd[e+3].split())
			
			if(day['status'] == 'Present'):
				present.append(day)
			else:	
				absent.append(day)
	
		absent = sorted(absent, key=lambda x:x['index'])
		present = sorted(present, key=lambda x:x['index'])	
		
		att['present_dates'] = present
		att['absent_dates'] = absent
	
		self.att_data.append(att)
		
		json.dump(self.att_data,open('attendance_'+self.write_file,'w'))
	

	def marks_data(self,response):
		marks = dict()

		marks['name'] = response.xpath('//th[@colspan="9"]/text()')[0].extract()
		lol=response.xpath('//tr[@class="odd"]/td[@class=""]/text()').extract()
		
		marks['t1'] = lol[0]
		marks['t2'] = lol[1]		
		marks['t3'] = lol[2]
		marks['t4'] = lol[3]
		marks['a1'] = lol[4]
		marks['a2'] = lol[5]
		marks['a3'] = lol[6]

		if(len(marks)==8):
			marks['final cie'] = "-"
		else:
			marks['final cie'] = lol[7]

		
		self.mark_data.append(marks)

		json.dump(self.mark_data,open('marks_'+self.write_file,'w'))

