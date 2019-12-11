#! /usr/bin/env python
# -*- coding: latin1 -*-
"""etbcinf8.py contains selected Command Info Services classes Info_*
   For Broker versions < V10 they should be imported from this module.

"""

from time import localtime, strftime
from adapya.base.defs import Abuf
from adapya.base.datamap import Datamap, String, Bytes, Filler, Uint1, \
    Uint2, Uint4, Uint8, T_HEX, T_IN, T_OUT, T_INOUT, T_NONE, str_str
from adapya.base.dtconv import intervalstr
from adapya.entirex.broker import option_str, uowStatus_str

# --- EntireX Broker Information Structure BROKER ------------------------

pstore_str = lambda i: str_str(i, { 0:'No', 1:'Hot', 2:'Cold', 4:'Warm'})

# pack class server service into one string 'class/server/service'
service_str = lambda svc:'%s/%s/%s' % (self.server_class,self.server,svc)

class Info_broker(Datamap):
    def __init__(self, **kw):
        fields=(                            # Available with CIS Interface version
        String('platform',8),
        Uint4('runtime',ppfunc=intervalstr),  #stckintervalstr if stck seconds
        Uint4('num_worker_act'),
        Uint4('num_long'),
        Uint4('long_act'),
        Uint4('long_high'),
        Uint4('num_short'),
        Uint4('short_act'),
        Uint4('short_high'),
        Uint4('long_size'),
        Uint4('short_size'),
        Uint4('num_service'),
        Uint4('service_act'),
        Uint4('num_server'),
        Uint4('server_act'),
        Uint4('server_high'),
        Uint4('num_client'),
        Uint4('client_act'),
        Uint4('client_high'),
        Uint4('num_conv'),
        Uint4('conv_high'),
        Uint2('trace_level'),
        Uint2('unused1',opt=T_NONE),            # 1

        Uint4('maxuows'),
        Uint4('maxuowmsg'),
        Uint4('uwtime',ppfunc=intervalstr),
        Uint4('maxdelcnt'),
        Uint4('maxmsgsize'),
        Uint4('totaluows'),
        Uint1('store'),
        Uint1('pstore',ppfunc=pstore_str),
        Uint1('uwstatp'),
        Uint1('deferred'),                  # 2

        String('accounting', 3),            # 3
        Uint1('authdefault'),
        Uint4('sslport'),
        Uint1('new_uow_msgs'),
        Uint1('snmp_licensed'),
        Uint2('unused2',opt=T_NONE),
        String('platformname',32),
        String('pstoretype',8),             # 3

        Uint1('pub_sub'),                   # 4
        Uint1('apiversion'),
        Uint1('cisversion'),
        Uint1('pstore_connected'),
        Uint4('num_topic'),
        Uint4('topic_act'),
        Uint4('num_subscriber'),
        Uint4('subscriber_act'),
        Uint4('subscriber_high'),
        Uint4('num_publisher'),
        Uint4('publisher_act'),
        Uint4('publisher_high'),
        Uint4('num_publication'),
        Uint4('publication_high'),
        Uint4('attach_mgrs_act'),
        Uint4('uwstat_add_time'),
        String('product_version',16),       # 4

        String('license_expiration',10),    # 5
        Uint1('security_type'),
        Uint1('accounting_enabled'),
        Uint4('num_free_ccb'),
        Uint4('num_free_pcb'),
        Uint4('num_free_pcb_ext'),
        Uint4('num_free_scb'),
        Uint4('num_free_scb_ext'),
        Uint4('num_free_subscb'),
        Uint4('num_free_tcb'),
        Uint4('num_free_tcb_ext'),
        Uint4('num_free_toq'),
        Uint4('num_free_uwcb'),
        Uint4('num_com_buffer'),
        Uint4('num_com_slot'),
        Uint4('num_com_slot_free'),
        Uint4('num_cmdlog_filter'),
        Uint4('num_cmdlog_filter_act'),
        Uint1('cmdlog'),
        Uint1('cmdlog_enabled'),
        String('unused3',2,opt=T_NONE),
        String('attribute_file_name',256),
        String('log_file_name',256),
        Uint4('log_file_size'),
        String('license_file_name',256),
        Uint4('cmdlog_size_max'),
        String('cmdlog_open_name',256),
        Uint4('cmdlog_open_size'),
        String('cmdlog_closed_name',256),
        Uint4('cmdlog_closed_size'),
        Uint4('unused4',opt=T_NONE),
        String('accounting_file_name',256),
        Uint4('accounting_file_size'),
        Uint4('control_interval'),
        Uint4('max_takeover_attempts'),
        String('run_mode',16),
        String('partner_cluster_addr',32),
        Uint4('num_cmdlog_switch_siz'),
        Uint4('num_cmdlog_switch_cis'),         # 5/6

        Uint4('client_nonact',ppfunc=intervalstr),
        Uint4('work_queue_entries'),
        Uint4('total_storage_alloc'),
        Uint4('total_storage_high'),
        Uint4('total_storage_limit'),
        String('broker_id',32),
        String('host_name',256),
        String('sysplex_name',8),
        Uint1('auto_logon'),
        Uint1('dyn_memory_management'),
        Uint1('dyn_worker_management'),
        Uint1('service_updates'),
        Uint1('topic_updates'),
        Uint1('transport_net'),
        Uint1('transport_ssl'),
        Uint1('transport_tcp'),
        Uint4('trap_error'),                    # 7/8
        )
        Datamap.__init__(self, 'Broker', *fields, **kw)


