"""

This script generates a report of all policies and conditions in an account.
This script will output 3 CSV files in the 'output' folder:
    1. policies_and_conditions_report.csv - This file contains all policies and conditions in an account.
    2. invalid_policies_report.csv - This file contains all policies that are invalid.
    3. empty_policies_report.csv - This file contains all policies that are empty.

"""

import os
import logging
import requests
from datetime import date
import shared.CsvFunctions as csv
import shared.NerdGraph as NerdGraph

logging.basicConfig(filename='logs.log', level=logging.INFO)

def get_report_file_names():

    policies_and_conditions_report_filename = csv.output_files() + "policies_and_conditions_report-"+str(date.today())+".csv"
    invalid_policies_report_filename = csv.output_files() + "invalid_policies_report-"+str(date.today())+".csv"
    empty_policies_report_filename =  csv.output_files() + "empty_policies_report-"+str(date.today())+".csv"

    return policies_and_conditions_report_filename, invalid_policies_report_filename, empty_policies_report_filename


def get_all_policies():
    query_variables = {
        "account_id": NerdGraph.accountId
    }

    all_policies_list = []

    next_cursor = None

    graphql_query = """
                query ($account_id:Int!) {
                  actor {
                    account(id: $account_id) {
                      alerts {
                        policiesSearch {
                          policies {
                            id
                            name
                          }
                          nextCursor
                          totalCount
                        }
                      }
                    }
                  }
                }
                """
    response = requests.post(NerdGraph.graphql_url, headers=NerdGraph.headers, json={'query': graphql_query, 'variables': query_variables})
    response_json = response.json()
    if response_json["errors"]:
        logging.error("Error retrieving all policies: " + str(response_json["errors"]))
        print("Error retrieving all policies. See logs.log for details.")
        exit()
    next_cursor = response_json["data"]["actor"]["account"]["alerts"]["policiesSearch"]["nextCursor"]
    result_policies = response_json["data"]["actor"]["account"]["alerts"]["policiesSearch"]["policies"]

    for policy in result_policies:
        policy_id = policy["id"]
        policy_name = policy["name"]

        all_policies_list.append({"policy_id": policy_id, "policy_name": policy_name})

    while next_cursor is not None:

        graphql_query = """
            query ($account_id:Int!) {
              actor {
                account(id: $account_id) {
                  alerts {
                    policiesSearch(cursor: "%s") {
                      policies {
                        id
                        name
                      }
                      nextCursor
                      totalCount
                    }
                  }
                }
              }
            }
            """ % (next_cursor)

        response = requests.post(NerdGraph.graphql_url, headers=NerdGraph.headers, json={'query': graphql_query, 'variables': query_variables})
        response_json = response.json()
        if response_json["errors"]:
            logging.error("Error retrieving all policies: " + str(response_json["errors"]))
            print("Error retrieving all policies. See logs.log for details.")
            exit()
        next_cursor = response_json["data"]["actor"]["account"]["alerts"]["policiesSearch"]["nextCursor"]
        result_policies = response_json["data"]["actor"]["account"]["alerts"]["policiesSearch"]["policies"]

        for policy in result_policies:
            policy_id = policy["id"]
            policy_name = policy["name"]

            all_policies_list.append({"policy_id": policy_id, "policy_name": policy_name})

    logging.info("All policy IDs and names have been retrieved. Total number of policies: " + str(len(all_policies_list)))

    return all_policies_list


