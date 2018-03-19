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
import scraper as sc


application = Flask(__name__)

# Secret key for sessions
application.secret_key = "mysecret"

USN = ""
DOB = ""


def run_spider():
    def f(q):
        try:
            runner = crawler.CrawlerRunner()
            deferred = runner.crawl(sc.SIS_Spider())

            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            q.put(None)
        except Exception as e:
            q.put(e)

    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result





@application.route("/getsisdata/<usn>/<dob>", methods=["GET", "POST"])
def getsisdata(usn,dob):
	global USN 
	global DOB
	
	USN = usn
	DOB = dob
	print(' usn recieved is - ' , USN);
	print(' dob recieved is - ' , DOB);
	run_spider()

	sis_data = dict()
	
	data = json.load(open('data_'+USN+'.json'))

	sis_data['attendance'] = json.load(open('attendance_'+USN+'.json'))
	sis_data['marks'] = json.load(open('marks_'+USN+'.json'))
	sis_data['name']=' '.join(data[0].split())	
	sis_data['sem']=' '.join(data[2].split())
	sis_data['earned']=' '.join(data[3].split())
	sis_data['to_earn']=' '.join(data[4].split())

	subject_list = list()
	for i in sis_data['attendance']:
		subject_list.append(i['name'])
	
	sis_data['subject_list'] = subject_list

	json.dump(sis_data,open('sis_'+USN+'.json','w'))

	with open("usage.txt", "a") as myfile:
		myfile.write(USN+"\n")

	os.remove('attendance_'+USN+'.json')
	os.remove('marks_'+USN+'.json')
	os.remove('data_'+USN+'.json')
	
	return jsonify(sis_data)
				
if __name__ == '__main__':
	application.run()

