#! /usr/bin/env python
# -*- coding: latin1 -*-

"""cmdinfo.py interface to Webmethods EntireX Broker CIS Services
and service explorer

Only a selection of the available fields is shown (see _FIELDS)

This covers the Broker API for Command and Information Services V9.7

Usage: cmdinfo [options]

Options::

    -h, --help              display this help
    -b, --broker ..         id of broker ETBxxxxx or hostname:port

    -c, --class ..          Broker server class (selector)
    -d  --detail            info request detailed conversation/uows
    -n, --name ..           Broker server name (selector)
    -k, --token ..          Token
    -m, --maxinfo ..        Receive buffer length - default 32768
    -o, --option ..         Option: QUIESCE, IMMED (first char suffices)
    -p, --puid              Physical user id (selector)
    -q, --seqno <int>       Sequence number (selector)
    -s, --service ..        Broker service (selector)
                              short: -s class/server/service
    -i, --infouid ..        user id for broker communication
    -u, --userid ..         user id for information on active clients (selector)
    -v, --convid ..         conversation id (selector)
    -w, --uowid ..          unit of work (selector)
    -x, --password ..       password
    -t, --trace ..          sum of trace flags
                            1 - dump buffers before Broker call
                            2 -              after call
                            4 - print broker calls, short and data
                            8 - detailed print of buffers

    CIS commands (default command: info)

    -S, --shutdown          needs parameters convid or service or seqno (for server)
                             or userid/puid/token for client
    -P, --purge <uowid>     psf remove uow from persistent store
    -T, --btrace <level>    Broker trace on level 1-8, 0 switch off


Example::

    1. show all services for broker class REPTOR and server MMSERV
       and related conversations, units of work and servers;
       show clients starting with userid MM
       show general broker information first::

         > cmdinfo -b zos3:3800 -u MM -s REPTOR/MMSERV/*

    2. shutdown a participant identified by userid, service and/or conversation::

         > cmdinfo -b zos3:3800 -Su OUT4_Reader
                                -Ss REPTOR/MMSERV/OUT4
                                -Sv 1290000000000105

"""
from __future__ import print_function          # PY3

from adapya.base.defs import Abuf
from adapya.base.dump import dump
from adapya.base.datamap import Datamap, String, Bytes, Filler, Uint1, \
    Uint2, Uint4, Uint8, T_HEX, T_IN, T_OUT, T_INOUT, T_NONE, str_str
from adapya.base.dtconv import intervalstr
from adapya.entirex.broker import Broker, BrokerException
from time import localtime, strftime

cis_version=10
# try this Broker version where Info_* classes in etbcinf.py can be used
# initial communication with Broker the kernel version determines if
# the classes need to be imported from etcinf8.py


class CISError(BrokerException):
    """Example use:
    try:
        info = cis.iget(...)
    except CISError as e:
        if e.epa.cishdr.error_code == x:
            print('\nCIS error: %s on %s/%s/%s' %(e.value,
                sv.server_class,sv.server,sv.service))
    """

    def __init__(self, value, epa):
        self.value = value
        self.epa = epa
    def __str__(self):
        return repr(self.value)



stckintervalstr = lambda i: intervalstr(int(i / 1.048576))
localtime_str = lambda t: strftime("%Y-%m-%d %H:%M:%S",localtime(t))

def usage():
    print(__doc__)

# --- EntireX Broker CIS Objects Constants ----------------------------
#                        * = no further selection crit. needed
CIO_BROKER = 7          #*
CIO_CLIENT = 2          #   active clients
CIO_CMDLOG_FILTER = 23  #
CIO_CONVERSATION = 4    #  active conversations
CIO_NET = 24            #* (INF) NET-WORK
CIO_PARTICIPANT = 18    #
CIO_POOL_USAGE = 25     #* (INF) pool usage and dynam. memory management
CIO_PSF = 9             #  (INF) unit of work status
CIO_PSFADA = 12         #* (INF) Adabas persistent store
CIO_PSFCTREE = 20       #* (INF) c-tree persistent store
CIO_PSFDIV = 11         #* (INF) DIV persistent store
CIO_PSFFILE = 13        #* (INF) (deprecated)
CIO_PSFMSG = 10         #  (INF)
CIO_PUBLICATION = 16    #  (INF) active publications (deprecated)
CIO_PUBLISHER = 15      #  (INF) active publishers (deprecated)
CIO_RESOURCE_USAGE = 26 #* (INF) Broker resource usage
CIO_SECURITY = 21       #*
CIO_SERVER = 1          #  active servers
CIO_SERVICE = 6         #  active services
CIO_SSL = 22            #* SSL communication
CIO_STATISTICS = 27     #* (INF) stats on Broker resources
CIO_SUBSCRIBER = 14     #  (deprecated)
CIO_TCP = 19            #* (INF) TCP communications
CIO_TRANSPORT = 29      #  (CMD)
CIO_TOPIC = 17          #  (INF) active topics (deprecated)
CIO_UOW_STATISTICS = 31 #  (INF) stats on Broker resources
CIO_USER = 28           #  (INF) Info on all users
CIO_WORKER = 8          #  (INF) Info on all workers
CIO_WORKER_USAGE = 8    #* (INF) Info on all workers

