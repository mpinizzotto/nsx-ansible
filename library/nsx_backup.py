
#!/usr/bin/env python
#coding=utf-8


def get_ftp_config(session):
    if session.read('applianceMgrBackupSettings')['body'] is not None:
        response = session.read('applianceMgrBackupSettings')['body']
        return response['backupRestoreSettings']['ftpSettings']
    else:
        return None

def get_schedule_config(session):
    if session.read('applianceMgrBackupSettings')['body'] is not None:
        response = session.read('applianceMgrBackupSettings')['body']
        try:
            return response['backupRestoreSettings']['backupFrequency']
        except:
            return None
    else:
        return None

def update_ftp_config(session, module):
    ftp_create_body = {'ftpSettings':
	                      {'userName': module.params['name'],
						   'passiveMode': 'true',
						   'useEPSV': 'true',
						   'password': module.params['password'],
						   'passPhrase': module.params['pass_phrase'],
						   'transferProtocol': module.params['transfer_protocol'],
						   'hostNameIPAddress': module.params['ip_addr'],
						   'backupDirectory': module.params['backup_directory'],
						   'filenamePrefix': module.params['file_name_prefix'],
						   'useEPRT': 'false',
						   'port': module.params['port']}
                      }
    return session.update('applianceMgrBackupSettingsFtp',
                           request_body_dict=ftp_create_body)['status']


def update_schedule_config(session, schedule):
    schedule_create_body = {'backupFrequency': schedule }
    return session.update('applianceMgrBackupSettingsSchedule',
                           request_body_dict=schedule_create_body)['status']


def normalize_schedule(backup_schedule): #pass in back_up module params

    
    if backup_schedule is not None:
        for item in backup_schedule:
            if not isinstance(item, dict):
                print 'schedule List {} is not a valid dictionary'.format(item)

            if item.get('frequency') == None:
                print  'Schedule List Entry {} in your list is missing the'\
                'mandatory \"frequency\" parameter'.format(item.get('frequency', None))

            else:
                item['frequency'] = str(item['frequency'])

            if item['frequency'] != item['frequency'].isupper():
                item['frequency'] = item['frequency'].upper()

            if item['frequency'] == 'HOURLY':
                if item.get('minuteOfHour', 'missing') == 'missing':
                        item['minuteOfHour'] = '0'
                else:
                    item['minuteOfHour'] = str(item['minuteOfHour'])

                schedule = { 'frequency': item['frequency'],
    		           'minuteOfHour': item['minuteOfHour'] }

            if item['frequency'] == 'DAILY':
                if item.get('hourOfDay', 'missing') == 'missing':
                    item['hourOfDay'] = '0'
                else:
                    item['hourOfDay'] = str(item['hourOfDay'])

                if item.get('minuteOfHour', 'missing') == 'missing':
                    item['minuteOfHour'] = '0'
                else:
                    item['minuteOfHour'] = str(item['minuteOfHour'])

                schedule = { 'frequency': item['frequency'],
    		           'minuteOfHour': item['minuteOfHour'],
    			 'hourOfDay': item['hourOfDay'] }

            if item['frequency'] == 'WEEKLY':
                if item.get('dayOfWeek', 'missing') == 'missing':
                    item['dayOfWeek'] = 'SUNDAY'
                else:
                    if item.get('dayOfWeek') != item.get('dayOfWeek').isupper():
                        item['dayOfWeek'] = str(item['dayOfWeek']).upper()

                if item.get('hourOfDay', 'missing') == 'missing':
                    item['hourOfDay'] = '0'
                else:
                    item['hourOfDay'] = str(item['hourOfDay'])

                if item.get('minuteOfHour', 'missing') == 'missing':
                    item['minuteOfHour'] = '0'
                else:
                    item['minuteOfHour'] = str(item['minuteOfHour'])

                schedule = { 'frequency': item['frequency'],
    		           'minuteOfHour': item['minuteOfHour'],
    			 'hourOfDay': item['hourOfDay'],
    			 'dayOfWeek': item['dayOfWeek'] }

        return True, None, schedule


def check_ftp(ftp_config, module):

    changed = False
    
    if ftp_config['userName'] == module.params['name']:
        changed = False     
    else:
        changed = True
        
    if ftp_config['transferProtocol'] == module.params['transfer_protocol']:
        changed = False
    else:
        changed = True
        
    if ftp_config['hostNameIPAddress'] == module.params['ip_addr']:
        changed = False
    else:
        changed = True
        
    if ftp_config['backupDirectory'] == module.params['backup_directory']:
        changed = False
    else:
        changed = True

    if ftp_config['filenamePrefix'] == module.params['file_name_prefix']:
        changed = False
    else:
        changed = True
    
    if module.params['password'] is not None:
        changed = True
    else:
	    changed = False
		
    if module.params['pass_phrase'] is not None:
        changed = True
    else:
        changed = False

    return changed