# --- EntireX Broker Information Structure CONVERSATION ---------------

class Info_conversation(Datamap):
    def __init__(self, **kw):
        fields=(                            # Available with CIS Interface version
        String('conv_id', 16),              # 1 Conversation ID

        String('serveruid', 32),            #   Server's UserID
        Bytes('serverpuid', 28),            #   Server's physical UserID
        String('serverpuidtrans',28,opt=T_NONE), # Server's translated PUID (unused)
        String('servertoken', 32),          #   Server's Token

        String('clientuid', 32),            #   Client's UserID
        Bytes('clientpuid', 28),            #   Client's physical UserID
        String('clientpuidtrans',28,opt=T_NONE), # Client's translated PUID
        String('clienttoken', 32),          #   Client's Token

        String('server_class', 32,opt=T_NONE),# SERVER-CLASS
        String('server', 32,opt=T_NONE),    #   SERVER-NAME
        String('service',32,
            ppfunc=lambda svc:'%s/%s/%s' % (self.server_class,self.server,svc)),
                                            # SERVICE = class/server/service

        Uint4('conv_nonact',ppfunc=intervalstr), #   Conversation timeout
        Uint4('last_active',ppfunc=intervalstr), #   Seconds since last activity
        Uint2('type'),                      # 1 Conversation type 0: conv, 1: non-conv
        Uint2('unused1',opt=T_NONE),        # 2 Alignment
        Uint4('totaluows'),                 # 2 Number of active UOWs
        String('client_rpc_libname', 128),  # 6 Client's
        String('client_rpc_progname',128),  # 6
        String('server_rpc_libname', 128),  # 6 Server's
        String('server_rpc_progname',128),  # 6
        )
        Datamap.__init__(self, 'Conversation', *fields, **kw)


# --- EntireX Broker Information Structure CLIENT SERVER (CS) ---------------

waiting_str =   lambda i: str_str(i, {0:'Not waiting',5:'Waiting'})
localtime_str = lambda t: strftime("%Y-%m-%d %H:%M:%S",localtime(t))


