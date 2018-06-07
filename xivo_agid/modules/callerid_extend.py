# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_agid import agid


def callerid_extend(agi, cursor, args):
    if 'agi_callington' in agi.env:
        agi.set_variable('XIVO_SRCTON', agi.env['agi_callington'])


agid.register(callerid_extend)
