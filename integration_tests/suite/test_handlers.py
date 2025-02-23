# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from hamcrest import assert_that, calling, raises
from .helpers.base import IntegrationTest, use_asset
from .helpers.agid import AGIFailException


@use_asset('base')
class TestHandlers(IntegrationTest):
    def test_monitoring(self):
        recv_vars, recv_cmds = self.agid.monitoring()
        assert recv_cmds['Status'] == 'OK'

    def test_incoming_user_set_features_with_dstid(self):
        with self.db.queries() as queries:
            sip = queries.insert_endpoint_sip()
            user, line, extension = queries.insert_user_line_extension(
                firstname='Firstname',
                lastname='Lastname',
                exten='1801',
                endpoint_sip_uuid=sip['uuid'],
            )

        variables = {
            'XIVO_USERID': user['id'],
            'XIVO_DSTID': user['id'],
            'XIVO_DST_EXTEN_ID': extension['id'],
            'XIVO_CALLORIGIN': 'patate',
            'XIVO_SRCNUM': extension['exten'],
            'XIVO_DSTNUM': 1800,
            'XIVO_BASE_CONTEXT': extension['context'],
            'WAZO_USER_MOH_UUID': '',
            'WAZO_CALL_RECORD_ACTIVE': '0',
            'XIVO_FROMGROUP': '0',
            'XIVO_PATH': '',
            f'PJSIP_ENDPOINT({line["name"]},webrtc)': 'no',
            f'PJSIP_DIAL_CONTACTS({line["name"]})': 'contact',
            'CHANNEL(videonativeformat)': '1',
        }
        recv_vars, recv_cmds = self.agid.incoming_user_set_features(variables)

        assert recv_cmds['FAILURE'] is False

        assert recv_vars['XIVO_DST_USERNUM'] == extension['exten']
        assert recv_vars['WAZO_DST_USER_CONTEXT'] == extension['context']
        assert recv_vars['WAZO_DST_NAME'] == 'Firstname Lastname'
        assert recv_vars['XIVO_DST_REDIRECTING_NAME'] == 'Firstname Lastname'
        assert recv_vars['XIVO_DST_REDIRECTING_NUM'] == extension['exten']
        assert recv_vars['WAZO_DST_UUID'] == user['uuid']
        assert recv_vars['WAZO_DST_TENANT_UUID'] == user['tenant_uuid']
        assert recv_vars['XIVO_INTERFACE'] == 'contact'
        assert recv_vars['XIVO_CALLOPTIONS'] == ''
        assert recv_vars['XIVO_SIMULTCALLS'] == str(user['simultcalls'])
        assert recv_vars['XIVO_RINGSECONDS'] == str(user['ringseconds'])
        assert recv_vars['XIVO_ENABLEDND'] == str(user['enablednd'])
        assert recv_vars['XIVO_ENABLEVOICEMAIL'] == str(user['enablevoicemail'])
        assert recv_vars['XIVO_MAILBOX'] == ''
        assert recv_vars['XIVO_MAILBOX_CONTEXT'] == ''
        assert recv_vars['XIVO_USEREMAIL'] == ''
        assert recv_vars['XIVO_ENABLEUNC'] == str(user['enableunc'])
        assert recv_vars['XIVO_FWD_USER_UNC_ACTION'] == 'none'
        assert recv_vars['XIVO_FWD_USER_UNC_ACTIONARG1'] == ''
        assert recv_vars['XIVO_FWD_USER_UNC_ACTIONARG2'] == ''
        assert recv_vars['XIVO_FWD_USER_BUSY_ACTION'] == 'none'
        assert recv_vars['XIVO_FWD_USER_BUSY_ISDA'] == '1'
        assert recv_vars['XIVO_FWD_USER_BUSY_ACTIONARG1'] == ''
        assert recv_vars['XIVO_FWD_USER_BUSY_ACTIONARG2'] == ''
        assert recv_vars['XIVO_FWD_USER_NOANSWER_ACTION'] == 'none'
        assert recv_vars['XIVO_FWD_USER_NOANSWER_ISDA'] == '1'
        assert recv_vars['XIVO_FWD_USER_NOANSWER_ACTIONARG1'] == ''
        assert recv_vars['XIVO_FWD_USER_NOANSWER_ACTIONARG2'] == ''
        assert recv_vars['XIVO_FWD_USER_CONGESTION_ACTION'] == 'none'
        assert recv_vars['XIVO_FWD_USER_CONGESTION_ISDA'] == '1'
        assert recv_vars['XIVO_FWD_USER_CONGESTION_ACTIONARG1'] == ''
        assert recv_vars['XIVO_FWD_USER_CONGESTION_ACTIONARG2'] == ''
        assert recv_vars['XIVO_FWD_USER_CHANUNAVAIL_ACTION'] == 'none'
        assert recv_vars['XIVO_FWD_USER_CHANUNAVAIL_ISDA'] == '1'
        assert recv_vars['XIVO_FWD_USER_CHANUNAVAIL_ACTIONARG1'] == ''
        assert recv_vars['XIVO_FWD_USER_CHANUNAVAIL_ACTIONARG2'] == ''
        assert recv_vars['CHANNEL(musicclass)'] == user['musiconhold']
        assert recv_vars['WAZO_CALL_RECORD_SIDE'] == 'caller'
        assert recv_vars['XIVO_USERPREPROCESS_SUBROUTINE'] == ''
        assert recv_vars['XIVO_MOBILEPHONENUMBER'] == ''
        assert recv_vars['WAZO_VIDEO_ENABLED'] == '1'
        assert recv_vars['XIVO_PATH'] == 'user'
        assert recv_vars['XIVO_PATH_ID'] == str(user['id'])

    def test_agent_get_options(self):
        with self.db.queries() as queries:
            agent = queries.insert_agent()

        recv_vars, recv_cmds = self.agid.agent_get_options(
            agent['tenant_uuid'],
            agent['number'],
        )

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_AGENTEXISTS'] == '1'
        assert recv_vars['XIVO_AGENTPASSWD'] == ''
        assert recv_vars['XIVO_AGENTID'] == str(agent['id'])
        assert recv_vars['XIVO_AGENTNUM'] == agent['number']
        assert recv_vars['CHANNEL(language)'] == agent['language']

    @pytest.mark.skip('NotImplemented: need agentd mock')
    def test_agent_get_status(self):
        with self.db.queries() as queries:
            agent = queries.insert_agent()

        recv_vars, recv_cmds = self.agid.agent_get_status(
            agent['tenant_uuid'],
            agent['id'],
        )

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_AGENT_LOGIN_STATUS'] == 'logged_in'

    @pytest.mark.skip('NotImplemented: need agentd mock')
    def test_agent_login(self):
        with self.db.queries() as queries:
            agent = queries.insert_agent()
            extension = queries.insert_extension()

        recv_vars, recv_cmds = self.agid.agent_login(
            agent['tenant_uuid'],
            agent['id'],
            extension['exten'],
            extension['context'],
        )

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_AGENTSTATUS'] == 'logged'

    @pytest.mark.skip('NotImplemented: need agentd mock')
    def test_agent_logoff(self):
        with self.db.queries() as queries:
            agent = queries.insert_agent()

        recv_vars, recv_cmds = self.agid.agent_logoff(
            agent['tenant_uuid'],
            agent['id'],
        )

        assert recv_cmds['FAILURE'] is False

    @pytest.mark.skip('NotImplemented: need to verify file on filesystem')
    def test_callback(self):
        pass

    def test_callerid_extend(self):
        recv_vars, recv_cmds = self.agid.callerid_extend('en')

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_SRCTON'] == 'en'

    def test_callerid_forphones_without_reverse_lookup(self):
        recv_vars, recv_cmds = self.agid.callerid_forphones(
            calleridname='name',
            callerid='numero',
        )

        assert recv_cmds['FAILURE'] is False

    @pytest.mark.skip('NotImplemented')
    def test_callfilter(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_call_recording(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_check_diversion(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_check_schedule(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_convert_pre_dial_handler(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_fwdundoall(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_getring(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_get_user_interfaces(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_group_answered_call(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_group_member(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_handler_fax(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_in_callerid(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_incoming_agent_set_features(self):
        pass

    def test_incoming_conference_set_features(self):
        name = u'My Conférence'
        with self.db.queries() as queries:
            conference = queries.insert_conference(name=name)

        variables = {
            'XIVO_DSTID': conference['id'],
        }
        recv_vars, recv_cmds = self.agid.incoming_conference_set_features(variables)

        bridge_profile = 'xivo-bridge-profile-{}'.format(conference['id'])
        user_profile = 'xivo-user-profile-{}'.format(conference['id'])
        assert recv_cmds['FAILURE'] is False
        assert recv_vars['WAZO_CONFBRIDGE_ID'] == str(conference['id'])
        assert recv_vars['WAZO_CONFBRIDGE_TENANT_UUID'] == conference['tenant_uuid']
        assert recv_vars['WAZO_CONFBRIDGE_BRIDGE_PROFILE'] == bridge_profile
        assert recv_vars['WAZO_CONFBRIDGE_USER_PROFILE'] == user_profile
        assert recv_vars['WAZO_CONFBRIDGE_MENU'] == 'xivo-default-user-menu'
        assert recv_vars['WAZO_CONFBRIDGE_PREPROCESS_SUBROUTINE'] == ''
        assert recv_cmds['EXEC CELGenUserEvent'] == 'WAZO_CONFERENCE, NAME: {}'.format(name)

    @pytest.mark.skip('NotImplemented')
    def test_incoming_did_set_features(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_incoming_group_set_features(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_incoming_queue_set_features(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_outgoing_user_set_features(self):
        pass

    def test_meeting_user(self):
        with self.db.queries() as queries:
            meeting = queries.insert_meeting()

        variables = {
            'WAZO_TENANT_UUID': meeting['tenant_uuid'],
        }

        # Lookup by UUID
        recv_vars, recv_cmds = self.agid.meeting_user(
            variables, 'wazo-meeting-{uuid}'.format(**meeting),
        )

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['WAZO_MEETING_NAME'] == meeting['name']
        assert recv_vars['WAZO_MEETING_UUID'] == meeting['uuid']

        # Lookup by number
        recv_vars, recv_cmds = self.agid.meeting_user(
            variables, meeting['number'],
        )

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['WAZO_MEETING_NAME'] == meeting['name']
        assert recv_vars['WAZO_MEETING_UUID'] == meeting['uuid']

    @pytest.mark.skip('NotImplemented')
    def test_paging(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_phone_get_features(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_phone_progfunckey_devstate(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_phone_progfunckey(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_provision(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_queue_answered_call(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_queue_skill_rule_set(self):
        pass

    def test_switchboard_set_features_no_switchboard(self):
        assert_that(
            calling(self.agid.switchboard_set_features).with_args('switchboard-not-found'),
            raises(AGIFailException)
        )

    def test_switchboard_set_features_fallback_no_fallback(self):
        with self.db.queries() as queries:
            switchboard = queries.insert_switchboard()

        recv_vars, recv_cmds = self.agid.switchboard_set_features(switchboard['uuid'])

        assert recv_cmds['FAILURE'] is False
        # resetting those variables is important when chaining switcbhoard forwards
        assert recv_vars['WAZO_SWITCHBOARD_FALLBACK_NOANSWER_ACTION'] == ''
        assert recv_vars['WAZO_SWITCHBOARD_FALLBACK_NOANSWER_ACTIONARG1'] == ''
        assert recv_vars['WAZO_SWITCHBOARD_FALLBACK_NOANSWER_ACTIONARG2'] == ''

    def test_switchboard_set_features_with_fallback(self):
        with self.db.queries() as queries:
            fallbacks = {
                'noanswer': {'event': 'noanswer', 'action': 'user', 'actionarg1': '1', 'actionarg2': '2'}
            }
            switchboard = queries.insert_switchboard(fallbacks=fallbacks)

        recv_vars, recv_cmds = self.agid.switchboard_set_features(switchboard['uuid'])

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['WAZO_SWITCHBOARD_FALLBACK_NOANSWER_ACTION'] == 'user'
        assert recv_vars['WAZO_SWITCHBOARD_FALLBACK_NOANSWER_ACTIONARG1'] == '1'
        assert recv_vars['WAZO_SWITCHBOARD_FALLBACK_NOANSWER_ACTIONARG2'] == '2'
        assert recv_vars['WAZO_SWITCHBOARD_TIMEOUT'] == ''

    def test_switchboard_set_features_with_timeout(self):
        with self.db.queries() as queries:
            switchboard = queries.insert_switchboard(timeout=42)

        recv_vars, recv_cmds = self.agid.switchboard_set_features(switchboard['uuid'])

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['WAZO_SWITCHBOARD_TIMEOUT'] == '42'

    @pytest.mark.skip('NotImplemented')
    def test_user_get_vmbox(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_user_set_call_rights(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_vmbox_get_info(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_wake_mobile(self):
        pass
