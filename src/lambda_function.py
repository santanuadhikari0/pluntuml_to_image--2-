import json
from plantuml import PlantUML, PlantUMLHTTPError
import os
import boto3
import uuid
import re
from botocore.config import Config


config = Config(signature_version='s3v4')
s3 = boto3.client('s3',  region_name='us-east-1',  config=config)

server = PlantUML(url='http://www.plantuml.com/plantuml/img/')
new_url= 'https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v15.0/dist'
import_lines = """
@startuml\n
\n!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v20.0/dist
\n!include AWSPuml/AWSCommon.puml
\n!include AWSPuml/InternetOfThings/IoTRule.puml
\n!include AWSPuml/Analytics/KinesisDataStreams.puml
\n!include AWSPuml/ApplicationIntegration/SimpleQueueService.puml
\n!include AWSPuml/ArtificialIntelligence/SageMakerModel.puml
\n!include AWSPuml/Robotics/RoboMaker.puml
\n!include AWSPuml/General/Users.puml
\n!include AWSPuml/NetworkingContentDelivery/APIGateway.puml
\n!include AWSPuml/SecurityIdentityCompliance/Cognito.puml
\n!include AWSPuml/Compute/Lambda.puml
\n!include AWSPuml/Database/DynamoDB.puml
\n!include AWSPuml/AWSSimplified.puml
\n!include AWSPuml/Compute/EC2.puml
\n!include AWSPuml/Compute/EC2Instance.puml
\n!include AWSPuml/Groups/AWSCloud.puml
\n!include AWSPuml/Groups/VPC.puml
\n!include AWSPuml/Groups/AvailabilityZone.puml
\n!include AWSPuml/Groups/PublicSubnet.puml
\n!include AWSPuml/Groups/PrivateSubnet.puml
\n!include AWSPuml/NetworkingContentDelivery/VPCNATGateway.puml
\n!include AWSPuml/NetworkingContentDelivery/VPCInternetGateway.puml
\n!include AWSPuml/InternetOfThings/IoTRule.puml
\n!include AWSPuml/Storage/SimpleStorageService.puml
\n!include AWSPuml/NetworkingContentDelivery/ElasticLoadBalancing.puml
\n!include AWSPuml/Database/RDS.puml
\n!include AWSPuml/NetworkingContentDelivery/CloudFront.puml
\n!include AWSPuml/SecurityIdentityCompliance/WAF.puml
\n!include AWSPuml/ManagementGovernance/AutoScaling.puml
\n!include AWSPuml/NetworkingContentDelivery/Route53.puml
\n!include AWSPuml/NetworkingContentDelivery/CloudFront.puml
\n!include AWSPuml/SecurityIdentityCompliance/WAF.puml
\n!include AWSPuml/Compute/EC2AutoScaling.puml
\n!include AWSPuml/Database/ElastiCache.puml
\n!include AWSPuml/NetworkingContentDelivery/ElasticLoadBalancingApplicationLoadBalancer.puml
\n!include AWSPuml/NetworkingContentDelivery/Route53HostedZone.puml
\n!include AWSPuml/Database/AuroraInstance.puml
\n!include AWSPuml/SecurityIdentityCompliance/IAMIdentityCenter.puml
"""




# replace ('S3(', 'SimpleStorageServiceS3(')



def remove_include_lines(paragraph):
    lines = paragraph.splitlines()
    filtered = [line for line in lines if not line.strip().startswith(('!include', '!define'))]
    return '\n'.join(filtered)

def add_lines_to_start(paragraph, import_lines):
    return import_lines + '\n' + paragraph

def extract_between_regex(text, start, end):
    pattern = re.escape(start) + r"(.*?)" + re.escape(end)
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None

