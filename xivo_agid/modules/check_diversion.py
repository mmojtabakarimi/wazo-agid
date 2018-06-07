# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_agid import agid
from xivo_agid import objects


def check_diversion(agi, cursor, args):
    queueid = agi.get_variable('XIVO_DSTID')
    try:
        queue = objects.Queue(agi, cursor, xid=int(queueid))
    except (ValueError, LookupError), e:
        agi.dp_break(str(e))

    waiting_calls = int(agi.get_variable('QUEUE_WAITING_COUNT({})'.format(queue.name)))
    if _is_hold_time_overrun(agi, queue, waiting_calls):
        _set_diversion(agi, 'DIVERT_HOLDTIME', 'QWAITTIME')
    elif _is_agent_ratio_overrun(agi, queue, waiting_calls):
        _set_diversion(agi, 'DIVERT_CA_RATIO', 'QWAITRATIO')
    else:
        _set_diversion(agi, '', '')


def _is_hold_time_overrun(agi, queue, waiting_calls):
    if queue.waittime is None or waiting_calls == 0:
        return False

    holdtime = int(agi.get_variable('QUEUEHOLDTIME'))
    return holdtime > queue.waittime


def _is_agent_ratio_overrun(agi, queue, waiting_calls):
    if queue.waitratio is None or waiting_calls == 0:
        return False

    agents = int(agi.get_variable('QUEUE_MEMBER({},logged)'.format(queue.name)))
    if agents == 0:
        return True

    return (waiting_calls + 1.0) / agents > queue.waitratio


def _set_diversion(agi, event, dialaction):
    agi.set_variable('XIVO_DIVERT_EVENT', event)
    agi.set_variable('XIVO_FWD_TYPE', 'QUEUE_' + dialaction)


agid.register(check_diversion)
