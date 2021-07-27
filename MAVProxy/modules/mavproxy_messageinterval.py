#!/usr/bin/env python
'''
Message interval setter
Sets message intervals and streamrates
'''

import time

from MAVProxy.modules.lib import mp_module
from pymavlink import mavutil

class MessageInterval(mp_module.MPModule):
    def __init__(self, mpstate):
        """Initialise module"""
        super(MessageInterval, self).__init__(mpstate, "messageinterval", "")
        self.mpstate = mpstate
        self.message_intervals = {}
        self.last_time = time.time()
        self.streamrate = 1.0
        self.add_command('messageinterval',
                         self.cmd_messageinterval,
                         "messageinterval module",
                         ['message', 'stream'])
        self.refresh_rate = 10

    def usage(self):
        '''show help on command line options'''
        return """Usage: messageinterval message <message_id> <value in Hz>
                         messageinterval stream <value in Hz>"""

    def cmd_messageinterval(self, args):
        '''control behaviour of the module'''
        if len(args) >= 1:
            command = args[0]
            if command == "message":
                if len(args) != 3:
                    print(self.usage())
                    return
                message = int(args[1])
                rate = float(args[2])
                self.message_intervals[message] = 1000000/rate
            elif command == "stream":
                if len(args) != 2:
                    print(self.usage())
                    return
                self.streamrate = float(args[1])

    def idle_task(self):
        '''called rapidly by mavproxy'''
        if time.time() - self.last_time > self.refresh_rate:
            self.last_time = time.time()
            # print("firing")
            # print(self.message_intervals)
            # request streams first, then override asking for individual messages
            self.master.mav.request_data_stream_send(
                self.mpstate.settings.target_system,
                self.mpstate.settings.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL,
                self.streamrate,
                1  # 1 to start sending
            )
            for message, interval in self. message_intervals.items():
                self.master.mav.command_long_send(
                    self.mpstate.settings.target_system,  # target_system
                    self.mpstate.settings.target_component,
                    mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
                    0,
                    message,
                    int(interval),
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)


def init(mpstate):
    '''initialise module'''
    return MessageInterval(mpstate)