cio_str = lambda i: str_str(i, {7:'BROKER',2:'CLIENT',23: 'CMDLOG_FILTER',
            4:'CONVERSATION',24:'NET',18:'PARTICIPANT',
            25:'POOL_USAGE', 9:'PSF', 12:'PSFADA', 20:'PSFCTREE',
            11:'PSFDIV', 16:'PUBLICATION', 15:'PUBLISHER', 26:'RESOURC_USAGE',
            21:'SECURITY',1:'SERVER',6:'SERVICE',22:'SSL',27:'STATISTICS',
            14:'SUBSCRIBER',19:'TCP', 29:'TRANSPORT', 17:'TOPIC',
            31:'UOW_STATISTICS', 28:'USER', 8:'WORKER', 8:'WORKER_USAGE'})


# --- EntireX Broker CIS Commands Constants ----------------------------
CIC_ALLOW_NEWUOWMSGS = 13
CIC_CLEAR_CMDLOG_FILTER = 20
CIC_CONNECT_PSTORE = 17
CIC_DISABLE_ACCOUNTING = 28
CIC_DISABLE_CMDLOG = 24
CIC_DISABLE_CMDLOG_FILTER = 22
CIC_DISABLE_DYN_WORKER = 37
CIC_DISCONNECT_PSTORE = 18
CIC_DISPLAY_REQUESTS = 45   # display number of requests
CIC_ENABLE_ACCOUNTING = 27
CIC_ENABLE_CMDLOG = 23
CIC_ENABLE_CMDLOG_FILTER = 21
CIC_ENABLE_DYN_WORKER = 38
CIC_FORBID_NEWUOWMSGS = 14
CIC_NO_OPERATION = 88
CIC_PRODUCE_STATISTICS = 25
CIC_PURGE = 12
CIC_RESET_USER = 29
CIC_RESUME = 31
CIC_SET_CMDLOG_FILTER = 19
CIC_SET_SINGLE_CONVERSATION = 40  # requires interface V8
CIC_SET_UOW_STATUS = 42  # requires V10
CIC_SHUTDOWN = 8
CIC_START = 33
CIC_STATUS = 36
CIC_STOP = 32
CIC_SUBSCRIBE = 15  # deprecated
CIC_SUSPEND = 30
CIC_SWITCH_CMDLOG = 26
CIC_TRACE_FLUSH = 35
CIC_TRACE_OFF = 2
CIC_TRACE_ON = 1
CIC_TRAP_ERROR = 34
CIC_UNSUBSCRIBE = 16  # deprecated

cic_str = lambda i: str_str(i, {
    13:'ALLOW_NEWUOWMSGS',20:'CLEAR_CMDLOG_FILTER',17:'CONNECT_PSTORE',
    28:'DISABLE_ACCOUNTING',24:'DISABLE_CMDLOG',22:'DISABLE_CMDLOG_FILTER',
    37:'DISABLE_DYN_WORKER',18:'DISCONNECT_PSTORE',27:'ENABLE_ACCOUNTING',
    23:'ENABLE_CMDLOG',21:'ENABLE_CMDLOG_FILTER',38:'ENABLE_DYN_WORKER',
    14:'FORBID_NEWUOWMSGS',88:'NO_OPERATION',25:'PRODUCE_STATISTICS',
    12:'PURGE',29:'RESET_USER',31:'RESUME',19:'SET_CMDLOG_FILTER',
    8:'SHUTDOWN',33:'START',36:'STATUS',32:'STOP',15:'SUBSCRIBE',
    30:'SUSPEND',26:'SWITCH_CMDLOG',35:'TRACE_FLUSH',2:'TRACE_OFF',
    1:'TRACE_ON',34:'TRAP_ERROR',16:'UNSUBSCRIBE'} )


# --- EntireX Broker CIS Options Constants ----------------------------
CIP_IMMED = 3
CIP_QUIESCE = 4
CIP_TR_LEVEL1 = 11
CIP_TR_LEVEL2 = 12
CIP_TR_LEVEL3 = 13
CIP_TR_LEVEL4 = 14
CIP_TR_LEVEL5 = 15
CIP_TR_LEVEL6 = 16
CIP_TR_LEVEL7 = 17
CIP_TR_LEVEL8 = 18

CIP_UOW_STATUS_ACCEPTED = 20
CIP_UOW_STATUS_CANCELLED = 21
CIP_ETB_FORCE = 26    # Forced operation
CIP_ETB_PREFETCH = 27 # ARF: OPTION PREFETCH


cip_str = lambda i: str_str(i, { 3:'CIP_IMMED', 4:'QUIESCE', 11:'TR_LEVEL1',
            12:'TR_LEVEL2',13:'TR_LEVEL3',14:'TR_LEVEL4',15:'TR_LEVEL5',
            16:'TR_LEVEL6',17:'TR_LEVEL7',18:'TR_LEVEL8',
            20:'UOW_STATUS_ACCEPTED', 21:'UOW_STATUS_CANCELLED',
            26:'ETB_FORCE', 27:'ETB_PREFETCH' } )


# Broker Information service Error Codes
bis_error = lambda i: str_str(i, {
    0:'Successful response', 1:'Invalid block length',
    2:'Invalid VERSION', 3:'OBJECT-TYPE missing',
    4:'Nothing found for this request', 5:'Invalid OBJECT-TYPE',
    6:'Invalid Info Level', 7:'Block length too short for Object Type',
    8:'User selection must be unique', 9:'Service selection must be unique',
    10:'Topic name must be specified (deprecated)',
    11:'PUID not possible with Info Level SHORT',
    })

