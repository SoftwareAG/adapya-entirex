#! /usr/bin/env python
# -*- coding: latin1 -*-

"""broker.py is a Python interface to Webmethods EntireX Broker

The module loads the EntireX Broker stub:

* broker.dll for 64-bit Python otherwise broker32.dll (on Windows)
* libbroker.so shared library (on Unix)

broker.py defines the Broker class using the Advanced Communication
interface (ACI) for communicating with the EntireX broker.
"""

from __future__ import print_function          # PY3

from . import acierror
# from exceptions import Exception             # PY3
from datetime import datetime
# import string PY3
import struct
import sys
import types

import ctypes
from ctypes import c_char_p

from adapya.base.defs import Abuf
from adapya.base.dump import dump
from adapya.base.datamap import Datamap, String, Bytes, Filler, Uint1, Uint4, \
    T_IN, T_OUT, T_INOUT, str_str


class BrokerException(Exception):
    """
    Instance will have set the following values:

    self.value  is the EXX Broker response string

    self.etb  is the Broker ACI call parameters that were used when
                the error occurred

    Example on how to call it::

        try:
            raise BrokerException(value,etb)
        except BrokerException as e:
            adalog.warning('BrokerException', e.value, e.__class__)
            dump(e.etb.error_buffer,log=adalog.warning)

    """

    def __init__(self, value, etb):
        if not value or value.startswith(' '):   # indicator no explanation in acierror.py
            value+='\nError-Text: %s' %(etb.errtext_buffer.value)
        self.value = value
        self.etb = etb
    def __str__(self):
        return repr(self.value)

class BrokerError(BrokerException):
    "Subclass of BrokerException for Broker Error Responses"
    pass
class BrokerTimeOut(BrokerException):
    "Subclass of BrokerException for timeouts of requests to Broker"
    pass
class InterfaceError(BrokerException):
    "Subclass of BrokerException for Broker Interface Errors"
    pass

if sys.platform.startswith('win'):
    if ctypes.sizeof(c_char_p) == 8:
        etblnk=ctypes.cdll.broker     # 64 bit broker DLL
    else:
        etblnk=ctypes.cdll.broker32   # 32 bit broker DLL
elif sys.platform != 'zos':
    # MVS load lib search order: STEPLIB, JOBLIB, LPA and Link List
    etblnk=ctypes.cdll.LoadLibrary('//BROKER2')
else:
    etblnk=ctypes.cdll.LoadLibrary('libbroker.so')

etblnk.broker.argtypes = [c_char_p,c_char_p,c_char_p,c_char_p]


# --- EntireX Broker API Type Constants (api_type) -----------------

API_TYPE1=                      1

# --- EntireX Broker API Version Constants (api_version) -----------

API_VERS1=                      1
API_VERS2=                      2
API_VERS3=                      3
API_VERS4=                      4
API_VERS5=                      5
API_VERS6=                      6
API_VERS7=                      7
API_VERS8=                      8
API_VERS9=                      9
API_VERS10=                    10
API_VERS_HIGHEST=              10   # Broker V9.9 single conv. mode


# --- EntireX Broker API API Function Constants (function) ---------

FCT_SEND =             1
FCT_RECEIVE =          2
FCT_UNDO =             4
FCT_EOC =              5
FCT_REGISTER =         6
FCT_DEREGISTER =       7
FCT_VERSION =          8
FCT_LOGON =            9
FCT_LOGOFF =          10
FCT_SET =             11
FCT_GET =             12
FCT_SYNCPOINT =       13
FCT_KERNELVERS =      14
FCT_LOCTRANS =        15  # deprecated
FCT_SETSSLPARMS =     16
FCT_SENDPUBLICATION = 17
FCT_RECVPUBLICATION = 18
FCT_SUBSCRIBE =       19
FCT_UNSUBSCRIBE =     20
FCT_CNTLPUBLICATION = 21
FCT_REPYERROR =       22

