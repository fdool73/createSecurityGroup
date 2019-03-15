def lambda_handler(event, context):

    import boto3
    from botocore.exceptions import ClientError
    import socket

    ec2 = boto3.client('ec2')
    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
    endpoints = [
    'ec2.eu-north-1.amazonaws.com','ec2.ap-south-1.amazonaws.com','ec2.eu-west-3.amazonaws.com','ec2.eu-west-2.amazonaws.com',
     'ec2.eu-west-1.amazonaws.com','ec2.ap-northeast-2.amazonaws.com','ec2.ap-northeast-1.amazonaws.com',
    'ec2.sa-east-1.amazonaws.com','ec2.ca-central-1.amazonaws.com','ec2.ap-southeast-1.amazonaws.com',
     'ec2.ap-southeast-2.amazonaws.com','ec2.eu-central-1.amazonaws.com','ec2.us-east-1.amazonaws.com',
    'ec2.us-east-2.amazonaws.com','ec2.us-west-1.amazonaws.com','ec2.us-west-2.amazonaws.com'
    ]

    response = ec2.create_security_group(GroupName='web-outbound',
                                         Description='Allow HTTP and HTTPS to all Amazon EC2 endpoints',
                                         VpcId=vpc_id)
    security_group_id = response['GroupId']
    revoke = ec2.revoke_security_group_egress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': '-1',
             'FromPort': -1,
             'ToPort': -1,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
        ]
    )
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

    for item in endpoints:
        cidr = socket.gethostbyname(item)
        response = ec2.authorize_security_group_egress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 80,
                 'ToPort': 80,
                 'IpRanges': [{'CidrIp': str(cidr)+'/32'}]},
                {'IpProtocol': 'tcp',
                 'FromPort': 443,
                 'ToPort': 443,
                 'IpRanges': [{'CidrIp': str(cidr)+'/32'}]}
            ])