# Broker command service Error Codes
bcs_error = lambda i: str_str(i, {
    0:'Successful response', 2:'Invalid VERSION', 3:'OBJECT-TYPE is missing',
    5:'Invalid OBJECT-TYPE', 20:'The user is not authorized to issue Broker commands',
    21:'Invalid COMMAND', 22:'Invalid OPTION', 23:'Shutdown possible for servers only',
    24:'Participant not found', 25:'Purge UOW failed',
    26:'User specification must be unique', 27:'Topic name must be specified (deprecated)',
    28:'Add subscription failed (deprecated)', 29:'Remove subscription failed (deprecated)',
    30:'User must be specified', 31:'Class/Server/Service must be unique',
    32:'Class and Topic cannot both be specified (deprecated)', 33:'Class, Topic or User must be specified',
    34:'Set command log filter failed', 35:'Clear command log filter failed',
    36:'Enable command log filter failed', 37:'Disable command log filter failed',
    38:'Switch command log files failed', 39:'Set security trace level failed',
    40:'Set PSTORE (PSF) trace level failed', 41:'Enable command logging failed',
    42:'Disable command logging failed', 43:'Connect PSTORE failed',
    44:'Disconnect PSTORE failed', 45:'Allow new UOW messages failed',
    46:'Forbid new UOW messages failed', 47:'Enable accounting failed',
    48:'Disable accounting failed', 49:'Reset user failed',
    50:'Command refused in current RUN-MODE', 51:'Service must be specified',
    52:'Service not found', 53:'CONVID must be specified', 54:'Conversation not found',
    55:'Cannot inhibit Conversation', 56:'Only supported for messages',
    57:'Cannot lock Conversation', 58:'Not for currently running Conversation',
    59:'Security violation detected', 60:'Invalid transport ID',
    61:'Cannot execute command', 62:'Command ignored. Only one Communicator left',
    63:'Command ignored. Cannot stop all Communicators', 64:'Communicator currently not suspended',
    65:'Communicator currently not stopped', 66:'Communicator currently not active',
    67:'Enable Dynamic Worker Management failed', 68:'Disable Dynamic Worker Management failed',
    69:'Transport reserved for Broker Service', 70:'TRACE-FLUSH failed',
    71:'Cannot set single-conversation mode because service is being used in other mode'\
       ' (still active conversations for service)',
    72:'Verification of attribute file failed', 73:'Cannot delete deferred service with UOW',
    74:'Cannot set UOW status', 75:'Cannot add service to SCM record',
    76:'Update SCM record failed', 77:'Conversation contains unprocessed UOWs',
    })

# --- EntireX Broker Command Request Structure ------------------------
class Cisreq(Datamap):
    def __init__(self, **kw):
        fields=(                        # Available with CIS Interface version
        Uint2('version',         opt=T_IN), # 1 Interface version
        Uint2('object_type', opt=T_IN, ppfunc=cio_str), # 1 Object type to which the command applies
        Uint2('command', opt=T_IN, ppfunc=cic_str),     # 1 CIS command
        Uint2('option', opt=T_IN, ppfunc=cip_str),      # 1 CIS option
        Bytes('puid',         28,opt=T_HEX),# 1 internal userid that distinguishes users with same userids
                                            #   id obtained from previous call, no translation done
        String('uowid',       16,opt=T_IN), # 2 Selector, optional, unit of work to be purged
        String('topic',       96,opt=T_IN), # 4 Selector, optional, topic to be subscribed or unsubscribed to
        String('uid',         32,opt=T_IN), # 4 Selector, optional, user name for subscription/unsubscription
                                            #   and participant shutdown
        String('token',       32,opt=T_IN), # 4 Selector, optional, token for subscription/unsubscription
                                            #   and participant shutdown
        String('server_class',32,opt=T_IN), # 5 Selector, optional, for command log filter addition or removal
        String('server',      32,opt=T_IN), # 5 Selector, optional, for command log filter addition or removal
        String('service',     32,opt=T_IN), # 5 Selector, optional, for command log filter addition or removal
        Filler('reserved',    32),          # 5 Reserved
        String('conv_id',     16,opt=T_IN), # 7 Selector, optional, for shutdown conversation
        String('transportid',  3,opt=T_IN), # 7 Selector, optional, for transport task (NET|Snn|Tnn)
                                            #   required for RESUME,START,STATUS,STOP,SUSPEND
        Uint1('exclude_attach',  opt=T_IN), # 7 Optional. Exclude attach servers when shutting down a service
        Uint4('seqno',           opt=T_IN), # 7 Optional. Sequence number of participant (e.g. client, server,
                                            #   publisher) to be shut down. Can be used instead of puid
        Uint4('error_number',    opt=T_IN), # 7 Optional. Sequence number of participant (e.g. client, server,
        )
        Datamap.__init__(self, 'Cisreq', *fields, **kw)

    def reset(self,v=cis_version):
        """ Reset values of the CIS Request instance """

        self.update(
            version=v,                      # interface level 8
            # init alpha selection fields with blanks
            conv_id='',
            seqno=0,
            server_class='',
            server='',
            service='',
            token='',
            topic='',
            transportid='',
            uid='',
            uowid='',
        )