function_str = lambda i: str_str(i, {1:'SEND', 2:'RECEIVE', 4:'UNDO',
                5:'EOC', 6:'REGISTER', 7:'DEREGISTER', 8:'VERSION',
                9:'LOGON', 10:'LOGOFF', 11:'SET', 12:'GET',
                13:'SYNCPOINT', 14:'KERNELVERS', 15:'LOCTRANS',
                16:'SETSSLPARMS', 17:'SENDPUBLICATION',
                18:'RECVPUBLICATION', 19:'SUBSCRIBE', 20:'UNSUBSCRIBE',
                21:'CNTLPUBLICATION', 22:'REPLYERROR'} )

# --- EntireX Broker API Option Constants (option) -----------------

OPT_MSG =           0x01
OPT_HOLD =          0x02
OPT_IMMED =         0x03
OPT_QUIESCE =       0x04
OPT_EOC =           0x05
OPT_CANCEL =        0x06
OPT_LAST =          0x07
OPT_NEXT =          0x08
OPT_PREVIEW =       0x09
OPT_COMMIT =        0x0a
OPT_BACKOUT =       0x0b
OPT_SYNC =          0x0c
OPT_ATTACH =        0x0d
OPT_DELETE =        0x0e
OPT_EOCCANCEL =     0x0f
OPT_QUERY =         0x10
OPT_SETUSTATUS =    0x11
OPT_ANY =           0x12
OPT_TERMINATE =     0x13
OPT_DURABLE =       0x14
OPT_CHECKSERVICE =  0x15
OPT_EXTENDED =      0x16

option_str = lambda i: str_str(i, {1:'MSG', 2:'HOLD', 3:'IMMED',
        4:'QUIESCE', 5:'EOC', 6:'CANCEL', 7:'LAST', 8:'NEXT',
        9:'PREVIEW', 10:'COMMIT', 11:'BACKOUT', 12:'SYNC', 13:'ATTACH',
        14:'DELETE', 15:'EOCCANCEL', 16:'QUERY', 17:'SETUSTATUS',
        18:'ANY', 19:'TERMINATE', 20:'DURABLE', 21:'CHECKSERVICE',
        22:'EXTENDED',})

# --- EntireX Broker Conversation Status Constants (conv_stat) -----

CONVSTAT_NEW  = 1
CONVSTAT_OLD  = 2
CONVSTAT_NONE = 3

convstat_str = lambda i: str_str(i, {1:'NEW',2:'OLD',3:'None'})

# --- EntireX Broker Store Constants (store) -----------------------

STORE_OFF=                      '\x01'
STORE_BROKER=                   '\x02'

# --- EntireX Broker Status Constants (status) ---------------------

STAT_OFF=                       '\x01'
STAT_STORED=                    '\x02'
STAT_DELIVERY_ATTEMP=           '\x03'
STAT_DELIVERED=                 '\x04'
STAT_PROCESSED=                 '\x05'
STAT_DEAD=                      '\x06'

texts_STAT = ('n/a','OFF','STORED','DELIVERY_ATTEMP','DELIVERED',
         'PROCESSED','DEAD')

# --- EntireX Broker UOW Status Constants (uowStatus) --------------

RECV_NONE =    0
RECEIVED =     1
ACCEPTED =     2
DELIVERED =    3
BACKEDOUT =    4
PROCESSED =    5
CANCELLED =    6
TIMEOUT =      7
DISCARDED =    8
RECV_FIRST =   9
RECV_MIDDLE = 10
RECV_LAST =   11
RECV_ONLY =   12

uowStatus_str = lambda i: str_str(i, {0:'RECV_NONE',1:'RECEIVED',
    2:'ACCEPTED',3:'DELIVERED',4:'BACKEDOUT',5:'PROCESSED',
    6:'CANCELLED',7:'TIMEOUT',8:'DISCARDED',9:'RECV_FIRST',
    10:'RECV_MIDDLE',11:'RECV_LAST',12:'RECV_ONLY'})

# --- EntireX Broker UOW Status Persist (uowStatusPersist) ---------

UWSTATP_DEFAULT=                '\x00'   # use default from Broker
UWSTATP_NO=                     '\xff'   # status is not persistent


# --- EntireX Broker Architecture Constants (data_arch) ------------

