#!/usr/bin/env python
#encoding=utf-8

"""
WeiXin message type
"""

from lxml import etree
import logging
import traceback

MESSAGE_TYPE_TEXT = 'text'
MESSAGE_TYPE_IMAGE = 'image'
MESSAGE_TYPE_VOICE = 'voice'
MESSAGE_TYPE_VEDIO = 'vedio'
MESSAGE_TYPE_LOCATION = 'location'
MESSAGE_TYPE_LINK = 'link'
MESSAGE_TYPE_EVENT = 'event'

MESSAGE_TYPES = [
    MESSAGE_TYPE_TEXT,
    MESSAGE_TYPE_IMAGE,
    MESSAGE_TYPE_VOICE,
    MESSAGE_TYPE_VEDIO,
    MESSAGE_TYPE_LOCATION,
    MESSAGE_TYPE_LINK,
    MESSAGE_TYPE_EVENT,
]

EVENT_TYPE_SUBSCRIBE = 'subscribe'
EVENT_TYPE_UNSUBSCRIBE = 'unsubscribe'
EVENT_TYPE_SCAN = 'scan'
EVENT_TYPE_LOCATION = 'LOCATION'
EVENT_TYPE_CLICK = 'CLICK'

EVENT_TYPES = [
    EVENT_TYPE_SUBSCRIBE,
    EVENT_TYPE_UNSUBSCRIBE,
    EVENT_TYPE_SCAN,
    EVENT_TYPE_LOCATION,
    EVENT_TYPE_CLICK,
]
    
class WeiXinMessage():
    """
    WeiXin message
    user message type: text, image, voice, vedio, location, link
    event message type: event
    event type: subscribe, unsubscribe, scan, LOCATION, CLICK
    """
    def __init__(self, data = None, L = None):
        """
            Initialize message
            @param data: xml data from WeiXin server
            @param L: configurable logging
        """
        if L is not None:
            self.L = L
        else:
            self.L = logging

        if data is not None:
            self.parseMessage(data)
        else:
            self.message = {
                'toUserName' : '',
                'fromUserName' : '',
                'createTime' : 0,
                'msgType' : '',
                'msgId' : 0,
                # content is different based on msgType
                'content' : '',
                }

    def parseMessage(self, data):
        """
        Parse XML message from WeiXin server
        @param data: xml data from WeiXin server
        """
        msg = etree.fromstring(data)
        self.message = {}
        try:
            self.message['toUserName'] = msg.xpath('/xml/ToUserName')[0].text
            self.message['fromUserName'] = msg.xpath('/xml/FromUserName')[0].text
            self.message['createTime'] = int(msg.xpath('/xml/CreateTime')[0].text)
            self.message['msgType'] = msg.xpath('/xml/MsgType')[0].text
            self.message['msgId'] = msg.xpath('/xml/MsgId')[0].text
            if self.message['msgType'] in MESSAGE_TYPES:
                self._parseMessageContent(msg)
            else:
                sefl.L.error("Invalid MsgType: %s", self.message['msgType'])
        except Exception, e:
            self.L.error(traceback.format_exc())

    def _parseMessageContent(self, msg):
        """
        Parse message content based on MsgType
        @param msg: xml message
        """
        message_type = self.message['msgType']
        if MESSAGE_TYPE_EVENT == message_type:
            self.message['content'] = {}
            self._parseMessageContentEvent(msg)
        elif MESSAGE_TYPE_TEXT == message_type:
            self.message['content'] = msg.xpath('/xml/Content')[0].text
        elif MESSAGE_TYPE_IMAGE == message_type:
            self.message['content'] = {}
            self.message['content']['picUrl'] = msg.xpath('/xml/PicUrl')[0].text
            self.message['content']['mediaId'] = msg.xpath('/xml/MediaId')[0].text
        elif MESSAGE_TYPE_VOICE == message_type:
            self.message['content'] = {}
            self.message['content']['mediaId'] = msg.xpath('/xml/MediaId')[0].text
            self.message['content']['format'] = msg.xpath('/xml/Format')[0].text
        elif MESSAGE_TYPE_VEDIO == message_type:
            self.message['content'] = {}
            self.message['content']['mediaId'] = msg.xpath('/xml/MediaId')[0].text
            self.message['content']['thumbMediaId'] = msg.xpath('/xml/ThumbMediaId')[0].text
        elif MESSAGE_TYPE_LOCATION == message_type:
            self.message['content'] = {}
            self.message['content']['locationX'] = msg.xpath('/xml/Location_X')[0].text
            self.message['content']['locationY'] = msg.xpath('/xml/Location_Y')[0].text
            self.message['content']['scale'] = msg.xpath('/xml/Scale')[0].text
            self.message['content']['label'] = msg.xpath('/xml/Label')[0].text
        elif MESSAGE_TYPE_LINK == message_type:
            self.message['content'] = {}
            self.message['content']['title'] = msg.xpath('/xml/Title')[0].text
            self.message['content']['description'] = msg.xpath('/xml/Description')[0].text
            self.message['content']['url'] = msg.xpath('/xml/Url')[0].text
            self.message['content']['thumbMediaId'] = msg.xpath('/xml/ThumbMediaId')[0].text

    def _parseMessageContentEvent(self, msg):
        """
        Parse message content for msgType: event
        @param msg: xml message
        """
        event_type = msg.xpath('/xml/Event')[0].text
        self.message['content']['event'] = event_type
        if (MESSAGE_TYPE_SUBSCRIBE == event_type and msg.find('EventKey')) or MESSAGE_TYPE_SCAN == event_type:
            self.message['content']['eventKey'] = msg.xpath('/xml/EventKey')[0].text
            self.message['content']['ticket'] = msg.xpath('/xml/Ticket')[0].text
        elif MESSAGE_TYPE_LOCATION == event_type:
            self.message['content']['latitude'] = msg.xpath('/xml/Latitude')[0].text
            self.message['content']['longitude'] = msg.xpath('/xml/Longitude')[0].text
            self.message['content']['precision'] = msg.xpath('/xml/Precision')[0].text
        elif MESSAGE_TYPE_CLICK == event_type:
            self.message['content']['eventKey'] = msg.xpath('/xml/EventKey')[0].text


    def dumpMessage(self):
        """
        Dump Message, for debug
        """
        return self.message
    
    def getReplyMessage(self, reply_type = MESSAGE_TYPE_TEXT):
        if reply_type not in MESSAGE_TYPES:
            return ''
        
        reply_msg = etree.fromstring('<xml></xml>')
        if MESSAGE_TYPE_TEXT == reply_type:
            node = etree.SubElement(reply_msg, 'ToUserName')
            node.text = self.message['fromUserName']
            node = etree.SubElement(reply_msg, 'FromUserName')
            node.text = self.message['toUserName']
            node = etree.SubElement(reply_msg, 'CreateTime')
            node.text = str(self.message['createTime'] + 1)
            node = etree.SubElement(reply_msg, 'Content')
            node.text = 'reply: ' + self.message['content']
            node = etree.SubElement(reply_msg, 'MsgType')
            node.text = reply_type
            return etree.tostring(reply_msg)
            
