import boto3


print("Creating EC2 Instance")
resource_ec2 = boto3.client("ec2")

resource_keypair = resource_ec2.create_key_pair(
    KeyName = "ansible-key"
)

key_material = resource_keypair['KeyMaterial']
with open("ansible-key.pem", "w") as key_file:
    key_file.write(key_material)
print("Key pair saved as key2.pem")

resource_vpc = resource_ec2.create_vpc(
    CidrBlock = '172.32.0.0/16'
)

vpc_id = resource_vpc['Vpc']['VpcId']

resource_subnet = resource_ec2.create_subnet(
    CidrBlock = '172.32.1.0/24',
    AvailabilityZone='ap-south-1a',
    VpcId = vpc_id
)

subnet_id = resource_subnet['Subnet']['SubnetId']

resource_igw = resource_ec2.create_internet_gateway()
internet_gateway_id = resource_igw['InternetGateway']['InternetGatewayId']

resource_ec2.attach_internet_gateway(
    InternetGatewayId=internet_gateway_id,
    VpcId=vpc_id
)

resource_route_table = resource_ec2.create_route_table(
    VpcId=vpc_id
)
route_table_id = resource_route_table['RouteTable']['RouteTableId']

resource_ec2.create_route(
    RouteTableId=route_table_id,
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=internet_gateway_id
)

resource_ec2.associate_route_table(
    RouteTableId=route_table_id,
    SubnetId=subnet_id
)

resource_sec_grp = resource_ec2.create_security_group(
    Description = "practice security group for boto3 task",
    GroupName = "eSparkBiz-SecGrp-1",
    VpcId = vpc_id
)

secgrp_1 = resource_sec_grp['GroupId']

resource_sec_grp_ingress = resource_ec2.authorize_security_group_ingress(
    GroupId = secgrp_1,
    IpPermissions = [
        {
            "FromPort" : 22,
            "IpProtocol" : "tcp",
            "IpRanges" : [
                {
                    "CidrIp" : "0.0.0.0/0",
                    "Description" : "SSH Allowed",
                },
            ],
            "ToPort" : 22,
        },
        {
            "FromPort" : 80,
            "IpProtocol" : "tcp",
            "IpRanges" : [
                {
                    "CidrIp" : "0.0.0.0/0",
                    "Description" : "HTTP Allowed",
                },
            ],
            "ToPort" : 80,
        },
        {
            "FromPort" : 443,
            "IpProtocol" : "tcp",
            "IpRanges" : [
                {
                    "CidrIp" : "0.0.0.0/0",
                    "Description" : "HTTPS Allowed",
                },
            ],
            "ToPort" : 443,
        }
    ],
)

resource_ec2.run_instances(
    ImageId = "ami-05e00961530ae1b55",
    MinCount = 3,
    MaxCount = 3,
    InstanceType = "t2.micro",
    KeyName = "ansible-key",        
    NetworkInterfaces=[
    {
        'DeviceIndex': 0,
        'AssociatePublicIpAddress': True,
        'SubnetId' : subnet_id,
        'Groups' : [secgrp_1]
    }
    ]
)