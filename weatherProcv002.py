#!/usr/bin/env python2.7

import socket
import sys
import datetime
import sqlite3
import os.path
import feedparser
import time

appLog = "comms.log"
stopFile = "stop.me"
urlObservations = "http://open.live.bbc.co.uk/weather/feeds/en/2634021/observations.rss"
weatherReported = 0

def stripValue(newValue):
  newValue = newValue.split(":")
  newValue = newValue[1].strip()
  
  return newValue

def getForecast():
  feed = feedparser.parse( urlObservations )

  #if feed.version == "rss20":
  conn = sqlite3.connect('trilby.db')
  c = conn.cursor()
  
  for post in feed.entries:
    
    published = post.published
    published = published.encode('utf-8')
    
    title = post.title
    title = title.encode('utf-8')
    t = title.split(":")
    t = t[2].split(",")
    weather = t[0].strip()
    
    summary = post.summary
    summary = summary.encode('utf-8')
    t = summary.split(",")
    temp = stripValue(t[0])
    wind = stripValue(t[1])
    speed = stripValue(t[2])
    humidity = stripValue(t[3])
    pressure = stripValue(t[4])
    pressureVariance = str(t[5])
    visibility = stripValue(t[6])

    sql = "DELETE FROM weather where published = '" + str(published) + "'"
    c.execute(sql)

    sql = str("INSERT INTO weather VALUES ('" + published + "', '" + weather + "', '" + temp  + "', '" + wind + "', '" + speed + "', '" + humidity + "', '" + pressure + "', '" + pressureVariance + "', '" + visibility + "')")
    print sql
    c.execute(sql)
      
  conn.commit()
  conn.close()
  
def insertMessage(today, remoteHost, recvMessage):
  # Insert into database
  conn = sqlite3.connect('trilby.db')
  c = conn.cursor()
  
  sql = str("INSERT INTO messages VALUES ('" + today + "','" + remoteHost + "','" + recvMessage + "')")
  c.execute(sql)

  t = recvMessage.split(".")
  
  sql = "DELETE FROM states where param = '" + str(t[0]) + "'"
  c.execute(sql)

  sql = "INSERT INTO states VALUES ('" + str(t[0]) + "', '" + str(t[1]) + "', '" + today + "')"
  c.execute(sql)
  
  conn.commit()
  conn.close()

def writeCommsLog(today, remoteHost, recvMessage):
  # write to comms log
  logFile = open(appLog, 'a')
  logFile.write(today + "," + remoteHost + "," + recvMessage + "\n")
  logFile.close()

def getLogDate():
  return '{:%d-%m-%y %H:%M:%S}'.format(datetime.datetime.now())

class host(object):
  hostname = ""
  message = ""
  
  def __init__(self, newHost):
    self.hostname = newHost

  def hostname():
    return self.hostname

  def message(newMessage):
    self.message = newMessage

  def message():
    return self.message

def main():
  
  print "Tribly weather server."

  conn = sqlite3.connect('trilby.db')
  c = conn.cursor()
  c.execute('CREATE TABLE IF NOT EXISTS messages ( date text, host text, message text);')
  c.execute('CREATE TABLE IF NOT EXISTS states ( param text, paramValue text, updated date );')
  c.execute('CREATE TABLE IF NOT EXISTS weather ( published text, weather text, temp text, wind text, speed text, humidity text, pressure text, pressureVariance text, visibility text);')

  # Save (commit) the changes
  conn.commit()

  getForecast()
  
  weatherReported = 0
  
  while True:
    
    if time.strftime("%M") in ["00", "15", "30", "45"] and weatherReported == 0:
      weatherReported = 1
      print time.strftime("%M")
      getForecast()

    if not (time.strftime("%M") in ["00", "15", "30", "45"]) and weatherReported == 1:
      print "E" + time.strftime("%M")
      weatherReported = 0
    
    if os.path.isfile(stopFile):
      print "process stopped by 'stop.me' file"
      quit()

if __name__ == "__main__": main()

