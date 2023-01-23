import sys
import argparse
import requests
import json
import datetime
import time



def post_request(url, headers, json):

    if len(url) and len(headers):
        response = requests.post(url=url, headers=headers, json=json)
        if (response.status_code != 200) and (response.status_code != 201):
            print('POST request fail!\n')
            print(response.status_code)
            print(response.json())
            response.raise_for_status()        
        else:
            return response.json()
        
        
        
def get_request(url, headers):

    if len(url) and len(headers):
        response = requests.get(url=url, headers=headers)
        if response.status_code != 200:
            print('GET request fail!\n')
            print(response.status_code)
            print(response.json())
            response.raise_for_status()        
        else:
            return response.json()
        
        
        
def put_request(url, headers, json):
    
    if len(url) and len(headers):
        response = requests.put(url=url, headers=headers, json=json)
        if response.status_code != 200:
            print('PUT request fail!\n')
            print(response.status_code)
            print(response.json())
            response.raise_for_status()        
        else:
            return response.json()
        
        
        
def get_available_ke_types(url, headers):
    
    full_url = url + '/api/public/sm/v2/rsm/config-item-types'
    data = get_request(url=full_url, headers=headers)
    
    return data
        
        
        
def get_available_workgroups(url, headers):
    
    full_url = url + '/api/public/sm/v2/rsm/work-groups'
    data = get_request(url=full_url, headers=headers)
    
    return data



def create_ke(url, headers, ke_parametrs):
    
    full_url = url + '/api/public/sm/v2/rsm/config-items?makeNameUnique=false'
    
    payload = {
                "name": ke_parametrs['ke_name'], 
                "description": ke_parametrs['ke_description'],
                "parent": { "id": 0 },
                "configItemType": { "id": ke_parametrs['ke_type_id'] },
                "ownerWorkGroup": { "id": ke_parametrs['owner_work_group_id'] },
                "labels": ke_parametrs['labels'],
                "sharedToWorkGroups": [ { "workGroupId": 0 } ] 
              }
    
    data = post_request(url=full_url, headers=headers, json=payload)
    if data is None or (data['configItemType']['id'] != ke_parametrs['ke_type_id'] ):
        print('Create KE failed!\n')
        exit(0)
    else:
        ke_parametrs['ke_id'] = data['id']
        print('Create KE successfully!\n')
        


def change_ke_type(url, headers, ke_parametrs):
    
    ### Получение id определенного типа КЕ по имени
    get_id_ke_type_by_name(url=url, headers=headers, ke_parametrs=ke_parametrs)
        
    full_url = url + '/api/public/sm/v2/rsm/config-items/'+ str(ke_parametrs['ke_id']) + '?makeNameUnique=false'
    payload = {
                "name": ke_parametrs['ke_name'],
                "description": ke_parametrs['ke_description'],
                "configItemType": { "id": ke_parametrs['ke_type_id'] },
                "ownerWorkGroup": { "id": ke_parametrs['owner_work_group_id'] },
                "labels": ke_parametrs['labels']
              }
    
    data = put_request(url=full_url, headers=headers, json=payload)        
    if data is None or (data['configItemType']['id'] != ke_parametrs['ke_type_id']):
        print('Change KE failed!\n')
        exit(0)
    else:
        print('Change KE successfully!\n')



def create_service_mode_for_ke(url, headers, ke_parametrs, service_mode_parametrs):
    
    full_url = url + '/api/public/sm/v1/rsm-maintenance'
    payload = {
                "dateStart": service_mode_parametrs['date_start'],
                "dateEnd": service_mode_parametrs['date_end'],
                "title": service_mode_parametrs['title'],
                "configItems": [ { "id": ke_parametrs['ke_id'], "scope": "CiAndChildren"} ]   
              }
    
    data = post_request(url=full_url, headers=headers, json=payload)
    if data is None or (data['configItems'][0]['id'] != ke_parametrs['ke_id']):
        print('Creating a service mode for KE failed!\n')
        exit(0)
    else:
        print('Creating a service mode for KE successfully!\n')
           
           
        
def search_for_id_by_name(name, json_data):
    
    element_id = None
    for element in json_data:
        if element['name'] == name:
            element_id = element['id']
            break
            
    return element_id



def get_id_by_name(name, func, *args):
    
    id_for_name = None
    
    data = func(*args)
    if data is None:
        print('Get data from REST API!\n')
        exit(0)
    
    id_for_name = search_for_id_by_name(name=name, json_data=data)
    
    return id_for_name
    
    
    