ACODE_HIGH_ASCII_IBM=           '\x01'
ACODE_LOW__ASCII_IBM=           '\x02'
ACODE_HIGH_EBCDIC_IBM=          '\x03'
ACODE_LOW__EBCDIC_IBM=          '\x04'
ACODE_HIGH_ASCII_VAX=           '\x05'
ACODE_LOW__ASCII_VAX=           '\x06'
ACODE_HIGH_EBCDIC_VAX=          '\x07'
ACODE_LOW__EBCDIC_VAX=          '\x08'
ACODE_HIGH_ASCII_IEEE=          '\x09'
ACODE_LOW__ASCII_IEEE=          '\x0a'
ACODE_HIGH_EBCDIC_IEEE=         '\x0b'
ACODE_LOW__EBCDIC_IEEE=         '\x0c'
ACODE_HIGHEST_VALUE=            '\x0d'

# --- EntireX Broker Force Logon Constants (forceLogon) ------------

FORCE_LOGON_NO=                 'N'
FORCE_LOGON_YES=                'Y'
FORCE_LOGON_S=                  'S'

# --- EntireX Broker Encryption Level Constants (encryptionLevel) --

ENCLEVEL_NONE=                  '\x00'
ENCLEVEL_TO_BROKER=             '\x01'
ENCLEVEL_TO_TARGET=             '\x02'

# --- EntireX Broker Kernel Security Constants (kernelSecurity) ----

KERNEL_SECURITY_NO=             'N'
KERNEL_SECURITY_YES=            'Y'
KERNEL_SECURITY_USER=           'U'
KERNEL_SECURITY_LIGHT=          'L'

# --- EntireX Broker Compression Level Constants (compress) --------

COMPRESS_LEVEL_0=               '0'
COMPRESS_LEVEL_1=               '1'
COMPRESS_LEVEL_2=               '2'
COMPRESS_LEVEL_3=               '3'
COMPRESS_LEVEL_4=               '4'
COMPRESS_LEVEL_5=               '5'
COMPRESS_LEVEL_6=               '6'
COMPRESS_LEVEL_7=               '7'
COMPRESS_LEVEL_8=               '8'
COMPRESS_LEVEL_9=               '9'
COMPRESS_LEVEL_NO=              'N'
COMPRESS_LEVEL_YES=             'Y'

# --- EntireX Broker API Size of fields ----------------------------

S_ADAPTERR=                     8
S_APPLICATION_NAME=             64
S_APPLICATION_TYPE=             8
S_BROKER_ID=                    32
S_CLIENTUID=                    32
S_COMMIT_TIME=                  17
S_CONV_ID=                      16
S_ENVIRONMENT=                  32
S_ERROR_CODE=                   8
S_ERROR_CLASS=                  4
S_ERROR_NUMBER=                 4
S_LOCALE=                       40
S_MSGID=                        32
S_MSGTYPE=                      16
S_PASSWORD=                     32
S_PLATFORM=                     8
S_PRODUCT_VERSION=              16
S_PTIME=                        8
S_PUBLICATION_ID=               16
S_PUID=                         28
S_SECURITY_TOKEN=               32
S_SERVER_CLASS=                 32
S_SERVER_NAME=                  32
S_SERVICE=                      32
S_T_NAME=                       8
S_TOKEN=                        32
S_TOPIC=                        96
S_TXT=                          40
S_U_STATUS=                     32
S_UOW_ID=                       16
S_USER_ID=                      32
S_USRDATA=                      16
S_VERS=                         8
S_WAIT=                         8
S_BROKER_URL=                   512

ETB_CODEPAGE_USE_PLATFORM_DEFAULT=  "LOCAL"

