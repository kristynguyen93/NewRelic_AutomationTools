import requests
import csv
import logging
from datetime import date
from shared import CsvFunctions as csv
from shared import NerdGraph

logging.basicConfig(filename='logs.log', level=logging.INFO)


def get_entities_filename():
    file_name = csv.output_files() + "missing_entities_deployment-"+str(date.today())+".csv"

    return file_name


def find_all_entities():

    all_entities_list = []

    next_cursor = None

    graphql_query = """
        {
          actor {
            entitySearch(query: "domain ='APM' AND accountId = %s") {
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
    """ % (NerdGraph.accountId)


    response = requests.post(NerdGraph.graphql_url, headers=NerdGraph.headers, json={'query': graphql_query})
    response_json = response.json()
    next_cursor = response_json["data"]["actor"]["entitySearch"]["results"]["nextCursor"]
    result_entities = response_json["data"]["actor"]["entitySearch"]["results"]["entities"]

    for entity in result_entities:
        entity_name = entity["name"]
        entity_guid = entity["guid"]

        all_entities_list.append({"entity_name": entity_name, "entity_guid": entity_guid})

    while next_cursor is not None:
        graphql_query = """
            {
              actor {
                entitySearch(query: "domain ='APM' AND accountId = %s") {
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
        """ % (NerdGraph.accountId)

        response = requests.post(NerdGraph.graphql_url, headers=NerdGraph.headers, json={'query': graphql_query})
        response_json = response.json()

        next_cursor = response_json["data"]["actor"]["entitySearch"]["results"]["nextCursor"]
        result_entities = response_json["data"]["actor"]["entitySearch"]["results"]["entities"]

        for entity in result_entities:
            entity_name = entity["name"]
            entity_guid = entity["guid"]

            all_entities_list.append({"entity_name": entity_name, "entity_guid": entity_guid})

    return all_entities_list


def find_deployment_entities():

    query_variables = {
        "account_id": NerdGraph.accountId
    }

    graphql_query = """
        query ($account_id:Int!) {
          actor {
            nrql(
              query: "SELECT uniques(entity.guid) FROM Deployment SINCE 1 MONTH AGO"
              accounts: $account_id
            ) {
              results
            }
          }
        }
    """

    response = requests.post(NerdGraph.graphql_url, headers=NerdGraph.headers, json={'query': graphql_query, 'variables': query_variables})
    response_json = response.json()

    deployment_entities = response_json["data"]["actor"]["nrql"]["results"][0]["uniques.entity.guid"]

    return deployment_entities


def find_entities_not_reporting_deployment():

    all_entities_list = find_all_entities()
    deployment_entities = find_deployment_entities()
    entities_not_reporting_list = []

    for entity in all_entities_list:
        if entity["entity_guid"] not in deployment_entities:
            entities_not_reporting_list.append(entity["entity_guid"])

    result_list = []

    for entity_guid in entities_not_reporting_list:
        for entity in all_entities_list:
            if entity["entity_guid"] == entity_guid:
                result_list.append(entity)

    file_name = get_entities_filename()

    logging.info("Writing entities not reporting deployment report to CSV file.")
    csv.write_list_of_dicts_to_csv(result_list, file_name)