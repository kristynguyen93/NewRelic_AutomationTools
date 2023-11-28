import requests
import csv
from datetime import date



# accountId and user api_key can be updated

accountId = "967232"
api_key =  "NRAK-GAQGNZ29C2H7G5HBT4636J3HZY9"
graphql_url = 'https://api.newrelic.com/graphql'
headers = {
    'Content-Type': 'application/json',
    'API-Key': api_key
}

def entities_filename():
    file_name = "missing_entities_deployment-"+str(date.today())+".csv"

    return file_name

def find_all_entities():

    all_entities_list = []

    graphql_query = '''
        {
          actor {
            entitySearch(query: "domain ='APM' AND accountId = ''' + accountId + '''") {
              count
              query
              results {
                entities {
                  guid
                  name
                  accountId
                  domain
                }
                nextCursor
              }
            }
          }
        }
    '''

    response = requests.post(graphql_url, headers=headers, json={'query': graphql_query})
    response_json = response.json()

    next_cursor = response_json["data"]["actor"]["entitySearch"]["results"]["nextCursor"]
    result_entities = response_json["data"]["actor"]["entitySearch"]["results"]["entities"]

    for entity in result_entities:
        entity_name = entity["name"]
        entity_guid = entity["guid"]

        all_entities_list.append({"entity_name": entity_name, "entity_guid": entity_guid})

    while next_cursor is not None:
        graphql_query = '''
            {
              actor {
                entitySearch(query: "domain ='APM' AND accountId = ''' + accountId + '''") {
                  count
                  query
                  results(cursor: "''' + next_cursor + '''") {
                    entities {
                      guid
                      name
                      accountId
                      domain
                    }
                    nextCursor
                  }
                }
              }
            }
        '''

        response = requests.post(graphql_url, headers=headers, json={'query': graphql_query})
        response_json = response.json()

        next_cursor = response_json["data"]["actor"]["entitySearch"]["results"]["nextCursor"]
        result_entities = response_json["data"]["actor"]["entitySearch"]["results"]["entities"]

        for entity in result_entities:
            entity_name = entity["name"]
            entity_guid = entity["guid"]

            all_entities_list.append({"entity_name": entity_name, "entity_guid": entity_guid})

    return all_entities_list

def find_deployment_entities():

    graphql_query = '''
        {
          actor {
            nrql(
              query: "SELECT uniques(entity.guid) FROM Deployment SINCE 1 MONTH AGO"
              accounts: ''' + accountId + '''
            ) {
              results
            }
          }
        }
    '''

    response = requests.post(graphql_url, headers=headers, json={'query': graphql_query})
    response_json = response.json()

    deployment_entities = response_json["data"]["actor"]["nrql"]["results"][0]["uniques.entity.guid"]

    return deployment_entities

def find_entities_not_reporting_deployment():

    all_entities_list = find_all_entities()
    deployment_entities = find_deployment_entities()

    print(len(all_entities_list))
    print(len(deployment_entities))

    entities_not_reporting_list = []

    for entity in all_entities_list:
        if entity["entity_guid"] not in deployment_entities:
            print(entity["entity_guid"])
            entities_not_reporting_list.append(entity["entity_guid"])

    result_list = []

    for entity_guid in entities_not_reporting_list:
        for entity in all_entities_list:
            if entity["entity_guid"] == entity_guid:
                result_list.append(entity)

    print(result_list)
    print(len(result_list))

    with open(entities_filename(), 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=result_list[0].keys())
        writer.writeheader()
        writer.writerows(result_list)



# find_entities_not_reporting_deployment()