def bedrock_response(user_input):
    messages = ''
    agent_id = "ODDCTBTDQT"
    agent_alias_id = "GPFHF7I8TW"
    region = "us-east-1"  # Example region
    full_response = ''
    # Generate a session ID (can persist across calls)
    session_id = str(uuid.uuid4())
    bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name=region)
    try:
    # Invoke the agent
        response = bedrock_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText= user_input            
        )
       
        for event in response['completion']:
            if 'chunk' in event:
                content = event['chunk']['bytes'].decode('utf-8')
                print(content)
                messages += content        
        print('messages',messages)    
    except Exception as e:
        print(f"Error invoking Bedrock Agent: {e}")
        messages =f'Error invoking Bedrock Agent: {e}'

    return messages 

def uml_code_generate(uml):
    after_rm = remove_include_lines(uml)
    print('after_rm', after_rm)
    after_add = add_lines_to_start(after_rm,import_lines)
    print('after_add', after_add)   
    after_add2 = after_add.replace('SimpleStorageServiceS3(', 'SimpleStorageService(').replace('ELBApplicationLoadBalancer(', 'ElasticLoadBalancingApplicationLoadBalancer(').replace('WAFSecurityAutomations(', 'WAF(').replace('IAM(', 'IAMIdentityCenter(').replace('RDSAurorainstance(', 'Aurorainstance(')
    after_add2 =  re.sub(r'^S3\(', 'SimpleStorageService(', after_add2) 
    print('after_add2', after_add2)
    return after_add2

def s3_url_generate(messages):

    try:
        uml = extract_between_regex(messages, "@startuml", "@enduml")
        if uml is not None:
            filter_uml_code = uml_code_generate(uml)
            uml_code1 = f""" \n{filter_uml_code}\n  @enduml """
            print('uml_code1', uml_code1)

            # Save to a .puml file
            with open('/tmp/diagram.puml', 'w') as f:
                f.write(uml_code1)

            # Generate image
            server.processes_file('/tmp/diagram.puml')
            print("Image generated.")

            local_file_path = '/tmp/diagram.png'  # Make sure this file exists

            # S3 destination
            bucket_name = 'plantuml-image'
            s3_object_key = 'uploads/diagram.png'

            # Check if the file exists before upload
            if os.path.exists(local_file_path):
                s3_client = boto3.client('s3')
                try:
                    s3_client.upload_file(local_file_path, bucket_name, s3_object_key)
                    print(f"Uploaded {local_file_path} to s3://{bucket_name}/{s3_object_key}")
                    presigned_url = s3.generate_presigned_url('get_object',Params={'Bucket': bucket_name, 'Key': s3_object_key},ExpiresIn=3600)
                    print("Presigned URL:", presigned_url)
                    presigned_link =f'Please click on this <a href="{presigned_url}" target="_blank">link</a> to download the architecture diagram.'
                    return presigned_link
                except Exception as e:
                    print("Upload failed:", str(e))
            else:
                print(f"File not found: {local_file_path}")

    except PlantUMLHTTPError as e:
        print("Failed to render PlantUML diagram:")
        print(str(e))  

def get_with_retry(user_input,retries, delay):
    response = ''    
    for attempt in range(retries + 1):  # total attempts = retries + 1
        try:
            messages = bedrock_response(user_input)
            if '@startuml' in messages:
                response += s3_url_generate(messages)
                # return response
                break
            if attempt < retries:
                response += messages
                print(f"Result was None. Retrying... ({attempt + 1}/{retries})")
        
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries:
                print(f"Result was exception. Retrying... ({attempt + 1}/{retries})")
                response = ''
            else:
                response = f"Failed after {retries} attempts: {e}"
    return response


def lambda_handler(event, context):   
    user_input = event['body']
    input = f'Generate PlantUML code for this: {user_input}'
    response = get_with_retry(input,0, 1)   
    return {
        'statusCode': 200,
        'body': response
    }

# "anthropic.claude-3-5-sonnet-20240620-v1:0"
# "You are an expert at generating PlantUML diagrams from text. Respond with only valid PlantUML code." "The AWS Solutions Architect role is a key position in cloud-focused organizations, responsible for designing and implementing scalable, secure, and cost-efficient solutions using AWS services."