def get_policy_conditions(policy_id, policy_name):
    query_variables = {
        "account_id": NerdGraph.accountId,
        "policy_id": policy_id
    }

    conditions_list = []
    invalid_policy_list = []
    empty_policy_list = []

    next_cursor = None

    graphql_query = """
        query ($account_id: Int!, $policy_id: ID) {
          actor {
            account(id: $account_id) {
              alerts {
                nrqlConditionsSearch(searchCriteria: {policyId: $policy_id}) {
                  nextCursor
                  nrqlConditions {
                    enabled
                    name
                    id
                    nrql {
                      query
                    }
                  }
                }
              }
            }
          }
        }
        """
    response = requests.post(NerdGraph.graphql_url, headers=NerdGraph.headers, json={'query': graphql_query, 'variables': query_variables})
    response_json = response.json()
    if response_json["errors"]:
        logging.error("Error retrieving all policies: " + str(response_json["errors"]))
        print("Error retrieving all policies. See logs.log for details.")
        exit()
    if response_json["data"]["actor"]["account"]["alerts"]["nrqlConditionsSearch"] is not None:
        next_cursor = response_json["data"]["actor"]["account"]["alerts"]["nrqlConditionsSearch"]["nextCursor"]
        if not response_json["data"]["actor"]["account"]["alerts"]["nrqlConditionsSearch"]["nrqlConditions"]:
            logging.info("EMPTY POLICY: " + "Policy ID: " + str(policy_id) + " Policy Name: " + str(policy_name))
            empty_policy_list.append({"policy_id": policy_id, "policy_name": policy_name})
            return conditions_list, invalid_policy_list, empty_policy_list
        else:
            logging.info("Policy ID: " + str(policy_id) + " Policy Name: " + str(policy_name) + " has conditions.")
            result_condition_list = response_json["data"]["actor"]["account"]["alerts"]["nrqlConditionsSearch"]["nrqlConditions"]
    else:
        logging.info("INVALID POLICY: " + "Policy ID: " + str(policy_id) + " Policy Name: " + str(policy_name))
        invalid_policy_list.append({"policy_id": policy_id, "policy_name": policy_name})
        return conditions_list, invalid_policy_list, empty_policy_list


    for condition in result_condition_list:
        condition_name = condition["name"]
        condition_id = condition["id"]
        condition_query = condition["nrql"]["query"]
        condition_enabled = condition["enabled"]

        conditions_list.append({"policy_id": policy_id, "policy_name": policy_name , "condition_id": condition_id, "condition_name": condition_name, "condition_query": condition_query, "condition_enabled": condition_enabled})

    while next_cursor is not None:

        graphql_query = """
            query ($account_id: Int!, $policy_id: ID) {
              actor {
                account(id: $account_id) {
                  alerts {
                    nrqlConditionsSearch(searchCriteria: {policyId: $policy_id}, cursor: "%s") {
                      nextCursor
                      nrqlConditions {
                        enabled
                        name
                        id
                        nrql {
                          query
                        }
                      }
                    }
                  }
                }
              }
            }
            """ % (next_cursor)

        response = requests.post(NerdGraph.graphql_url, headers=NerdGraph.headers, json={'query': graphql_query, 'variables': query_variables})
        response_json = response.json()
        if response_json["errors"]:
            logging.error("Error retrieving all policies: " + str(response_json["errors"]))
            print("Error retrieving all policies. See logs.log for details.")
            exit()
        if response_json["data"]["actor"]["account"]["alerts"]["nrqlConditionsSearch"] is not None:
            next_cursor = response_json["data"]["actor"]["account"]["alerts"]["nrqlConditionsSearch"]["nextCursor"]
            if not response_json["data"]["actor"]["account"]["alerts"]["nrqlConditionsSearch"]["nrqlConditions"]:
                logging.info("EMPTY POLICY: " + "Policy ID: " + str(policy_id) + " Policy Name: " + str(policy_name))
                empty_policy_list.append({"policy_id": policy_id, "policy_name": policy_name})
                return conditions_list, invalid_policy_list, empty_policy_list
            else:
                logging.info("Policy ID: " + str(policy_id) + " Policy Name: " + str(policy_name) + " has conditions.")
                result_condition_list = response_json["data"]["actor"]["account"]["alerts"]["nrqlConditionsSearch"]["nrqlConditions"]
        else:
            logging.info("EMPTY POLICY: " + "Policy ID: " + str(policy_id) + " Policy Name: " + str(policy_name))
            invalid_policy_list.append({"policy_id": policy_id, "policy_name": policy_name})

            return conditions_list, invalid_policy_list, empty_policy_list

        for condition in result_condition_list:
            condition_name = condition["name"]
            condition_id = condition["id"]
            condition_query = condition["nrql"]["query"]
            condition_enabled = condition["enabled"]

            conditions_list.append({"policy_id": policy_id, "policy_name": policy_name, "condition_id": condition_id, "condition_name": condition_name, "condition_query": condition_query, "condition_enabled": condition_enabled})

    return conditions_list, invalid_policy_list, empty_policy_list


def generate_policies_conditions_report():

    policies_and_conditions_report = []
    invalid_policies_report = []
    empty_policies_report = []

    all_policies_list = get_all_policies()

    for policy in all_policies_list:
        temp_conditions_list, temp_invalid_policies_list, temp_empty_policies_list = get_policy_conditions(policy["policy_id"], policy["policy_name"])

        if temp_conditions_list is not None:
            for condition in temp_conditions_list:
                policies_and_conditions_report.append(condition)

        if temp_invalid_policies_list is not None:
            for policy in temp_invalid_policies_list:
                invalid_policies_report.append(policy)


        if temp_empty_policies_list is not None:
            for policy in temp_empty_policies_list:
                empty_policies_report.append(policy)

    policies_and_conditions_report_filename, invalid_policies_report_filename, empty_policies_report_filename = get_report_file_names()

    logging.info("Writing policies and conditions report to CSV file.")
    csv.write_list_of_dicts_to_csv(policies_and_conditions_report, policies_and_conditions_report_filename)
    csv.write_list_of_dicts_to_csv(invalid_policies_report, invalid_policies_report_filename)
    csv.write_list_of_dicts_to_csv(empty_policies_report, empty_policies_report_filename)