#!/usr/bin/env python
# coding=utf-8

"""
WeiXin message processor
"""

import hashlib
from .wxMessage import WeiXinMessage

class WeiXinMessageProcessor():
    def __init__(self, token):
        """
        @param token: weixin token
        """
        self.token = token

    def checkSignature(self, signature, timestamp, nonce):
        """
        @return: Chech if a request is from WeiXin server. Return true when siganature matches given arguments.
        """
        args = [self.token, timestamp, nonce]
        args.sort()
        return signature == hashlib.sha1(''.join(args)).hexdigest()

    def processMessage(self, data):
        """
        Process message
        @param data: xml data from WeiXin server POST request.
        @return: message send back to user(if any).
        """
        message = WeiXinMessage(data)
        return message.getReplyMessage('text')
        #return message.dumpMessage()

