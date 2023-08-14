# Copyright (c) 2023, Xgrid Inc, https://xgrid.co

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import boto3
import logging

# Initialize the AWS Cost Explorer Client
ce_client = boto3.client('ce')

def breakdown_service_cost(service, account_id, start_date, end_date):
    """
    Break down the cost of a specific AWS service.
    
    Args:
    - service: The AWS service name.
    - account_id: The AWS account ID.
    - start_date: Cost data start date in the format 'YYYY-MM-DD'.
    - end_date: Cost data end date in the format 'YYYY-MM-DD'.

    Returns:
    - A dictionary with a detailed breakdown of the service cost.
    """
    
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}],
            Filter={
                'And': [
                    {'Dimensions': {'Key': 'SERVICE', 'Values': [service]}},
                    {'Dimensions': {'Key': 'LINKED_ACCOUNT', 'Values': [account_id]}}
                ]
            }
        )
        return response['ResultsByTime']

    except Exception as e:
        logging.error(f"Error fetching cost breakdown for {service}: {str(e)}")
        return None

def lambda_handler(event, context):
    """
    Breaks down the costs of the top 5 expensive AWS services.
    
    Args:
    - event: 
        - Contains a list of the top 5 expensive services and associated details.
        - start_date
        - end_date
        - account_id
    - context: Lambda context object.

    Returns:
    - A dictionary with cost breakdown details for each service.
    """

    services = json.loads(event['services'])
    start_date = event['start_date']
    end_date = event['end_date']
    account_id = event['account_id']
    cost_breakdown = {}

    for service_data in services:
        service_name = service_data['Service']

        breakdown = breakdown_service_cost(service_name, account_id, start_date, end_date)
        cost_breakdown[service_name] = breakdown

    logging.info(cost_breakdown)
    return {
        'statusCode': 200,
        'body': json.dumps(cost_breakdown)
    }