errinf_str = lambda i: str_str(i, {
    0:'OK',1:'Invalid block length',2:'Invalid API version',
    3:'Object Type missing',4:'Nothing found for this request',
    5:'Invalid Object Type',6:'Invalid Info Level',
    7:'Block length too short for Obj. Type',8:'User selection must be unique',
    9:'Service selection must be unique',10: 'Topic name must be specified',
    })


# --- EntireX Broker CIS Response Header ------------------------------
# (Struct HD_CIS). Common header used by information services and
# the command service.
# The header structure is always the first structure
# in the receive buffer that comes back from an information
# or command service request. Even receive buffers obtained
# with subsequent RECEIVE commands have this structure as the
# first part of the buffer.
class Cishdr(Datamap):
    def __init__(self, **kw):
        fields=(
        Uint4('error_code'),                # 1 CIS return code (0 = OK)
        Uint4('totobj'),                    # 1 Total number of objects returned in object list
        Uint4('curobj'),                    # 1 Number of objects returned within current receive block
        Uint4('max_sc_len'),                # 1 longest SERVER-CLASS value in object list
        Uint4('max_sn_len'),                # 1 longest SERVER-NAME value in object list
        Uint4('max_sv_len'),                # 1 longest SERVICE value in object list
        Uint4('max_uid_len'),               # 1 longest USER-ID value in object list
        Uint4('max_tk_len'),                # 1 longest TOKEN value in object list
        Uint4('max_topic_len'),             # 4 longest TOPIC value in object list
        Uint4('requesttime',ppfunc=localtime_str),# 4 time that request was received by broker kernel
        Uint4('reserved',opt=T_NONE),       # 4
        String('etb_error_code',8),         # 5 Secondary error code from broker kernel
        String('etb_error_text',40),        # 5 Secondary error text from broker kernel
        Uint4('max_ppc_lib_len'),           # 6 longest RPC-LIB value in object list
        Uint4('max_ppc_pgm_len'),           # 6 longest RPC-PGM value in object list
        )
        Datamap.__init__(self, 'Cishdr', *fields, **kw)



# --- EntireX Broker Information Request Structure ------------------------
class Infreq(Datamap):
    """ Information request Structure Class
    """
    def __init__(self, **kw):
        fields=(                            # Available with CIS Interface version
                                            # | Optional/Required
                                            # | |
        Uint4('block_length'),              # 1 R  Return data in this length
        Uint2('version'),                   # 1 R  Interface version
        Uint2('reserved1',opt=T_NONE),      #
        Uint2('object_type'),               # 1 R  Object type for which info is requested
        String('uid',    32),               # 1 O  Selector user id of client or server
        Bytes('puid',    28,opt=T_HEX),     # 1 O  Selector internal userid that distinguishes users
                                            #      with same userids, no translation done
        String('token',       32),          # 1 O  Selector
        String('server_class', 32),         # 1 O  Selector
        String('server',      32),          # 1 O  Selector
        String('service',     32),          # 1 O  Selector
        String('conv_id',     16),          # 1 O  Selector
        Uint2('reserved2',opt=T_NONE),      # 1
        String('uowid',       16),          # 2 O  Selector
        Uint1('uowstatus'),                 # 2 O  Selector
        String('userstatus',  32),          # 2 O  Selector
        String('recvuid',     32),          # 2 O  Selector UOW reciever's user id
        String('recvtoken',   32),          # 2 O  Selector UOW reciever's token
        String('recvserver',  32),          # 2 O  Selector UOW reciever's server name
        String('recvservice', 32),          # 2 O  Selector UOW reciever's service name
        String('recvclass',   32),          # 2 O  Selector UOW reciever's class name
        String('reserved3', 3,opt=T_NONE),  # 2
        String('topic', 96),                # 4 O  Selector
        String('publicationid', 16),        # 4 O  Selector
        Uint2('subscriptiontype'),          # 4 O  Selector
        Uint2('reserved4',opt=T_NONE),      # 4
        Uint2('conv_type'),                 # 5 O  Selector
        Uint2('reserved5',opt=T_NONE),      # 5
        )
        Datamap.__init__(self, 'Infreq', *fields, **kw)

    def reset(self,v=cis_version):
        """ reset values of the Information Request instance """

        self.update(
            version=v,                     # interface level 9 (UOW statistics)
            # init alpha selection fields with blanks
            uid='',
            token='',
            server_class='',
            server='',
            service='',
            conv_id='',
            uowid='',
            userstatus='',
            recvuid='',
            recvtoken='',
            recvserver='',
            recvservice='',
            recvclass='',
            topic='',
            publicationid='',
        )