class Info_clientserver(Datamap):
    def __init__(self,  clientserver, **kw):
        fields=(                            # Available with CIS Interface version
        String('uid', 32),                  # 1 UserID
        #Bytes('puid', 28),                  #   Physical UserID
        String('puid', 28),                 #   Physical UserID
        String('puidTrans',28,opt=T_NONE),  #   Translated physical UserID
        String('token', 32),                #   User's Token
        Uint2('charset'),                   #   User's character set: *****
                                            #     EBCDIC_IBM .....  34 ('22')
                                            #     EBCDIC_SNI .....  66 ('42')
                                            #     ASCII_PC_386 ...   1 ('01')
                                            #     ASCII_PC_OS2 ...  16 ('10')
                                            #     ASCII_8859_1 ... 128 ('80')
        Uint2('highorderfirst'),            #   Big Endian = 1
        Uint2('status',ppfunc=waiting_str), #   User's status: 0: not waiting, 5: waiting
        Uint2('unused1',opt=T_NONE),        #   Alignment
        String('waitconvid', 16),           #   CONVID user is waiting for:
                                            #     "NEW"|"OLD"|"ANY"|"NONE"|n
        String('server_class', 32,opt=T_NONE),# User waiting for this ....
        String('server', 32,opt=T_NONE),    #
        String('service',32,
            ppfunc=lambda svc:'%s/%s/%s' % (self.server_class,self.server,svc)),
                                            # SERVICE = class/server/service

        Uint4('conv_act'),                  #   Active conversations of this user
        Uint4('service_act'),               #   Active services by server
        Uint4('last_active',ppfunc=intervalstr),#   Seconds since last activity
        Uint4('nonact',ppfunc=intervalstr), #   Nonactivity timeout
        Uint4('waited_new',ppfunc=intervalstr), #   Accum.wait time CONVID=NEW
        Uint4('waits_new'),                 #   Number of waits CONVID=NEW
        Uint4('waited_old',ppfunc=intervalstr), #   Accum.wait time CONVID!=NEW
        Uint4('waits_old'),                 #   Number of waits CONVID!=NEW
        Uint4('convs'),                     # 1 No. of conversations
        Uint4('active_uow'),                # 2 Total number of active UOWs
        String('ipv4_address',16),          # 4 IPv4 address client/server
        String('host_name',256),            #   Host name client/server
        Uint1('recv_option',ppfunc=option_str), #   RECEIVE option
        Uint1('attach_mgr'),                #   Attach manager
        Uint2('unused2',opt=T_NONE),        # 4 Alignment
        String('reserved_etbinfo_v73_1',32,opt=T_NONE),# 5 Reserved for future use
        String('app_name',64),              # 5
        String('app_type',8),               # 5
        String('reserved_etbinfo_v73_3',32,opt=T_NONE),# 5 Reserved for future use
        Uint4('authsucc'),                  # 5 Counter AUTHORIZ succeeded
        Uint4('authfail'),                  # 5 Counter AUTHORIZ failed
        Uint4('created',ppfunc=localtime_str),    # 5 Creation time
        String('rpclib',128),               # 6 ACI RPCLIB
        String('rpcpgm',128),               # 6 ACI RPCPGM
        Uint4('seqno'),                     # 7 unique client/server sequence number
        String('app_version',16),           # 7
        String('ipv6_address',46),          # 8 IPv6 address client/server
        String('unused',2,opt=T_NONE),      # 8 Alignment
        )
        Datamap.__init__(self, clientserver, *fields, **kw)

class Info_client(Info_clientserver):
    def __init__(self, **kw):
        super(Info_client,self).__init__('Client', **kw)

class Info_server(Info_clientserver):
    def __init__(self, **kw):
        super(Info_server,self).__init__('Server', **kw)


# --- EntireX Broker Information Structure PERSISTENT STORE ---------------

class Info_psf(Datamap):
    def __init__(self, **kw):
        fields=(                            # Available with CIS Interface version
        String('uow_id', 16),               # 2 UOW ID
        String('conv_id', 16),              #   Conversation ID
        String('senderuid',32),             #   Sender UserID
        String('sendertoken',32),           #   Sender User Token
        String('senderserver',32),          #   Sender SERVER-NAME
        String('senderclass',32),           #   Sender SERVER-CLASS
        String('senderservice',32),         #   Sender SERVICE
        String('recvruid',32),              #   Receiver UserID
        String('recvrtoken',32),            #   Receiver User Token
        String('recvrserver',32),           #   Receiver SERVER-NAME
        String('recvrclass',32),            #   Receiver SERVER-CLASS
        String('recvrservice',32),          #   Receiver SERVICE
        String('userstatus',32),            #   User status
        Uint1('uowstatus',ppfunc=lambda x:'%-9s'%uowStatus_str(x)), #   Unit of work status
        Uint1('eoc'),                       #   End of conversation? 0|1
        Uint1('store'),                     #   Persistent? 0|1
        Uint1('uowstatstore'),              #   Persistent UOW status? 0|1
        Uint4('eocreason'),                 #   EOC reason code
        Uint4('deliveries'),                #   Attempt to delivery count
        Uint4('msgcnt'),                    #   Number of messages
        Uint4('msgsize'),                   #   Total message size
        String('uwstatus_lifetime',32),     #   Status life time
        String('uwcreate_time',32),         #   Unit of work creation time
        Uint4('uw_lifetime',ppfunc=intervalstr),# 2 Unit of work life time
        )
        Datamap.__init__(self, 'PersistentMessage', *fields, **kw)