def get_id_ke_type_by_name(url, headers, ke_parametrs):
    
    ke_parametrs['ke_type_id'] = get_id_by_name(ke_parametrs['ke_type_name'], get_available_ke_types, url, headers)
    if ke_parametrs['ke_type_id'] is None:
        print('Get for KE type id named ' + ke_parametrs['ke_type_name'] + ' failed!\n')
        exit(0)
    else:
        print('Get for KE type id named ' + ke_parametrs['ke_type_name'] + ' successfully!\n')
    
    
    
def get_id_workgroup_by_name(url, headers, ke_parametrs):
    
    ke_parametrs['owner_work_group_id'] = get_id_by_name(ke_parametrs['owner_work_group'], get_available_workgroups, url, headers)
    if ke_parametrs['owner_work_group_id'] is None:
        print('Get workgroup id for owner failed!\n')
        exit(0)
    else:
        print('Get workgroup id for owner successfully!\n')    



def createParser():
    parser = argparse.ArgumentParser( 
               prog = 'Script rest_api_request 0.0.1',
               description = ''' Это скрипт делает запросы к REST API.''',
               epilog = ''' (c) Vladimir   January 2023.   Автор скрипта не несёт никакой ответственности за последствия его использования. '''   
                                    )
                                    
    parser.add_argument('-u', '--url', required=True, help = 'Url ссылка сервера REST API.')
    parser.add_argument('-a', '--authentication_token', required=True, help = 'Токен аутентификации от аккаунта на серверe REST API.')
    parser.add_argument('-o', '--owner_work_group', required=True, help = 'Рабочая группа-владелец.')
    
    return parser
    


def main():
    try:
        
        parser = createParser()
        namespace_args = parser.parse_args(sys.argv[1:])
        
        headers = {
                    'Authorization': 'Bearer ' + namespace_args.authentication_token,
                    'accept' : 'application/json',
                    'Content-Type' : 'application/json'
                  }
        
        url = namespace_args.url
        
        ke_parametrs = {
                         'ke_id' : None,
                         'ke_type_id' : None,
                         'ke_type_name': 'Router',
                         'ke_name' : None,
                         'ke_description' : None,
                         'labels' : None,
                         'owner_work_group_id' : None,
                         'owner_work_group' : namespace_args.owner_work_group
                       }
        
        # Получение доступных типов КЕ 
        
        data = get_available_ke_types(url=url, headers=headers)
        if data is None:
            print('Get available KE types failed!\n')
            exit(0)
        else:
            print('Get available KE types successfully!\n')
            
        ################################
        
        # Создание KE
        
        ### Получение id определенного типа КЕ по имени
        ke_parametrs['ke_type_id'] = search_for_id_by_name(name=ke_parametrs['ke_type_name'], json_data=data)
        if ke_parametrs['ke_type_id'] is None:
            print('Lookup for KE type id named ' + ke_parametrs['ke_type_name'] + ' failed!\n')
            exit(0)
        else:
            print('Lookup for KE type id named ' + ke_parametrs['ke_type_name'] + ' successfully!\n')
            
        
        ### Получение id определенной рабочей группы-владельца по имени
        get_id_workgroup_by_name(url=url, headers=headers, ke_parametrs=ke_parametrs)
                
        ke_parametrs['ke_name'] = "Test_task_five"
        ke_parametrs['ke_description'] = "Тестовая_задача_номер_5"
        ke_parametrs['labels'] = { 'source_name' : 'Тестовое задание' }
        
        create_ke(url=url, headers=headers, ke_parametrs=ke_parametrs)
        
        ####################################
        
        
        # Изменить тип КЕ
        
        ke_parametrs['ke_type_name'] = 'Switch'
        change_ke_type(url=url, headers=headers, ke_parametrs=ke_parametrs)
        
        ##########################################
        
        
        # Создание сервисного режима для КЕ
        
        todays_datetime = datetime.datetime.now() 
        service_mode_parametrs = {
                                   'date_start' : todays_datetime.astimezone().isoformat('T', 'seconds'),
                                   'date_end' : todays_datetime.replace(month=(todays_datetime.month + 1)).astimezone().isoformat('T', 'seconds'),
                                   'title' : 'Test_task_five_service_mode'
                                 }
        
        create_service_mode_for_ke(url=url, headers=headers, ke_parametrs=ke_parametrs, service_mode_parametrs=service_mode_parametrs)
        
        ##########################################
        
    except json.JSONDecodeError as exception:
        print('exception json.JSONDecodeError', exception.msg)
    except requests.HTTPError as exception:
        print('exception requests.HTTPError', exception)
    else:
        print('Successful script execution!')


if __name__ == "__main__":                        
    main()