class Cis(object):
    def __init__(self, cis='INFO', broker='', user='', trace=0, rcvsize=32768):
        """ Command and Information service object

            cis = default 'INFO' - full information on all clients/servers/conversations
                  'CMD'          - command services
                  'USER-INFO'    - Information limited to user's own resources
                  'PARTICIPANT-SHUTDOWN'
                  'SECURITY-CMD'

        """
        global cis_version
        self.rcvsize=rcvsize
        self.bb = Broker()
        self.bb.trace = trace & 7
        #bb.trace=1 # dump buffers before Broker calls
        #bb.trace=2 # dump buffers after Broker calls
        # bb.trace=4 # print Broker calls
        # bb.trace=6 # print Broker calls + dump buffers after
        self.bb.broker_id = broker
        self.bb.user_id = user
        self.trace = trace

        # set CIS fixed service names
        self.bb.server_class= 'SAG'
        self.bb.server_name = 'ETBCIS'
        self.bb.service     =  cis       # type of CIS service (INFO, CMD, ..)

        # set up CIS structures: request and info buffer
        self.cishdr=Cishdr()    # cis header in receive / info buffer

        self.bb.receive_buffer = Abuf(rcvsize)
        self.bb.receive_length = rcvsize

        self.cishdr.buffer=self.bb.receive_buffer

        if cis == 'INFO':
            self.infreq=Infreq()
            self.infreq.buffer=Abuf(self.infreq.dmlen)
            self.infreq.reset()                                 # reset search fields
            self.infreq.block_length=rcvsize-self.cishdr.dmlen  # size of usable info buffer

            self.bb.send_buffer=self.infreq.buffer
            self.bb.send_length=self.infreq.dmlen

        elif cis in ('CMD', 'PARTICIPANT-SHUTDOWN', 'SECURITY-CMD'):
            self.req=Cisreq()
            self.req.buffer=Abuf(self.req.dmlen)
            self.req.reset(v=cis_version)        # reset optional fields

            self.bb.send_buffer=self.req.buffer
            self.bb.send_length=self.req.dmlen

        else:
            print('Unsupported request', cis)
            print('Terminating')
            exit(1)


    def __enter__(self):                    # context manager
        global cis_version

        print('\n%s' % self.bb.version())

        kernel_version = self.bb.kernelVersion()

        print('\nKernel %s \n    with kernelsecurity=%s' % (
            kernel_version, self.bb.kernelsecurity))

        # extract major version number: "Version 9.12.0.1"
        _, v2 = kernel_version.split(' ',1)  # maxsplit=1 in PY3
        major, _ = v2.split('.',1)            # maxsplit=1 in PY3

        kv = int(major)

        if kv < 10:
            cis_version = 8

        # bb.kernelsecurity=KERNEL_SECURITY_NO this is set by kernelVersion()
        # when using ACI level 8 or higher

        self.bb.logon()      # L O G O N

        # print('Kernel Version=%s' % bb.kernelVersion())
        # print('server_class=%s\nserver_name=%s\nservice=%s'% \
        #    (self.bb.server_class, self.bb.server_name, self.bb.service))

        print('\nStarted CIS Session with Broker %s' % self.bb.broker_id)
        return self

    def __exit__(self, type, value, tb):    # context manager
        self.bb.logoff()
        print('Logged off from CIS Session with Broker')


    def icmd(self, obj, cmd, option=0,conv_id='',puid='',seqno=0,
            server_class='',server='',service='',token='',uid='',uowid=''):
        """ send command request to Broker

        Example: Perform CIS Command
        >> with Cis(cis='CMD',broker='da3f:3800',user='MM') as cis:
        >>     ibr = cis.icmd(?)
        >>     ibr.dprint()
        >>

        """

        self.req.update(
            object_type=obj,
            command=cmd,
            option=option,
            conv_id=conv_id,             # selection
            server_class=server_class,   # selection
            server=server,               # selection
            service=service,             # selection
            puid=puid,                   # selection
            seqno=seqno,
            token=token,                 # selection
            uid=uid,                     # selection
            uowid=uowid,                 # selection
            )

        try:
            self.bb.conv_id='NONE'  # required
            self.bb.wait='YES'      # 0s -> 00200031
            if cmd == CIC_SET_SINGLE_CONVERSATION:
                # needed for other commands that operate on objects of calling user ?
                self.bb.token=token     # also set it in etbcb

            self.bb.send()

            if self.trace & 8:
                print('after cmd execution call to %s/%s/%s' % (
                    self.bb.server_class, self.bb.server_name, self.bb.service))
                self.req.dprint()
                self.cishdr.dprint()

        except:
            if self.trace&8:
                self.req.dprint()
                self.cishdr.dprint()
                self.bb.dprint()
            raise CISError('Error during processing CIS command',self)

        finally:
            if self.cishdr.error_code > 0:
                ec = self.cishdr.error_code
                raise CISError('Broker Command Service Error %d: %s' % (
                               ec, bcs_error(ec)), self)

    def iget(self, itype, uid='', puid='', server_class='', server='',service='',
            token='',conv_id=''):
        """ function to get one info object
        Example: get and print general BROKER information
        >> with Cis(broker='da3f:3800',user='MM') as cis:
        >>     ibr = cis.iget(CIO_BROKER)
        >>     ibr.dprint()
        >>

        """
        global cis_version

        if cis_version > 8:
            from adapya.entirex.etbcinf import Info_broker, Info_UOW_statistics
        else:
            from adapya.entirex.etbcinf8 import Info_broker, Info_UOW_statistics

        # info objects returning only one item - suitable for iget()
        infos = {CIO_BROKER: Info_broker,
            CIO_UOW_STATISTICS: Info_UOW_statistics}      # currently limited

        Infoclass = infos.get(itype,None)

        if Infoclass:
            self.infreq.object_type = itype     # set object type in request
            info = Infoclass()
        else:
            raise CISError('Invalid CIS object for ireader() type %s' % cio_str(itype),self)

        self.infreq.update(
            version=9 if itype == CIO_UOW_STATISTICS else cis_version,
            server_class=server_class,   # selection
            server=server,               # selection
            service=service,             # selection
            uid=uid,                     # selection
            puid=puid,                   # selection
            token=token,                 # selection
            conv_id=conv_id,             # selection
            )

        try:
            self.bb.conv_id='NEW'
            self.bb.wait='YES'      # 0s -> 00200031
            self.bb.send()

            if self.trace & 8:
                print('after first call')
                self.infreq.dprint()
                self.cishdr.dprint()

            if self.cishdr.error_code == 4:
                info = None
            elif self.cishdr.error_code > 0:
                ec = self.cishdr.error_code
                raise CISError('Broker Information Service Error %d: %s' % (
                               ec, bis_error(ec)), self)
            else: # self.cishdr.error_code == 0
                if self.cishdr.totobj != 1:
                    raise CISError('Nothing returned from Broker CIS',self)

                offset=self.cishdr.dmlen       # first info after cishdr

                info.buffer=Abuf(info.dmlen)
                info.buffer.value=self.bb.receive_buffer[offset:offset+info.dmlen]

            self.bb.endConversation()
            return info

        except:
            raise   # return any error



    def iread(self, itype, uid='', puid='', token='',
            server_class='', server='',service='',
            conv_id='',uowid='',uowstatus=0,userstatus='',
            recvuid='',recvtoken='',recvclass='',recvserver='',recvservice='',
            topic='',publicationid='',
            conv_type=0,subscriptiontype=0):
        """ generator returning info objects from class
        Example: read and print information on all services of REPTOR server_class
        >> cis=Cis(broker='da3f:3800',user='MM')
        >> for iob in cis.iread(CIO_SERVICE,server_class='REPTOR'):
        >>     iob.dprint()
        >>

        """
        global cis_version

        if cis_version > 8:
            from adapya.entirex.etbcinf import Info_conversation, \
                Info_client, Info_server, Info_psf, Info_service, Info_UOW_statistics
        else:
            from adapya.entirex.etbcinf8 import Info_conversation, \
                Info_client, Info_server, Info_psf, Info_service, Info_UOW_statistics

        ii = Broker()   # establish unique conversation for read sequence
        # copy properties from own Cis object
        ii.trace        = self.bb.trace
        ii.broker_id    = self.bb.broker_id
        ii.user_id      = self.bb.user_id

        # set CIS fixed service names
        ii.server_class = 'SAG'
        ii.server_name  = 'ETBCIS'
        ii.service      = 'INFO'          # Full information on all clients/servers/conversations

        cishdr=Cishdr()    # cis header in receive / info buffer

        infreq=Infreq()
        infreq.buffer=Abuf(infreq.dmlen)
        infreq.block_length=self.rcvsize-cishdr.dmlen  # size of usable info buffer
        infreq.version=cis_version                     # interface level 8
        # init alpha selection fields from call parameters
        infreq.uid=uid
        infreq.puid=puid
        infreq.token=token
        infreq.server_class=server_class
        infreq.server=server
        infreq.service=service
        infreq.conv_id=conv_id
        infreq.uowid=uowid
        infreq.userstatus=userstatus
        infreq.recvuid=recvuid
        infreq.recvtoken=recvtoken
        infreq.recvserver=recvserver
        infreq.recvservice=recvservice
        infreq.recvclass=recvclass
        infreq.topic=topic
        infreq.publicationid=publicationid
        infreq.subscriptiontype=subscriptiontype
        infreq.conv_type=conv_type

        ii.receive_buffer=Abuf(self.rcvsize)
        ii.receive_length = self.rcvsize

        cishdr.buffer=ii.receive_buffer

        ii.send_buffer=infreq.buffer
        ii.send_length=infreq.dmlen

        infos = {CIO_CLIENT: Info_client, CIO_SERVER: Info_server,
                CIO_CONVERSATION: Info_conversation, CIO_PSF: Info_psf,
                CIO_SERVICE: Info_service, CIO_UOW_STATISTICS: Info_UOW_statistics }

        Infoclass = infos.get(itype,None)

        if Infoclass:
            infreq.object_type = itype     # set object type in request
            info = Infoclass()
        else:
            raise 'Invalid CIS object for ireader() type %s' % cio_str(itype)

        try:
            ii.conv_id='NEW'
            ii.wait='YES'      # 0s -> 00200031
            ii.send()

            if self.trace & 8:
                print('after first call')
                infreq.dprint()
                cishdr.dprint()

            if self.cishdr.error_code == 4: # 4 nothing found
                ec = self.cishdr.etb_error_code
                et = self.cishdr.etb_error_text
                if not ec == '00000000':
                    print('Broker Information Service ETB Error %d: %s\nNo objects returned' % (
                               ec, et))
            elif self.cishdr.error_code > 0: # print any other error
                ec = self.cishdr.error_code
                raise CISError('Broker Information Service Error %d: %s' % (
                               ec, bis_error(ec)), self)

            if cishdr.totobj == 0:
                raise StopIteration

            remaining = cishdr.totobj

            while 1:
                offset=cishdr.dmlen       # first info after cishdr

                for i in range(cishdr.curobj):
                    # print('returning %d. object in current' % (i)
                    # info.dprint()
                    info.buffer=Abuf(info.dmlen)
                    info.buffer.value=ii.receive_buffer[offset:offset+info.dmlen]

                    yield info
                    offset += info.dmlen  # next offset in receive buffer

                remaining -= cishdr.curobj

                if remaining > 0:
                    ii.receive()
                    if self.trace & 8:
                        print('after next call')
                        infreq.dprint()
                        cishdr.dprint()
                else:
                    raise StopIteration

        except:
            raise   # return with StopIteration or any other error
        finally:
            if cishdr.totobj > 0:
                ii.endConversation()