# EntireX Broker control block
etbcbfields = (
    Uint1('api_type',       opt=T_IN),
    Uint1('api_version',    opt=T_IN),
    Uint1('function',       opt=T_IN),
    Uint1('option',         opt=T_IN),
    Filler('reserved1', 16),

    Uint4('send_length',    opt=T_IN),
    Uint4('receive_length', opt=T_IN),  # maximum receive length
    Uint4('return_length',  opt=T_OUT), # length of returned data
    Uint4('errtext_length', opt=T_IN),  # error text buffer len

    String('broker_id',      32, opt=T_IN),

    # service name
    String('server_class',   32),
    String('server_name',    32),
    String('service',        32),

    String('user_id',        32, opt=T_IN),
    String('password',       32, opt=T_IN),    # may contain binary data
    String('token',          32, opt=T_IN),
    Bytes('security_token',  32),
    String('conv_id',        16),              #0x124 conversational/non.
    String('wait',           8, opt=T_IN),     #blocked/non-blocked, time in sec

    String('error_code',      8, opt=T_OUT),
    String('environment',    32, opt=T_IN),    #translation parm

    # V2 following
    Uint4('adcount',             opt=T_OUT),   # attempted deliv. count
    Bytes('user_data',       16, opt=T_OUT),
    Bytes('msg_id',          32),
    String('msg_type',       16),

    String('ptime',           8, opt=T_IN),    # future use
    Bytes('newpassword',     32, opt=T_IN),
    String('adapt_err',       8, opt=T_OUT),
    String('client_uid',     32, opt=T_OUT),
    Uint1('conv_stat',           opt=T_OUT),
    Bytes('store',  1),                        # UOW is persistent
    Bytes('status',  1),                       # future use

    # V3 following
    Uint1('uowStatus'),
    String('uowTime',         8, opt=T_IN),     # lifetime of UOW (sec)
    String('uowID', 16),
    String('userStatus', 32),
    Bytes('uowStatusPersist', 1, opt=T_IN),    # persist flag
    Filler('reserved2', 3),

    # V4 following
    String('locale_string',  40, opt=T_IN),    # callers set_locale
    Bytes('data_arch',        1, opt=T_IN),    # architecture

    # V6 following
    String('forceLogon',      1, opt=T_IN),
    Bytes('encryptionLevel',  1),

    # V7 following
    String('kernelsecurity', 1),
    String('commitTime',     17, opt=T_OUT),
    String('compress',        1, opt=T_IN),
    # Filler('reserved3', 114),                # size=744 ACI V6/V7

    # V8 following (=Broker V7.2)
    Filler('reserved4', 6),                    # align
    String('uowStatusTime', 8),                # UOW status life time
    String('topic', 96),                       #
    String('publicationID', 16),               # size = 756 ACI V8

    # V9 following (=Broker V8.1)
    Filler('reserved5', 32),                   # was bid (partner broker id)
    Filler('reserved6', 12),                   # align
    Uint4('clientId',  opt=T_OUT),             # unique client id set on RECV/SEND w. WAIT
    Filler('reserved7', 32),                   # align
    String('logCommand', 1),                   #
    String('credentialsType', 1),              # default: userid/passw, '1'=IAF auth.
    Filler('reserved8', 34),                   # size=872 V9

    # V10 following (=Broker V9.7)
    Uint4('varlist_offset'),                   #
    Uint4('long_broker_id_length'),            # size = 880 / 0x350 LETBCB10
    )

LETBCB9 =  872
LETBCB10 = 880


def pptime(timestring):
    if timestring.strip() and timestring.strip('\x00') : # string not blank or zero
        return "%04s-%02s-%02s %02s:%02s:%02s.%03s UTC+0" % (timestring[0:4], timestring[4:6], timestring[6:8],
            timestring[8:10],timestring[10:12],timestring[12:14], timestring[14:])
    else:
        return ''

