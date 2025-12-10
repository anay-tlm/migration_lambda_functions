import json
import os
import re
import boto3
import uuid
from datetime import datetime
import pandas as pd
import pytz
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from marshmallow import Schema, fields, validate, INCLUDE, validates, ValidationError
from slugify import slugify
import psycopg2
from psycopg2 import errors
import requests

'''postgresql connectivity'''
pg_config = {
    "host": "192.168.7.165",
    "port": 54322,
    "dbname": "postgres",
    "user": "postgres",
    "password": "your-super-secret-and-long-postgres-password",
}
connection = psycopg2.connect(**pg_config)
cursor = connection.cursor()

origin_pattern = r"tlminsidesales\.com"

email_regex = r'([A-Za-z0-9]+[-.-_\'])*[A-Za-z0-9]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+(?<!\\.)$'
url_pattern = r'\b(?:https?|ftp):\/\/[-A-Za-z0-9+&@#\/%?=~_|!:,.;]*[-A-Za-z0-9+&@#\/%=~_|]'
header_object = {
    'Content-Type': 'application/json',
    "Access-Control-Allow-Origin": "*"
}
lambda_client = boto3.client('lambda', region_name="ap-south-1")


class AccountCreation(Schema):
    class Meta:
        unknown = INCLUDE

    addresses = fields.Str(required=True)
    email = fields.Str(required=True, )
    client_first_name = fields.Str(required=True)
    client_last_name = fields.Str(required=True)
    display_name = fields.Str(required=True)
    country_code = fields.Str(required=True)
    industry = fields.Str(required=True)
    is_all_zipcode = fields.Str(required=True, validate=validate.OneOf(['YES', 'NO']))
    resource = fields.Int(required=True, validate=validate.Range(min=0, max=10000000000))
    phone = fields.Str(required=True)
    website_url = fields.Str(required=True)
    city = fields.Str(required=True)
    country = fields.Str(required=True)
    domain = fields.Str(required=True)
    employee_size = fields.Str(required=True)
    zipcode = fields.Str(required=True)
    system = fields.Str(required=True)
    check_domain = fields.Str(required=True, validate=validate.OneOf(['NTL', 'TL']))
    hosting = fields.Str(required=True)
    kickoff_date = fields.Str(required=True)
    banner_url = fields.Str(required=True, allow_none=True)
    billing_cc = fields.Str(required=True, allow_none=True)
    billing_to = fields.Str(required=False, allow_none=True)
    blog_url = fields.Str(required=True, allow_none=True)
    display_logo = fields.Str(required=True)
    facebook_url = fields.Str(required=True, allow_none=True)
    linkedin_url = fields.Str(required=True, allow_none=True)
    twitter_url = fields.Str(required=True, allow_none=True)
    youtube_url = fields.Str(required=True, allow_none=True)
    follow_up_services = fields.Str(required=True, allow_none=True)
    follow_up_service_name = fields.Str(required=True, allow_none=True)
    follow_up_short_service_name = fields.Str(required=True, allow_none=True)
    parent_account = fields.Str(required=True, allow_none=True)