# --- EntireX Broker Information Structure SERVICE -------------------

class Info_service(Datamap):
    def __init__(self, **kw):
        fields=(                            # Available with CIS Interface version
                                            # 1
        String('server_class', 32,opt=T_NONE),# SERVER-CLASS
        String('server', 32,opt=T_NONE),    #   SERVER-NAME
        String('service',32,
            ppfunc=lambda x:'%s/%s/%s' % (self.server_class,self.server,self.service)),
                                            # SERVICE = class/server/service

        String('translate', 8),             #    Name of translation routine
        Uint4('conv_nonact',ppfunc=intervalstr),#    Conversation timeout
        Uint4('servers_act'),               #    Active servers
        Uint4('conv_act'),                  #    Active conversations
        Uint4('conv_high'),                 #    High watermark
        Uint4('longbuffer_act'),            #    Active LONG-BUFFER entries
        Uint4('longbuffer_high'),           #    High watermark
        Uint4('shortbuffer_act'),           #    Active SHORT-BUFFER entries
        Uint4('shortbuffer_high'),          #    High watermark
        Uint4('waitserver'),                #    No. waits for server MSGs
        Uint4('server_occupied'),           #    No. times all servers busy
        Uint4('pending'),                   #    No. pending conversations
        Uint4('pending_high'),              #    High watermark
        Uint4('total_requests'),            # 1  Total number of requests
        Uint4('maxuows'),                   # 2  Max # of active UOWs
        Uint4('maxuowmsg'),                 #    Max # of messages per UOW
        Uint4('uwtime',ppfunc=intervalstr), #    Max UOW life time
        Uint4('maxdelcnt'),                 #    Max delivery count
        Uint4('maxmsgsize'),                #    Max message size
        Uint4('totaluows'),                 #    Total number of active UOWs
        Uint1('store'),                     #    Startup value STORE: 0: off, 1: Broker
        Uint1('uwstatp'),                   #    uowStatusLifetime Multiplier
        Uint1('deferred'),                  # 2  default status for UOW  0: no, 1: yes
        Uint1('enclevel'),                  # 3  Encryption Level
        Uint4('attachmgrs_act'),            # 4  No. active attach managers
        Uint4('uwstat_addtime'),            # 4  UWSTAT-LIFETIME
        Uint4('num_conv'),                  # 5  No. conversations
        Uint4('num_server'),                #    No. servers
        Uint4('longbuffers'),               #    No. long message buffers
        Uint4('shortbuffers'),              #    No. short message buffers
        String('conversion',8),             #    Name of conversion routine
        String('conversion_parms',255),     #    Conversion parameters
        String('unused1', 5, opt=T_NONE),   # 5 alignment
        )
        Datamap.__init__(self, 'Service', *fields, **kw)


# --- EntireX Broker Information Structure UOW STATISTICS ---------------

class Info_UOW_statistics(Datamap):
    def __init__(self, **kw):
        fields=(                            # Available with CIS Interface version EXX 9/10
        String('server_class', 32,opt=T_NONE),# SERVER-CLASS
        String('server', 32,opt=T_NONE),    #  SERVER-NAME
        String('service',32,
            ppfunc=lambda svc:'%s/%s/%s' % (self.server_class,self.server,svc)),
                                            # SERVICE = class/server/service
        Uint8('uows'),                      # Number of active UOWs (active==current)
        Uint8('messages'),                  # Number of active UOW messages
        Uint8('Bytes'),                     # Number of bytes in active UOW messages
        Uint4('max_messages'),              # Max. number of messages in one UOW
        Uint4('max_bytes'),                 # Max. number of bytes in one UOW
        String('oldest_uow',32),            # Oldest time of UOW creation
        String('newest_uow',32),            # Newest time of UOW creation
        )
        Datamap.__init__(self, 'UOW Statistics', *fields, **kw)

__version__ = '1.0.1'
if __version__ == '1.0.1':
    _svndate='$Date: 2018-05-28 12:00:39 +0200 (Mon, 28 May 2018) $'
    _svnrev='$Rev: 826 $'
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