class Etbcb(Datamap):
    "Defines Broker control block with its attributes and Broker call()"
    def __init__(self, send_length=0, receive_length=0,
                 use_api_version=API_VERS7,**kw):

        self.__dict__['errtext_buffer'] = Abuf(80)
        self.__dict__['send_buffer'] = None
        self.__dict__['receive_buffer'] = None
        self.__dict__['trace'] = None
        self.__dict__['use_api_version'] = use_api_version

        Datamap.__init__(self, 'Etbcb', *etbcbfields, **kw)

        self.buffer=Abuf(self.dmlen)
        self.errtext_length=80
        self.api_type=API_TYPE1
        self.api_version=use_api_version

        if receive_length > 0:
            self.receive_buffer=Abuf(receive_length)
            self.receive_length=receive_length
        if send_length > 0:
            self.send_buffer=Abuf(send_length)
            self.send_length=send_length

    def call(self):
        if self.trace&1:
            print('Before Broker call')
            dump(self.buffer, header='ETBCB')
            dump(self.receive_buffer, header='Receive Buffer')
            # print(repr(self.send_buffer), len(self.send_buffer), self.send_length)
            dump(self.send_buffer, header='Send Buffer')
            dump(self.errtext_buffer, header='Error Text Buffer')
            # self.error_code=''

        if self.trace&4:
            print('\n%s == EXX %s%s%s%s' % ( datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                function_str( self.function),
                ' option='+option_str(self.option) if self.option else '',
                ' wait='+self.wait.strip('\x00 ')
                    if self.function==FCT_RECEIVE and self.wait > 8*' ' else '',
                ' user=%s token=%s Service=%s/%s/%s'%(self.user_id,self.token,
                        self.server_class,self.server_name,self.service)
                    if self.function==FCT_LOGON else ''
                ))
            if 0: # self.function==FCT_SEND:
                print(repr(self.send_buffer), len(self.send_buffer), self.send_length)
                dump(self.send_buffer[0:self.send_length],
                    header='    send_buffer',prefix='   ')

        i = etblnk.broker(self.buffer, self.send_buffer, self.receive_buffer,
              self.errtext_buffer )

        if self.trace&2:
            print('After Broker call')
            dump(self.buffer, header='ETBCB')
            # dump(self.receive_buffer, header='Receive Buffer')
            if self.return_length>0:
                dump(self.receive_buffer[0:self.return_length],
                    header='    receive_buffer', prefix='   ')
            # print(repr(self.send_buffer), len(self.send_buffer), self.send_length)
            dump(self.send_buffer, header='Send Buffer')
            dump(self.errtext_buffer, header='Error Text Buffer')
        if self.trace&4:
            print('    conv_id=%-16s  conv_stat=%s  return_length=%d' %(
                self.conv_id.strip('\x00 '),
                convstat_str(self.conv_stat),
                self.return_length))
            print('      uowID=%-16s  uowStatus=%-9s  commitTime=%s' % (
                self.uowID.strip('\x00 '),
                uowStatus_str(self.uowStatus),
                pptime(self.commitTime)))

        if self.error_code > '00000000':
            if self.error_code in (
                    '00740074',   # Wait timeout
                    '02150373'):  # Transport timeout (new with single conv?)
                raise BrokerTimeOut( acierror.geterror(self.error_code), self)
            raise BrokerError(acierror.geterror(self.error_code),self)

        if i != 0:
            raise InterfaceError(acierror.geterror('0020%04d' %i), self)