def lambda_handler():
    event = {"check_domain":"NTL","display_name":"9december-testing","client_first_name":"9december","client_last_name":"testing","industry":"Healthcare","employee_size":"2-10","country":"India","city":"ngp","addresses":"215 East Bay Street Suite 500-E Charleston, SC 29401","zipcode":"32751","phone":"23678","website_url":"","hosting":"Microsoft Office","domain":"connexiocloud.com","email":"9december@chatgpt.com","kickoff_date":"11/12/2025","resource":"1","is_all_zipcode":"YES","system":"5","display_logo":"https://public-uploads-tlm.s3.amazonaws.com/dashboard-logo/switch_telecome_logo.png","account_status":"","facebook_url":"","linkedin_url":"","twitter_url":"","youtube_url":"","banner_url":"","billing_cc":"","billing_to":"","blog_url":"","follow_up_service_name":"","follow_up_services":"","follow_up_short_service_name":"","last_keap_status":"","country_code":"US","account_name":"9december-testing","parent_account":"006dfa1e-1603-46ab-8158-6027f7077d48"}
    # print(event)
    # if event is None:
    #     print(f"pay load empty")
    #     return {
    #         'statusCode': 422,
    #         # "headers": header_object,
    #         'body': json.dumps({"message": "pay load empty"})
    #     }
    #
    # if len(event) == 0:
    #     print("pay load empty")
    #     return {
    #         'statusCode': 422,
    #         # "headers": header_object,
    #         'body': json.dumps({"message": "pay load empty"})
    #     }
    # print(event)
    #
    # if not event['headers'].get('origin'):
    #     print(f"payload not contain origin")
    #     return {
    #         'statusCode': 422,
    #         # "headers": header_object,
    #         'body': json.dumps({"message": "payload not contain origin"})
    #     }
    #
    # if not event['headers'].get('authorization'):
    #     print("payload not contain authorization")
    #     return {
    #         'statusCode': 422,
    #         # "headers": header_object,
    #         'body': json.dumps({"message": "payload not contain authorization"})
    #     }
    #
    # print("authorize employee")
    #
    # lambda_invocation = boto3.client('lambda', region_name="ap-south-1")
    # list_data = {'Authorization': event['headers']['authorization']}
    #
    # authorize_employee = lambda_invocation.invoke(
    #     FunctionName="arn:aws:lambda:ap-south-1:405255119935:function:tlm_internal_custom_authorizer",
    #     InvocationType='RequestResponse', Payload=json.dumps(list_data))
    #
    # authorize_employee_result = json.loads(authorize_employee['Payload'].read())
    #
    # print(authorize_employee_result)
    #
    # if authorize_employee_result['statusCode'] == 200:
    #     print(authorize_employee_result['message'])
    # else:
    #     return {
    #         "statusCode": 422,
    #         # "headers": header_object,
    #         'body': json.dumps({"response": 'unauthorized person'})
    #     }
    #
    # match1 = re.search(origin_pattern, event['headers']['origin'])
    # cu_region_name = ""
    # if bool(match1):
    #     cu_region_name = 'ap-south-1'
    #     print('region')
    #     dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    #     # pool_id = os.environ.get('client_dashboard_pool_id')
    #     pool_id = os.environ.get('client_dashboard_pool_id_dev')
    # else:
    #     cu_region_name = 'ap-south-1'
    #     print("locally db")
    #     dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    #     pool_id = os.environ.get('client_dashboard_pool_id_dev')
    #
    # if not event.get('body'):
    #     print("payload not contain body")
    #     return {
    #         'statusCode': 422,
    #         # "headers": header_object,
    #         'body': json.dumps({"message": "payload not contain body"})
    #     }

    cu_region_name = 'ap-south-1'
    print("locally db")
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    pool_id = "us-east-1_RjkjlTGia"
    if pool_id is None or pool_id == '':
        print("pool id not found")
        return {
            'statusCode': 422,
            # "headers": header_object,
            'body': json.dumps({"message": "Unable get user pool for user creation"})
        }

    # event = json.loads(event['body'])
    desired_timezone = 'Asia/Kolkata'
    india_timezone = pytz.timezone(desired_timezone)
    cognito = boto3.client('cognito-idp', region_name='us-east-1')
    user_list = "92d9bb0a-ad81-4121-8c4c-5ff1cf1709cf,329b3297-1d66-4ae8-bfe8-afdf13e5b1d4,0f8beaf2-54b4-4191-8f64-2cf8dc2acc1a,7be1d1a3-f731-403e-b90e-0b10397caab3"
    user_list = user_list.split(',')
    print(f"user list is {user_list}")
    tbl_error_log = dynamodb.Table("tbl_error_log")
    tbl_account = dynamodb.Table('tbl_account')
    tbl_user = dynamodb.Table('tbl_user')
    tbl_company = dynamodb.Table('tbl_company')
    tbl_industry = dynamodb.Table('tbl_industry_type')
    tbl_title = dynamodb.Table('tbl_title')
    tbl_hosting = dynamodb.Table('tbl_hosting')
    tbl_employee_size = dynamodb.Table('tbl_employee_size')

    industry_rec = pd.DataFrame(tbl_industry.scan()['Items'])
    title_rec = pd.DataFrame(tbl_title.scan()['Items'])
    emp_size = pd.DataFrame(tbl_employee_size.scan()['Items'])
    hosting_df = pd.DataFrame(tbl_hosting.scan()['Items'])

    account_df = pd.DataFrame(tbl_account.query(IndexName='tlm_account-account_id-index',
                                                KeyConditionExpression=Key('tlm_account').eq('tlm_account'))['Items'])
    account_df = account_df.fillna('')
    account_df['domain'] = account_df['email'].str.split('@').str[1]
    account_df['domain'] = account_df['domain'].astype(str)
    account_df['domain'] = account_df['domain'].apply(lambda x: x.strip().lower())

    print(f"get all accounts df")
    constant_account_df = account_df
    constant_account_df = constant_account_df.fillna('')
    constant_account_df = constant_account_df[constant_account_df['account_status'] == "Active"]

    companies_count_df = constant_account_df['company_id'].value_counts().reset_index()
    companies_count_df.columns = ['company_id', 'company_account_count']
    filter_companies_count_df = companies_count_df[companies_count_df['company_account_count'] != 1]
    unique_company_id_list = filter_companies_count_df['company_id'].unique().tolist()
    final_constant_account_df = constant_account_df[constant_account_df['company_id'].isin(unique_company_id_list)]

    franchise_value_dict = {}
    for f_cmp_id in unique_company_id_list:
        cmp_accounts = constant_account_df[constant_account_df['company_id'] == f_cmp_id]
        acct_list = cmp_accounts['account_id'].unique().tolist()
        franchise_value_dict[f_cmp_id] = acct_list

    def check_email_existence(email, user_pool_idx):
        try:
            response = cognito.admin_get_user(
                UserPoolId=user_pool_idx,
                Username=email
            )
            return response['Username']

        except cognito.exceptions.UserNotFoundException:
            return "create"

    def create_user(user_email, account_id):
        password = 'yf2byU$@zTg5'
        email_address = str(user_email).lower().strip()
        create_user_response = cognito.admin_create_user(
            UserPoolId=pool_id,
            Username=email_address,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email_address,
                },
                {
                    'Name': 'email_verified',
                    'Value': 'True',
                },
            ],
            TemporaryPassword=password,
            ForceAliasCreation=True,
            MessageAction='SUPPRESS'
        )
        if create_user_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            user_id = create_user_response['User']['Username']
            try:
                tbl_user.put_item(Item={
                    'user_id': user_id,
                    'account_ids': [str(account_id)],
                    'email': email_address,
                    'user_type': ' ',
                    'status': 'Active'
                }
                )
            except Exception as e:
                print('Unable to create user in table user', e)
            response = cognito.admin_set_user_password(
                UserPoolId=pool_id,
                Username=email_address,
                Password=password,
                Permanent=True
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print('User has been created successfully', email_address)
                return user_id
        else:
            print('User may be already there')

    def update_error_log(error_log, error_description):
        try:
            insert_error = tbl_error_log.put_item(
                Item={
                    'date': datetime.now(india_timezone).date().strftime('%d/%m/%Y'),
                    'error_log': str(error_log),
                    'description': str(error_description),
                    'created_at': datetime.now(india_timezone).isoformat(),
                    'updated_at': datetime.now(india_timezone).isoformat()
                })
        except ClientError as err_log:
            print(err_log)
            print(f"error while updating error log in error table")

    datavalidation = AccountCreation(unknown=INCLUDE)

    try:
        datavalidation.load(event, )
    except ValidationError as err:
        error_message = ''
        for key in err.messages.keys():
            for msg in err.messages[key]:
                error_message += ' ' + key + ' ' + msg
        print(error_message)
        print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                               error_description=f"{err.messages.keys()} {str(error_message)}"))

        return {
            "statusCode": 422,
            # "headers": header_object,
            'body': json.dumps({"message": error_message})
        }

    total_columns = ['display_name', 'client_first_name', 'client_last_name', 'industry', 'employee_size', 'country',
                     'country_code', 'city', 'addresses', 'zipcode', 'phone', 'website_url', 'hosting', 'domain',
                     'email',
                     'kickoff_date', 'resource', 'is_all_zipcode', 'system', 'display_logo', 'banner_url', 'billing_cc',
                     'billing_to', 'blog_url',
                     'facebook_url', 'linkedin_url', 'twitter_url', 'youtube_url', 'check_domain',
                     'follow_up_short_service_name',
                     'follow_up_services', 'follow_up_service_name', 'parent_account']

    for col in total_columns:
        if col not in event.keys():
            print(f"{col} field not in input data")
            return {
                "statusCode": 422,
                # "headers": header_object,
                'body': json.dumps({"message": f"Required input {col} is missing"})
            }

    required_columns = ['display_name', 'client_first_name', 'client_last_name', 'industry', 'employee_size', 'country',
                        'country_code', 'city', 'addresses', 'zipcode', 'phone', 'hosting', 'domain',
                        'email',
                        'kickoff_date', 'resource', 'is_all_zipcode', 'system', 'display_logo']

    for req_col in required_columns:
        if str(event[req_col]).strip() == "":
            print(f"{req_col} field value can not be empty")
            return {
                'body': json.dumps({"message": f"{req_col} field value can not be empty"}),
                # "headers": header_object,
                "statusCode": 422
            }
        if str(event[req_col]).strip() != "" and str(event[req_col]).strip() is None:
            print(f"{req_col} field value can not be None")
            return {
                'body': json.dumps({"message": f"{req_col} field value can not be None"}),
                # "headers": header_object,
                "statusCode": 422
            }
        if str(req_col).strip() == 'zipcode' and len(str(event[req_col]).strip()) < 5:
            print(f"zipcode length must be 5 or more")
            return {
                'body': json.dumps({"message": f"zipcode length must be 5 or more"}),
                # "headers": header_object,
                "statusCode": 422
            }

    try:
        chk = int(str(event['resource']).strip())
    except ValueError as err:
        print(f"resource should be integer number, {err}")
        return {
            "statusCode": 422,
            # "headers": header_object,
            'body': json.dumps({"message": f"Resource should be a number"})
        }

    try:
        chk = int(str(event['system']).strip())
    except ValueError as err:
        print(f"system should be integer number, {err}")
        return {
            "statusCode": 422,
            # "headers": header_object,
            'body': json.dumps({"message": f"System should be a number"}),
        }

    if int(str(event['resource']).strip()) != 0 and int(str(event['resource']).strip()) < 0:
        # if not (int(event['resource']) > 0 and int(event['resource']) != 0):
        error_message = 'resource should be 0 or grater than 0'
        print(error_message)
        print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                               error_description=str(error_message)))
        return {
            "statusCode": 422,
            # "headers": header_object,
            'body': json.dumps({"message": error_message}),
        }

    company_name = str(event['display_name']).strip().title()
    account_name = slugify(str(event['display_name']).strip().lower())

    if not re.match(email_regex, str(event['email']).strip().lower()):
        print(f'Please Enter valid email {event["email"]}')
        print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                               error_description=str(f'Please Enter valid email {event["email"]}')))
        return {
            "statusCode": 422,
            # "headers": header_object,
            'body': json.dumps({"message": f'Please Enter valid email {event["email"]}'})
        }

    if event['billing_cc'] != '':
        if not re.match(email_regex, str(event['billing_cc']).strip().lower()):
            print(f'Please Enter valid billing_cc {event["billing_cc"]}')
            print(
                update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                 error_description=str(f'Please Enter valid billing_cc {event["billing_cc"]}')))
            return {
                'body': json.dumps({'message': f'Please Enter valid billing_cc {event["billing_cc"]}'}),
                # "headers": header_object,
                "statusCode": 422

            }

    if event['billing_to'] != '':
        if not re.match(email_regex, str(event['billing_to']).strip().lower()):
            print(f'Please Enter valid billing_to {event["billing_to"]}')
            print(
                update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                 error_description=str(f'Please Enter valid billing_to {event["billing_to"]}')))
            return {
                'body': json.dumps({'message': f'Please Enter valid billing_cc {event["billing_to"]}'}),
                # "headers": header_object,
                "statusCode": 422
            }

    if event['blog_url'] != '':
        if not re.match(url_pattern, event['blog_url']):
            print(f'Please Enter valid blog_url {event["blog_url"]}')
            print(
                update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                 error_description=str(f'Please Enter valid blog_url {event["blog_url"]}')))
            # return {'message': f'Invalid blog_url {event["blog_url"]}', "statusCode": 400}
            return {
                'body': json.dumps({'message': f'Please Enter valid blog_url {event["blog_url"]}'}),
                # "headers": header_object,
                "statusCode": 422
            }

    if event['facebook_url'] != '':
        if not re.match(url_pattern, event['facebook_url']):
            print(f'Please Enter valid facebook_url {event["facebook_url"]}')
            print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                   error_description=str(
                                       f'{event["display_name"]} invalid facebook_url {event["facebook_url"]}')))
            # return {'message': f'Invalid facebook_url {event["facebook_url"]}', "statusCode": 400}
            return {
                'body': json.dumps({'message': f'Please Enter valid facebook_url {event["facebook_url"]}'}),
                # "headers": header_object,
                "statusCode": 422
            }

    if event['linkedin_url'] != '':
        if not re.match(url_pattern, event['linkedin_url']):
            print(f'Please Enter valid linkedin_url {event["linkedin_url"]}')
            print(
                update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                 error_description=str(f'Please Enter valid linkedin_url {event["linkedin_url"]}')))
            return {
                'body': json.dumps({'message': f'Please Enter valid linkedin_url {event["linkedin_url"]}'}),
                # "headers": header_object,
                "statusCode": 422
            }
            # return {'message': f'Invalid linkedin_url {event["linkedin_url"]}', "statusCode": 400}

    if event['twitter_url'] != '':
        if not re.match(url_pattern, event['twitter_url']):
            print(f'Please Enter valid twitter_url {event["twitter_url"]}')
            print(
                update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                 error_description=str(
                                     f'Please{event["display_name"]} Enter valid twitter_url {event["twitter_url"]}')))
            # return {'message': f'Invalid twitter_url {event["twitter_url"]}', "statusCode": 400}
            return {
                'body': json.dumps({'message': f'Please Enter valid twitter_url {event["twitter_url"]}'}),
                # "headers": header_object,
                "statusCode": 422
            }

    if event['youtube_url'] != '':
        if not re.match(url_pattern, event['youtube_url']):
            print(f'Please Enter valid youtube_url {event["youtube_url"]}')
            print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                   error_description=str(
                                       f' {event["display_name"]} Please Enter valid youtube_url {event["youtube_url"]}')))
            return {
                'body': ({'message': f'Please Enter valid youtube_url {event["youtube_url"]}'}),
                # "headers": header_object,
                "statusCode": 422
            }

    if event['website_url'] != '':
        if not re.match(url_pattern, event['website_url']):
            print(f'Please Enter valid website_url {event["website_url"]}')
            print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                   error_description=str(
                                       f'{event["display_name"]} Please Enter valid website_url {event["website_url"]}')))
            return {
                'body': ({'message': f'Please Enter valid website_url {event["website_url"]}'}),
                # "headers": header_object,
                "statusCode": 422
            }

    try:
        kickoff_date = datetime.strptime(event['kickoff_date'], '%d/%m/%Y').date()
        upd_kickoff_date = kickoff_date.strftime("%Y-%m-%d")
        current_date = datetime.now().date()
        if kickoff_date < current_date:
            print("please select future kickoff date")
            return {
                "statusCode": 422,
                # "headers": header_object,
                'body': json.dumps({"message": "please select future kickoff date"})
            }
    except ValueError:
        print("The provided date string does not match the expected format dd/mm/YYYY")
        print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                               error_description=str(
                                   f'{event["display_name"]} the expected format dd/mm/YYYY {event["kickoff_date"]}')))
        return {
            "statusCode": 422,
            # "headers": header_object,
            'body': json.dumps(
                {"message": "The provided kickoff_date string does not match the expected format  dd/mm/YYYY"})
        }

    filter_account_df = account_df[account_df['account_name'].isin([account_name])]

    if not filter_account_df.empty:
        print(f'Account already exists {account_name}')
        print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                               error_description=str(f'Account already exists {account_name}')))
        return {
            'body': json.dumps({'message': 'Account already exists'}),
            # "headers": header_object,
            "statusCode": 422
        }

    if event['check_domain'] == 'NTL':
        # filter_account_company = account_df[account_df['domain'].isin([str(event['email']).split('@')[1]])]
        filter_account_company = account_df[
            account_df['domain'].isin([str(event['email']).lower().strip().split('@')[1]])]
        if filter_account_company.empty and not event.get('account_company_id'):
            try:
                company_response = pd.DataFrame(tbl_company.query(IndexName='zipcode-name-index',
                                                                  KeyConditionExpression=Key('zipcode').eq(
                                                                      event['zipcode']))['Items'])
                if company_response.shape[0] > 0:
                    company_response['name'] = company_response['name'].apply(lambda x: x.strip().lower())
                    company_response = company_response[
                        company_response['name'] == str(event['display_name']).strip().lower()]
                if company_response.empty:
                    company_id = uuid.uuid4()
                    industry_type = industry_rec[industry_rec['industry_type'] == event['industry']]
                    employee_size = emp_size[emp_size['employee_size'] == event['employee_size']]

                    if industry_type.empty:
                        print(f"given industry type not found {event['industry']}")
                        print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                               error_description=f"given industry type not found {event['industry']}"))
                        # return {'message': 'user already exist in cognito', "statusCode": 400}
                        return {
                            'body': json.dumps({'message': 'given industry type not found'}),
                            # "headers": header_object,
                            "statusCode": 422
                        }

                    if employee_size.empty:
                        print(f"given employee_size not found {event['employee_size']}")
                        print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                               error_description=f"given employee_size not found {event['employee_size']}"))
                        #                         return {'message': 'user already exist in cognito', "statusCode": 400}
                        return {
                            'body': json.dumps({'message': 'given employee_size not found'}),
                            # "headers": header_object,
                            "statusCode": 422
                        }
                    tbl_company.put_item(
                        Item={
                            "company_id": str(company_id),
                            "name": company_name,
                            "industry": industry_type['industry_id'].iloc[0],
                            "employee_size": employee_size['employee_size_id'].iloc[0],
                            "city": str(event['city']).title(),
                            "zipcode": str(event['zipcode']),
                            "address": str(event['addresses']),
                            "country": str(event['country']),
                            "phone": str(event['phone']),
                            "website": str(event['website_url']),
                            "domain": str(event['domain']),
                            "hosting": str(event['hosting']),
                            "created_at": datetime.now().isoformat(),
                            "updated_at": datetime.now().isoformat(),
                            "business_status": "",
                            "latitude": "",
                            "longitude": "",
                        }
                    )
                    '''insert into postgresql'''
                    print(company_id)
                    try:
                        cursor.execute(
                            "INSERT INTO company (company_id,name,address,zipcode,website,city,country,"
                            "domain,employee_size,industry,hosting,latitude,longitude,phone,created_at,updated_at)"
                            "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (
                                str(company_id),
                                company_name,
                                str(event['addresses']),
                                str(event['zipcode']),
                                str(event['website_url']),
                                str(event['city']).title(),
                                str(event['country']),
                                str(event['domain']),
                                employee_size['employee_size_id'].iloc[0],
                                industry_type['industry_id'].iloc[0],
                                str(event['hosting']),
                                None,  # latitude
                                None,  # longitude
                                str(event['phone']),
                                datetime.now().isoformat(),
                                datetime.now().isoformat()
                            )
                        )
                        print(connection.commit())
                    except errors.UniqueViolation:
                        connection.rollback()
                        print("Error: company already exists")
                    except Exception as err:
                        print(f"error while inserting company record, {err}")
                        print(f"Error while creating company in postgresql, {err}")
                        print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                               error_description=f"{event['zipcode']}_{company_name} Error while creating company in postgresql, {err}"))

                else:
                    if company_response.shape[0] > 1:
                        print(
                            f"on zipcode {event['zipcode']} multiple company already present with same name {company_name} ")
                        print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                               error_description=f"{event['display_name']} on zipcode {event['zipcode']} multiple company already present with same name {company_name} "))
                        #
                        # return {
                        #     'statusCode': 400,
                        #     'message': f"on zipcode {event['zipcode']} multiple company already present with same name {company_name} "
                        # }
                        # return {
                        #     'statusCode': 400,
                        #     "headers": header_object,
                        #     'body': json.dumps({'message': f"on zipcode {event['zipcode']} multiple company already present with same name {company_name} "})
                        # }
                    company_id = company_response['company_id'].iloc[0]
            except ClientError as e:
                print(f"Error while creating company, {e}")
                print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                       error_description=f"{event['zipcode']}_{company_name} Error while creating company, {e}"))
                return {
                    'statusCode': 422,
                    # "headers": header_object,
                    'body': json.dumps({'message': f"Error while creating company, {e}"})
                }
        else:
            if len(filter_account_company['company_id'].unique().tolist()) > 1:
                print(
                    f'company domain for account {account_name} already exist but company id multiple for same  company')
                print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                       error_description=str(
                                           f' {event["zipcode"]}_{company_name} company domain for account {account_name} already exist but company id multiple for same  company')))
                return {
                    'body': json.dumps({
                                           'message': f'account domain for account {account_name} already exist but client company id are multiple'}),
                    # "headers": header_object,
                    "statusCode": 422
                }
            if not filter_account_company.empty:
                company_id = filter_account_company['company_id'].iloc[0]
        if event.get('account_company_id'):
            if not filter_account_company.empty:
                if str(event['account_company_id']).strip() != str(company_id).strip():
                    print(f"company id not matched with existing company id")
                    print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                           error_description=f"{event['zipcode']}_{company_name} company id not matched with existing company id"))
                    return {
                        'statusCode': 422,
                        # "headers": header_object,
                        'body': json.dumps({
                                               'message': f"client email domain match to already exist company but company id not matched with existing company id"})
                    }
            else:
                company_id = event['account_company_id']
                # chekc company id present in database or not
                try:
                    get_company = tbl_company.query(KeyConditionExpression=Key('company_id').eq(company_id))
                    if get_company['Count'] == 0:
                        return {
                            'statusCode': 422,
                            # "headers": header_object,
                            'body': json.dumps({'message': f"provide client company not found in database"})
                        }
                except ClientError as err:
                    print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                           error_description=str(
                                               f"error while get company {company_id} for account {account_name} {err.response['Error']['Message']}")))
                    return {
                        'statusCode': 422,
                        # "headers": header_object,
                        'body': json.dumps(
                            {'message': f"Error while get company information for account {account_name}"})
                    }
    else:
        company_id = "4a408c0f-06c0-4d29-b391-5d8b0508951d"
        account_name = slugify(account_name)

        '''get tl urls'''
        company_all_account = pd.DataFrame(
            tbl_account.query(KeyConditionExpression=Key('company_id').eq(company_id))['Items'])
        company_all_account = company_all_account[(company_all_account['facebook_url'] != "") &
                                                  (company_all_account['linkedin_url'] != "") &
                                                  (company_all_account['twitter_url'] != "") &
                                                  (company_all_account['youtube_url'] != "")]
        event['facebook_url'] = company_all_account['facebook_url'].iloc[0]
        event['linkedin_url'] = company_all_account['linkedin_url'].iloc[0]
        event['twitter_url'] = company_all_account['twitter_url'].iloc[0]
        event['youtube_url'] = company_all_account['youtube_url'].iloc[0]

    new_account_id = uuid.uuid4()
    # followup_services_list = ['follow_up_services', 'follow_up_service_name', 'follow_up_short_service_name']
    # for field in followup_services_list:
    #     event.setdefault(field, "")

    if str(event['follow_up_service_name']).strip() == "" and str(event['follow_up_short_service_name']).strip() == "":
        if company_id in franchise_value_dict.keys():
            print("present")
            franchise_acct_list = franchise_value_dict[company_id]
            filter_franchise_acct = account_df[(account_df['account_id'].isin(franchise_acct_list)) &
                                               (account_df['follow_up_service_name'] != "") &
                                               (account_df['follow_up_short_service_name'] != "")]
            if not filter_franchise_acct.empty:
                event['follow_up_services'] = filter_franchise_acct['follow_up_services'].iloc[0]
                event['follow_up_service_name'] = filter_franchise_acct['follow_up_service_name'].iloc[0]
                event['follow_up_short_service_name'] = filter_franchise_acct['follow_up_short_service_name'].iloc[0]

    company_response = tbl_company.query(KeyConditionExpression=Key('company_id').eq(str(company_id)))
    created_company_name = ""
    if company_response['Count'] == 1:
        created_company_name = company_response['Items'][0]['name']
    else:
        print(f"company not present at tbl_company")

    if str(event['parent_account']).strip() != "":
        billing_type = "duplicate"
    else:
        billing_type = "automatic"


    try:
        insert_account = tbl_account.put_item(
            Item={
                'company_id': str(company_id),
                'account_id': str(new_account_id),
                'account_name': str(account_name),
                'account_status': "Active",
                'addresses': str(event['addresses']).strip(),
                'banner_url': str(event['banner_url']),
                'billing_cc': str(event['billing_cc']).lower().strip(),
                'billing_to': str(event['billing_to']).lower().strip(),
                'blog_url': str(event['blog_url']),
                'client_first_name': str(event['client_first_name']).strip().title(),
                'client_last_name': str(event['client_last_name']).strip().title(),
                'client_name': str(event['client_first_name']).strip().title() + ' ' + str(
                    event['client_last_name']).strip().title(),
                'country_code': str(event['country_code']).upper(),
                'created_at': datetime.now().isoformat(),
                'display_logo': str(event['display_logo']),
                'display_name': str(event['display_name']).strip(),
                'email': str(event['email']).lower().strip(),
                'facebook_url': str(event['facebook_url']),
                'industry': str(event['industry']),
                'is_all_zipcode': str(event['is_all_zipcode']),
                'kickoff_date': str(event['kickoff_date']),
                'linkedin_url': str(event['linkedin_url']),
                'phone': str(event['phone']),
                # 'postal_code': str(event['zipcode']),
                'headquarter': str(event['zipcode']),
                'resource': int(event['resource']),
                'twitter_url': str(event['twitter_url']),
                'updated_at': datetime.now().isoformat(),
                'website_url': str(event['website_url']),
                'youtube_url': str(event['youtube_url']),
                'system': str(event['system']),
                'account_parameters': '',
                'background_process': '',
                'address_line_1': '',
                'address_line_2': '',
                'admin_area_1': '',
                'admin_area_2': '',
                'follow_up_services': event['follow_up_services'],
                'follow_up_service_name': event['follow_up_service_name'],
                'follow_up_short_service_name': event['follow_up_short_service_name'],
                'invoice_prefix': "",
                'pay_type': "",
                "base_price": int(0),
                "chargebee_subscription_id": "",
                "lead_charges": int(0),
                'revenue': int("0"),
                'tlm_account': 'tlm_account',
                'username': "",
                'billing_cc_fn': '',
                'billing_to_fn': str(event['client_first_name']).strip().title(),
                'billing_type': billing_type,
                'keap_account_status': 'Not Active',
                'keap_cc': '',
                'keap_data': int(0),
                'keap_first_name': '',
                'keap_frequency': '',
                'keap_to': '',
                'last_keap_status': '',
                'lead_confirmation_email': '',
                'lead_confirmation_first_name': '',
                'lead_confirmation_last_name': '',
                'outlook_profile': '',
                "parent_account": str(event['parent_account']).strip()
            }
        )
        if insert_account["ResponseMetadata"]["HTTPStatusCode"] == 200:

            '''insert into postgresql database'''
            try:
                cursor.execute("INSERT INTO account (account_id,company_id,account_name,client_first_name,client_last_name,"
                               "client_name,display_name,email,is_all_zipcode,kickoff_date,phone,resource,system,created_at,"
                               "account_status,account_parameters,background_process,parent_account,postal_code,"
                               "username,updated_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                               (
                                   str(new_account_id),
                                   str(company_id),
                                   str(account_name),
                                   str(event['client_first_name']).strip().title(),
                                   str(event['client_last_name']).strip().title(),
                                   str(event['client_first_name']).strip().title() + ' ' + str(
                                       event['client_last_name']).strip().title(),
                                   str(event['display_name']).strip(),
                                   str(event['email']).lower().strip(),
                                   str(event['is_all_zipcode']),
                                   str(upd_kickoff_date),
                                   str(event['phone']),
                                   int(event['resource']),
                                   int(event['system']),
                                   datetime.now().isoformat(),
                                   "Active",
                                   None,
                                   None,
                                   str(event['parent_account']).strip(),
                                   str(event['zipcode']),
                                   None,
                                   datetime.now().isoformat()
                               ))
                print(connection.commit())
                if cursor.rowcount == 1:
                    print("account added in postgresql")
                if cursor.rowcount == 0:
                    print("account not added in postgresql")
                if cursor.rowcount > 1:
                    print("multiple account added in postgresql")
            except errors.UniqueViolation:
                connection.rollback()
                print(f"already present in account table")
            except Exception as err:
                print(f"Error while creating account, {err}")
                print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                       error_description=f"Error while creating account in postgresql{err}"))
            city = ''
            try:
                country_code = str(event['country_code']).lower()
                zipcode = str(event['zipcode']).strip()
                url = f"http://api.zippopotam.us/{country_code}/{zipcode}"
                response = requests.get(url)
                print(response.status_code)
                if response.status_code == 200:
                    data = response.json()
                    print(data)
                    place = data.get("places", [{}])[0]
                    city = place.get("place name")
            except Exception as err:
                print(f"error getting city, {err}")
                return {
                    'statusCode':400,
                    'body': json.dumps({'message':f"error getting city, {err}"})
                }
            try:
                cursor.execute(
                    "INSERT INTO account_address (address_id, account_id,addresses,city,country_code,headquarter,"
                    "created_at,address_line_1,address_line_2,admin_area_1,admin_area_2,updated_at)"
                    "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        str(uuid.uuid4()),
                        str(new_account_id),
                        str(event['addresses']).strip(),
                        city,
                        str(event['country_code']).upper(),
                        str(event['zipcode']).strip(),
                        datetime.now().isoformat(),
                        None,
                        None,
                        None,
                        None,
                        datetime.now().isoformat()
                    ))
                print(connection.commit())
                if cursor.rowcount == 1:
                    print("account_address added in postgresql")
                if cursor.rowcount == 0:
                    print("account_address not added in postgresql")
                if cursor.rowcount > 1:
                    print("multiple account_address added in postgresql")
            except errors.UniqueViolation:
                connection.rollback()
                print(f"already present in account address")
            except Exception as err:
                print(f"Error while creating account address, {err}")
                print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                       error_description=f"Error while creating account address in postgresql{err}"))

            try:
                cursor.execute(
                    "INSERT INTO account_billing (billing_id, account_id,base_price,chargebee_subscription_id,lead_charges,revenue,"
                    "created_at,billing_cc,billing_cc_fn,billing_to,billing_to_fn,billing_type,lead_confirmation_email,lead_confirmation_first_name,"
                    "lead_confirmation_last_name,updated_at)"
                    "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        str(uuid.uuid4()),
                        str(new_account_id),
                        int(0),
                        "",
                        int(0),
                        str(0),
                        datetime.now().isoformat(),
                        str(event['billing_cc']).lower().strip(),
                        None,
                        str(event['billing_to']).lower().strip(),
                        str(event['client_first_name']).strip().title(),
                        billing_type,
                        None,
                        None,
                        None,
                        datetime.now().isoformat()
                    ))
                print(connection.commit())
                if cursor.rowcount == 1:
                    print("account_billing added in postgresql")
                if cursor.rowcount == 0:
                    print("account_billing not added in postgresql")
                if cursor.rowcount > 1:
                    print("multiple account_billing added in postgresql")
            except errors.UniqueViolation:
                connection.rollback()
                print(f"already present in account_billings")
            except Exception as err:
                print(f"Error while creating account_billings, {err}")
                print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                       error_description=f"Error while creating account_billings in postgresql{err}"))

            try:
                cursor.execute(
                    "INSERT INTO account_profiles (profile_id, account_id,follow_up_service_name,follow_up_short_service_name,"
                    "created_at,banner_url,blog_url,display_logo,facebook_url,flicker_url,follow_up_services,linkedin_url,twitter_url,"
                    "website_url,youtube_url,updated_at)"
                    "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        str(uuid.uuid4()),
                        str(new_account_id),
                        str(event['follow_up_service_name']).strip(),
                        str(event['follow_up_short_service_name']).strip(),
                        datetime.now().isoformat(),
                        str(event['banner_url']),
                        str(event['blog_url']),
                        str(event['display_logo']),
                        str(event['facebook_url']),
                        None,
                        str(event['follow_up_services']),
                        str(event['linkedin_url']),
                        str(event['twitter_url']),
                        str(event['website_url']),
                        str(event['youtube_url']),
                        datetime.now().isoformat()
                    ))
                print(connection.commit())
                if cursor.rowcount == 1:
                    print("account_profiles added in postgresql")
                if cursor.rowcount == 0:
                    print("account_profiles not added in postgresql")
                if cursor.rowcount > 1:
                    print("multiple account_profiles added in postgresql")
            except errors.UniqueViolation:
                connection.rollback()
                print(f"already present in account_profiles")
            except Exception as err:
                print(f"Error while creating account_profiles, {err}")
                print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                       error_description=f"Error while creating account_profiles in postgresql{err}"))

            try:
                cursor.execute(
                    "INSERT INTO account_keap (keap_id, account_id,keap_account_status,keap_cc,"
                    "created_at,keap_data,keap_first_name,keap_frequency,keap_to,last_keap_status,updated_at)"
                    "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        str(uuid.uuid4()),
                        str(new_account_id),
                        'Inactive',
                        [],
                        datetime.now().isoformat(),
                        int(0),
                        None,
                        None,
                        None,
                        None,
                        datetime.now().isoformat()
                    ))
                print(connection.commit())
                if cursor.rowcount == 1:
                    print("account_keap added in postgresql")
                if cursor.rowcount == 0:
                    print("account_keap not added in postgresql")
                if cursor.rowcount > 1:
                    print("multiple account_keap added in postgresql")
            except errors.UniqueViolation:
                connection.rollback()
                print(f"already present in account_keap")
            except Exception as err:
                print(f"Error while creating account_keap, {err}")
                print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                       error_description=f"Error while creating account_keap in postgresql{err}"))


            try:
                if company_id == "4a408c0f-06c0-4d29-b391-5d8b0508951d":
                    inputParams0 = {'account_id': str(new_account_id), 'region': cu_region_name}
                    response = lambda_client.invoke(
                        FunctionName='arn:aws:lambda:ap-south-1:405255119935:function:tlm_account_onboarding_create_geojson_file',
                        InvocationType='RequestResponse',
                        Payload=json.dumps(inputParams0)
                    )
                    payload = response['Payload'].read()
                    print('Lambda Function Response:', payload)
            except Exception as err:
                print(f"error, invoking tlm_account_onboarding_create_geojson_file lambda function,{err}")
                print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                       error_description=f"error, invoking tlm_account_onboarding_create_geojson_file lambda function,{err}"))
                return {
                    'statusCode': 400,
                    'body': json.dumps({'message': f"Error calling lambda function, {err}"})
                }

            try:
                email_exists = check_email_existence(str(event['email']).strip().lower(), pool_id)
                if email_exists == 'create':
                    cognito_user_id = create_user(str(event['email']).strip().lower(), str(new_account_id))
                else:
                    cognito_user_id = email_exists
                    user_list.append(cognito_user_id)

                print("Company ID: " + str(company_id))
                print("Account ID: " + str(new_account_id))
                print("User ID: " + str(cognito_user_id))

                try:
                    if cu_region_name == "us-east-1":
                        owner_email = ['notification@tlminsidesales.com']
                        cc_email = []
                    else:
                        owner_email = ['archana.sahu@tlminsidesales.com']
                        cc_email = ['karishma.rangari@tlminsidesales.com']

                    inputParams = {
                        'template_key': "account_creation.html",
                        "display_name": str(event['display_name']).strip(),
                        "client_name": str(event['client_first_name']).strip().title() + ' ' + str(
                            event['client_last_name']).strip().title(),
                        "company_name": created_company_name,
                        "user_email": str(event['email']).strip().lower(),
                        "owner_email": owner_email,
                        "cc_email": cc_email,
                        "kickoff_date": str(event['kickoff_date'])
                    }
                    response = lambda_client.invoke(
                        FunctionName='arn:aws:lambda:ap-south-1:405255119935:function:tlm_send_alert_notification',
                        InvocationType='RequestResponse',
                        Payload=json.dumps(inputParams, default=str)
                    )
                    payload = response['Payload'].read()
                    print('Lambda Function Response:', payload)

                    ##slack notification
                    inputParams2 = {
                        'template_key': "account_creation.html",
                        'channel_id': 'C0949DB0YET',
                        "display_name": str(event['display_name']).strip(),
                        "client_name": str(event['client_first_name']).strip().title() + ' ' + str(
                            event['client_last_name']).strip().title(),
                        "company_name": created_company_name,
                        "user_email": str(event['email']).strip().lower(),
                        "owner_email": owner_email,
                        "cc_email": cc_email,
                        "kickoff_date": str(event['kickoff_date'])
                    }
                    response = lambda_client.invoke(
                        FunctionName='arn:aws:lambda:ap-south-1:405255119935:function:tlm_send_alert_slack_notification',
                        InvocationType='RequestResponse',
                        Payload=json.dumps(inputParams2, default=str)
                    )
                    payload = response['Payload'].read()
                    print('Lambda Function Response:', payload)

                    ##create account history
                    inputParams3 = {
                        'account_id': str(new_account_id).strip(),
                        'region': cu_region_name
                    }
                    response3 = lambda_client.invoke(
                        FunctionName='arn:aws:lambda:ap-south-1:405255119935:function:tlm_create_account_history',
                        InvocationType='RequestResponse',
                        Payload=json.dumps(inputParams3, default=str)
                    )
                    payload = response3['Payload'].read()
                    print('Lambda Function Response:', payload)
                except Exception as err:
                    print(f"Error calling lambda function, {err}")
                    print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                           error_description=f"Error calling lambda function, {err}"))
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'message': f"Error calling lambda function, {err}"})
                    }
            except Exception as err:
                print(f"Error while creating cognito user, {err}")
                print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                       error_description=f"{event['email']}_{company_name} Error while creating cognito user, {err}"))
                return {
                    'statusCode': 302,
                    # "headers": header_object,
                    'body': json.dumps({
                        'message': f"Error while creating cognito user but account is created  account_id ={new_account_id} and company_id = {company_id}"})
                }

            # add account id in admin users
            for user in user_list:
                print(user)
                cur_user_info = []
                # get user and update
                try:
                    get_user = tbl_user.query(KeyConditionExpression=Key('user_id').eq(user))
                    if get_user['Count'] == 0:
                        print(f"user Not found")
                        print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                               error_description=str(
                                                   f"user Not found while add account {new_account_id} for user id {user}")))
                        continue
                    cur_user_info.extend(get_user['Items'][0]['account_ids'])
                except ClientError as err:
                    print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                           error_description=str(
                                               f"error while get user while adding account {new_account_id} {err.response['Error']['Message']}")))
                if new_account_id not in cur_user_info:
                    cur_user_info.append(str(new_account_id))
                try:
                    update_user = tbl_user.update_item(
                        Key={'user_id': user},
                        ConditionExpression='user_id=:val1',
                        UpdateExpression="set account_ids=:val2,updated_at=:val3",
                        ExpressionAttributeValues={
                            ':val1': user,
                            ':val2': cur_user_info,
                            ':val3': datetime.now(india_timezone).isoformat(),
                        },
                        ReturnValues="UPDATED_NEW"
                    )
                    print(f"For {user} account {new_account_id} added successfully")
                except ClientError as err:
                    print(err)
                    print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                                           error_description=str(
                                               f"error while adding account {new_account_id} for user {user} error {err.response['Error']['Message']}")))

            return {
                'body': json.dumps({"message": "Account Successfully created",
                                    "data": [{'company_id': str(company_id),
                                              'account_id': str(new_account_id),
                                              'user_id': str(cognito_user_id)
                                              }]}),
                # "headers": header_object,
                "statusCode": 200
            }
    except ClientError as err:
        print(f"Error while creating account, {err}")
        print(update_error_log(error_log=f'tlm_account_onboarding#{str(uuid.uuid4())}',
                               error_description=f" zipcode_company_name_{event['zipcode']}_{company_name} Error while creating account,{err.response['Error']['Message']}"))
        return {
            'statusCode': 302,
            # "headers": header_object,
            'body': json.dumps({
                                   'message': f"Error while creating account but company is created company_id =  {company_id} ,and error =  {err}"})
        }