if __name__=='__main__':

    import getopt
    import sys
    from collections import defaultdict, Counter

    cmd=0       # CIC_ command
    option=0    # CIP_IMMED /CIP_QUIESCE   # CIP_ option
    obj=0       # CIO_ object
    puid=''
    pwd=None
    brokerid = 'da3f:3800'
    btrace=0
    bservice=bclass=bname=''
    detail=0
    maxinfo=32768
    convid=''
    seqno=0
    uowid=''
    token=''
    iserv='INFO'    # CIS SERVICE
    buser='cmdinfo.py'  # for communication with broker
    uid=''   # for getting information on broker clients
    try:
        opts, args = getopt.getopt(sys.argv[1:],
            'hb:c:di:k:m:n:o:p:q:P:s:St:T:u:v:w:',
            ['help','broker=','btrace=','class=','convid=','detail','infouid=',
            'name=','option=','password=','puid=','purge=','maxinfo=',
            'seqno=','service=','shutdown','shutserv',
            'uowid=','userid=','token=','trace='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-b', '--broker'):
            brokerid = arg
        elif opt in ('-c', '--class'):
            bclass=arg
        elif opt in ('-d', '--detail'):
            detail = 1 # detailed info with conversations and uows
        elif opt in ('-n', '--name'):
            bname=arg
        elif opt in ('-o', '--option'):
            if arg.upper().startswith('Q'):
                option=CIP_QUIESCE
            elif arg.upper().startswith('I'):
                option=CIP_IMMED
        elif opt in ('-x', '--password'):
            pwd=arg
        elif opt in ('-p', '--puid'):
            puid=arg
        elif opt in ('-P', '--purge'):
            cmd=CIC_PURGE
            uowid = arg
        elif opt in ('-m', '--maxinfo'):
            maxout=int(arg)
        elif opt in ('-q', '--seqno'):
            seqno=int(arg)
        elif opt in ('-s', '--service'):
            sss=arg.split('/')      # --service class:server:service
            del sss[3:]             # skip any extranous items
            bservice=sss.pop()
            if sss:
                bname=sss.pop()
                if sss:
                    bclass=sss.pop()
        elif opt in ('-S', '--shutdown'):
            cmd=CIC_SHUTDOWN
        elif opt in ('-T', '--btrace'):
            tlevel=int(arg)
            if tlevel > 8:
                tlevel=8
            if tlevel > 0:
                cmd=CIC_TRACE_ON
                option = CIP_TR_LEVEL1 - 1 + tlevel
            else:
                cmd=CIC_TRACE_OFF
        elif opt in ('-i', '--infouid'):
            buser=arg
        elif opt in ('-u', '--userid'):
            uid=arg
        elif opt in ('-v', '--convid'):
            convid=arg
            detail = 1
        elif opt in ('-w', '--uowid'):
            uowid=arg
            detail = 1
        elif opt in ('-k', '--token'):
            token=arg
        elif opt in ('-t', '--trace'):
            btrace=int(arg)

    print(80*'=')

    if cmd == CIC_SHUTDOWN:
        if convid:
            obj = CIO_CONVERSATION
            iserv = 'CMD'
            print('\nBroker CIS command SHUTDOWN for CONVERSATION %s' % convid)
        elif seqno or puid:
            obj = CIO_SERVER
            iserv = 'CMD'
            print('\nBroker CIS command SHUTDOWN for server seqno=%d/puid=%s' % (seqno,puid))
        elif bservice:
            obj = CIO_SERVICE
            iserv = 'CMD'
            print('\nBroker CIS command SHUTDOWN for service %s/%s/%s' % (bclass,bname,bservice))
        elif uid:
            obj = CIO_PARTICIPANT
            iserv = 'PARTICIPANT-SHUTDOWN'
            print('\nBroker CIS command SHUTDOWN for participant %s/%s/%d' % (uid,token,seqno))
        else:
            print('\nBroker CIS command client only supports SHUTDOWN with CONVERSATIONID or SERVICE or participant userid or server seqno')
            exit(1)
    elif cmd == CIC_PURGE:
        if uowid:
            obj = CIO_PSF
            iserv = 'CMD'
            print('\nBroker CIS command PURGE unit-of-work %s' % uowid)
        else:
            print('\nBroker CIS command PURGE needs UOWID')
            exit(1)
    elif cmd == CIC_TRACE_ON:
            obj = CIO_BROKER
            iserv = 'CMD'
            print('\nBroker CIS command TRACE-ON %d' % tlevel)
    elif cmd == CIC_TRACE_OFF:
            obj = CIO_BROKER
            iserv = 'CMD'
            print('\nBroker CIS command TRACE-OFF')


    if cmd > 0: # all comands are processed here
        with Cis(cis=iserv,broker=brokerid,user=buser,trace=btrace) as cis:
            ibr = cis.icmd(obj, cmd, option=option, uowid=uowid,conv_id=convid,seqno=seqno,
                server=bname,service=bservice,server_class=bclass,token=token,uid=uid,puid=puid)
        exit()

    # else: (not a command)
    #       use information services

    # select fields for display of info structures
    BROKER_FIELDS=('runtime','maxmsgsize','platformname','product_version',
        'pstoretype','pstore','uwtime','client_nonact',)
    SERVICE_FIELDS=('service','conv_nonact','servers_act','conv_act','uwtime',
        'totaluows','store','deferrred',
        'arf','scm','prefetch','maxPostponeAttempts','postponeDelay' ) # 10
    CONV_FIELDS=('conv_id','service','conv_nonact',
        'serveruid','servertoken','clientuid','clienttoken','conv_nonact',
        'last_active','totaluows',
        'arf','scm','prefetch','roaming')    # 10: prefetch / roaming ???
    PSF_FIELDS=('uow_id','uowstatus','uwcreate_time','uw_lifetime','eoc','deliveries',
        'msgcnt','msgsize',
        'arf','scm',    # 10 line too long: 'maxPostponeAttempts','remainingPostponeAttempts','postponeDelay','back2accepted',
        'commit_time')  # 10  create_time = Pstore V5??
    CS_FIELDS=('uid','puid','puidTrans','token','status','waitconvid','service','conv_act',
        'service_act','last_active','nonact','waits_new','waits_old',
        'convs','active_uow','recv_option','created','seqno',
        'arf','scm','prefetch','roaming')    # 10: prefetch / roaming ???

    svcs_client = defaultdict(list)
    conv_client = Counter()
    uows_client = Counter()

    with Cis( broker=brokerid,user=buser,trace=btrace) as cis:
        ibr = cis.iget(CIO_BROKER)
        ibr.dprint(selectfields=BROKER_FIELDS)

        for sv in cis.iread(CIO_SERVICE, server_class=bclass, server=bname,service=bservice):
            # Service selectors: puid or uid/token or uid or token
            #                    class/server/service
            print(80*'-')
            sv.dprint(selectfields=SERVICE_FIELDS)

            for sr in cis.iread(CIO_SERVER, server=sv.server, server_class=sv.server_class,
                                service=sv.service):
               # possible selectors: puid or uid/token or uid or token
               #                     class/server/service
               sr.dprint(selectfields=CS_FIELDS)

            css=''
            uidtok=''

            if detail:
                for j, cv in enumerate(
                        # Conversation selectors: puid or uid/token or uid or token
                        #                        class/server/service or conv_id
                        cis.iread(CIO_CONVERSATION, server=sv.server,
                            server_class=sv.server_class, service=sv.service) ):
                    print('Conversation %d'%(j+1))
                    cv.dprint(selectfields=CONV_FIELDS)
                    if not css:
                        css = '%s/%s/%s' % (cv.server_class,cv.server,cv.service)
                        uidtok = (cv.clientuid,cv.clienttoken)
                        svcs_client[uidtok].append(css)     # note all services client uses
                    conv_client[uidtok] += 1                # count all conversations client has
                    uows_client[uidtok] += cv.totaluows     # count all uows client has

                    if cv.totaluows > 0:
                        print('Persistent messages for conversation %s' % cv.conv_id)
                        header=1
                        for ps in cis.iread(CIO_PSF, conv_id=cv.conv_id, server=sv.server,
                                            server_class=sv.server_class, service=sv.service):
                            # Persistent store selectors: puid or uid/token or uid or token or conv_id
                            #          class/server/service or any combination
                            if header:
                                ps.lprint(header=1,selectfields=PSF_FIELDS)
                                header=0
                            ps.lprint(selectfields=PSF_FIELDS)
                        print() # new line
            else: # no detail
                us = cis.iget(CIO_UOW_STATISTICS, server=sv.server,
                             server_class=sv.server_class, service=sv.service)
                print()
                if us:
                    # UOW Statistics
                    us.dprint()
                else:
                    print('No UOW statistics available for %s/%s/%s\n' %(
                        sv.server_class,sv.server,sv.service))

        if uid:
            print(80*'=')
            print('Broker clients with USER ID starting with %r' % uid)
            for ob in cis.iread(CIO_CLIENT):
                # Client selectors: uowid or uid/token or uid or token
                #    server=sv.server,server_class=sv.server_class,service=sv.service)

                if not ob.uid.startswith(uid):   # post selection
                    continue

                ob.dprint(selectfields=CS_FIELDS)
                uidtok=(ob.uid,ob.token)
                svs = svcs_client[uidtok]
                if svs:
                    print(' Client has total of %d CONVs and %d committed UOWs receivable with services' % (
                        conv_client.get(uidtok,0),
                        uows_client.get(uidtok,0)))
                    for sv in svs:
                        print('\t',sv)
                print()

        #for i, ob in enumerate(
        #        cis.iread(CIO_SERVER, uid='REPTOR-DA3F-----MM10007') ):
        #    print('Server %d'%(i+1)
        #    ob.dprint()



__version__ = '1.0.1'
if __version__ == '1.0.1':
    _svndate='$Date: 2018-07-19 19:42:39 +0200 (Thu, 19 Jul 2018) $'
    _svnrev='$Rev: 842 $'
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