class Broker(Etbcb):
    """Defines the essential Broker ACI functions using the Etbcb.
       For reference see EntireX Broker ACI Programming.
    """

    def __init__(self, broker_id='localhost', user_id='monty', token=None,
                 receive_length=2048, send_length=2048):
        Etbcb.__init__(self, receive_length=receive_length, send_length=send_length)

        self.broker_id=broker_id
        self.user_id=user_id
        if token != None:
            self.token=token

    def backout(self):
        "Backout UOW but continue conversation"
        self.function=FCT_SYNCPOINT
        self.option=OPT_BACKOUT
        self.call()
        self.uowID=''   # reset some fields after commit
        self.uowStatus=RECV_NONE

    def commit(self):
        "Commit UOW but continue conversation"
        self.function=FCT_SYNCPOINT
        self.option=OPT_COMMIT
        self.call()
        self.uowID=''   # reset some fields after commit
        self.uowStatus=RECV_NONE

    def commitEndConversation(self):
        "Commit UOW and end conversation"
        self.function=FCT_SYNCPOINT
        self.option=OPT_EOC
        self.call()
        self.conv_id=''           # reset some fields after commit
        self.uowID=''
        self.uowStatus=RECV_NONE

    def kernelVersion(self):
        "Determine Broker kernel version"
        self.function=FCT_KERNELVERS
        self.option = OPT_EXTENDED
        self.call()

        print('\nMAX-MSG is %d' % self.return_length)
        # maxmsg is returned with the OPT_EXTENDED option
        # obviously works with use_api_version V4
        # unrelated to single conversation mode

        if self.api_version > self.use_api_version:
            self.api_version=self.use_api_version

        # return self.errtext_buffer[:].strip(b'\x00 ') # remove blanks and x00
        return self.errtext_buffer.buf2str() # remove blanks and x00

    def deregister(self):
        "A server can deregister a service from EntireX Broker"
        self.function=FCT_DEREGISTER
        self.option=OPT_QUIESCE
        self.call()

    def endConversation(self, option=0):
        """A client or server can terminate one or more conversations.
           This is the EOC function in ACI terms
        """
        self.function=FCT_EOC
        self.option=option    # set to CANCEL to abort conversation
        self.call()

    def logon(self, password=None, newpassword=None):
        "Establish communication with a Broker kernel"
        self.function=FCT_LOGON
        if password:
            self.password=password
        self.option=0
        self.call()

    def logoff(self):
        "Terminate communication with Broker kernel"
        self.function=FCT_LOGOFF
        self.option=OPT_HOLD
        self.call()

    def receive(self, conv_id='', option=0, wait=''):
        """Used by clients to receive incoming messages and by servers
           to receive incoming requests
        """
        self.function=FCT_RECEIVE
        if conv_id!='':
            self.conv_id=conv_id
        if option!=0:
            self.option=option
        if wait!='':
            self.wait=wait
        self.call()

    def receiveNew(self, wait=''):
        """Receive any message from new conversation"""
        self.function=FCT_RECEIVE
        self.conv_id='NEW'
        self.option=OPT_ANY
        if wait!='':
            self.wait=wait
        self.call()

    def register(self, option=0):
        """Used by servers to inform EntireX Broker that a
           service is available
        """
        self.function=FCT_REGISTER
        self.option = option    # only valid option: ATTACH
        self.call()

    def send(self, conv_id='', option=0):
        """Used by clients to send requests and servers to send replies"""
        self.function=FCT_SEND
        if conv_id!='':
            self.conv_id=conv_id
        if option!=0:
            self.option=option
        self.call()
        if self.option == OPT_COMMIT:
            # self.conv_id=''          # keep conv_id
            self.uowID=''              # reset uow fields
            self.uowStatus=RECV_NONE
        elif self.option == OPT_EOC:
            self.conv_id=''            # reset conv/uow fields
            self.uowID=''
            self.uowStatus=RECV_NONE

    def syncpoint(self,option=0):
        """ Function allows to manage Units of Work (UOWs)"""
        self.function=FCT_SYNCPOINT
        if option!=0:
            self.option=option
        self.call()
        if self.option == OPT_COMMIT:  # reset conv/uow fields
            # self.conv_id=''          # leave conversation open
            self.uowID=''
            self.uowStatus=RECV_NONE

    def undo(self):
        """Remove messages that have been sent out but not received"""
        self.function=FCT_UNDO
        self.call()

    def version(self):
        """return the version of the EntireX Broker Stub"""
        self.function=FCT_VERSION
        self.call()
        if self.api_version > self.use_api_version:
            self.api_version=self.use_api_version
        if self.return_length > 0:
            return self.receive_buffer.buf2str()[0:self.return_length-1]
        else:
            return ''


class ParmsBrokerService:
    "Defines parameters for a Broker service"

    def __init__(self,broker_id='',user_id='',\
                 server_class='',server_name='',service=''):
        self.broker_id=broker_id
        self.user_id=user_id
        self.server_class=server_class
        self.server_name=server_name
        self.service=service


__version__ = '1.0.1'
if __version__ == '1.0.1':
    _svndate='$Date: 2018-06-19 18:08:34 +0200 (Tue, 19 Jun 2018) $'
    _svnrev='$Rev: 839 $'
    __version__ = 'Dev ' +  _svnrev.strip('$') + \
                  ' '.join(_svndate.strip('$').split()[0:3])

#  Copyright 2004-2019 Software AG
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
