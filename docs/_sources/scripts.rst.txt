*******
Scripts
*******

There is one script in adapya-entirex that can be run on the command line.
It accepts Unix style parameters. A help page is shown with the help option.

cmdinfo.py - EntireX Broker CIS Services
========================================

The command line script cmdinfo.py is a client service explorer of the
webMethods EntireX Broker CIS Services.

Only a selection of the available fields is shown (see \*_FIELDS)

This covers the Broker API for Command and Information Services V9.7

Usage::

    cmdinfo [options]

Options
-------
::

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


Examples
--------

    1. show all services for broker class REPTOR and server MMSERV
       and related conversations, units of work and servers;
       show clients starting with userid MM
       show general broker information first::

         > cmdinfo -b zos3:3800 -u MM -s REPTOR/MMSERV/*

    2. shutdown a participant identified by userid / a service / a conversation::

         > cmdinfo -b zos3:3800 -Su OUT4_Reader
                                -Ss REPTOR/MMSERV/OUT4
                                -Sv 1290000000000105