def check_schedule(schedule_config, schedule):

    changed = False
    if cmp(schedule_config, schedule) is not 0:
        changed = True
        return changed
    #for items in schedule:
    #    if schedule[items] != schedule_config[items]:
    #        changed = True
    #        return changed
    else:
        return changed


def delete_config(session):
    return session.delete('applianceMgrBackupSettings')
	
def delete_schedule(session):
    return session.delete('applianceMgrBackupSettingsSchedule')


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent']),
            nsxmanager_spec=dict(required=True, no_log=True, type='dict'),
            name=dict(required=True, type='str'),
            password=dict(required=True, no_log=True, type='str'),
            transfer_protocol=dict(default='FTP', choices=['FTP', 'SFTP']),
            ip_addr=dict(required=True, type='str'),
            port=dict(default='21', type='str'),
            backup_directory=dict(required=True, type='str'),
            file_name_prefix=dict(type='str'),
            pass_phrase=dict(required=True, no_log=True, type='str'),
            backup_schedule=dict(required=True, type='list'),
        ),
        supports_check_mode=False
    )

    from nsxramlclient.client import NsxClient
    import time

    session = NsxClient(module.params['nsxmanager_spec']['raml_file'], module.params['nsxmanager_spec']['host'],
                  module.params['nsxmanager_spec']['user'], module.params['nsxmanager_spec']['password'])
	
	
    #ftp_changed = False
    #schedule_changed = False
	#			  
    #ftp_config = get_ftp_config(session)
    #schedule_config = get_schedule_config(session)
	#
    #if ftp_config or schedule_config and module.params['state'] == 'absent':
    #    delete_config(session)
    #    ftp_changed = True
	#	schedule_changed = True
	#
	#if ftp_changed:
	#    module.exit_json(changed=True, ftp_config='1')
	#    
    #
    #if module.params['state'] == module.params['state'] 'absent' and ftp_config:
    #    delete_config(session)
    #    module.exit_json(changed=True, ftp_config='4')
    #
    #elif module.params['state'] == 'absent' and not ftp_config:
    #    module.exit_json(changed=False, ftp_config='3')
    # 
    #if module.params['state'] == 'present' and ftp_config:
    #    ftp_changed = check_ftp(ftp_config, module) #check if ftp changed
    #else:
    #    ftp_changed = True
    #
    #if schedule_config:
    #    valid, msg, schedule = normalize_schedule(module.params['backup_schedule']) #normalize list
    #    if not valid:
    #        module.fail_json(msg=msg)
    #
    #    schedule_changed = check_schedule(schedule_config, schedule) #compare config against normalized list is changed?
    #
    #if ftp_changed or schedule_changed:
    #    if ftp_changed:
	#	    delete_config(session)
    #        time.sleep(10)
    #        update_ftp_config(session, module)
	#    if schedule_changed:
    #        update_schedule_config(session, schedule)
    #
	#	module.exit_json(changed=True, ftp_config=ftp_config, schedule_config='1')
    #else:
    #    module.exit_json(changed=False, ftp_config=ftp_config, schedule_config='2')
    #
	#	
	#	
	#	
	#---------------------------------------------	
		
    ftp_changed = False
    schedule_changed = False

    ftp_config = get_ftp_config(session)
    schedule_config = get_schedule_config(session)

    if ftp_config and module.params['state'] == 'absent':
        delete_config(session)
        module.exit_json(changed=True, ftp_config='1')
	
	if not ftp_config and module.params['state'] == 'absent':
	    module.exit_json(changed=True, ftp_config='2')

    if not ftp_config and module.params['state'] == 'present':
        update_ftp_config(session, module)
        ftp_changed = True
     
    if not schedule_config and module.params['state'] == 'present':
        valid, msg, schedule = normalize_schedule(module.params['backup_schedule']) #normalize list
        if not valid:
            module.fail_json(msg=msg) 
        update_schedule_config(session, schedule)
        schedule_changed = True
		
    if ftp_config:
        ftp_settings_changed = check_ftp(ftp_config, module) #check if ftp changed
        if ftp_settings_changed:
            update_ftp_config(session, module)
            ftp_changed = True


    if schedule_config:
        valid, msg, schedule = normalize_schedule(module.params['backup_schedule']) #normalize list
        if not valid:
            module.fail_json(msg=msg)
        schedule_settings_changed = check_schedule(schedule_config, schedule) #compare config against normalized list is changed?
        if schedule_settings_changed:
            delete_schedule(session)        
            update_schedule_config(session, schedule)
            schedule_changed = True

    if ftp_changed or schedule_changed:
        module.exit_json(changed=True, ftp_config='3')
    else:
        module.exit_json(changed=False, ftp_config='4')


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()

