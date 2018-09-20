# aws-cfn-update

Programmatically update CloudFormation templates. It will update both .yaml and .json formats of
a CloudFormation template. Note that formatting and comments may be lost.

Commands:
```
  container-image           Updates the Docker image of ECS Container...
  latest-ami                Updates the AMI name of Custom::AMI resources...
  cron-schedule-expression  Updates the schedule expression of an AWS::Events::Rules resources...
```

# container-image - Updates the Docker image of ECS Container Definitions.

will update any container definition where the base image name matches the specified image name 
excluding the tag. For example, the command:
```
aws-cfn-update container-image --image mvanholsteijn/paas-monitor:0.6.0
```
will update:

```yaml
  Type: AWS::ECS::TaskDefinition
  Properties:
    ContainerDefinitions:
      - Name: paas-monitor
        Image: mvanholsteijn/paas-monitor:0.5.9
```

to::

```yaml
  Type: AWS::ECS::TaskDefinition
  Properties:
    ContainerDefinitions:
      - Name: paas-monitor
        Image: mvanholsteijn/paas-monitor:0.6.0
```



# latest-ami - Updates the AMI name of Custom::AMI resources

will update the AMI name of [Custom::AMI](https://github.com/binxio/cfn-ami-provider) resources to the latest version.  

For example, the command: 

```
aws-cfn-update latest-ami --ami-name-pattern 'amzn-ami-*ecs-optimized'
```

Updates the AMI name of Custom::AMI resources to the latest version. 
It will update the following resource definition from:

```yaml
         Type: Custom::AMI
         Properties:
           Filters:
             name: amzn-ami-2017.09.a-amazon-ecs-optimized
           Owners:
             - amazon
```
to:

```yaml
         Type: Custom::AMI
         Properties:
           Filters:
             name: amzn-ami-2017.09.l-amazon-ecs-optimized
           Owners:
             - amazon
```

By specifying --add-new-version, a new Custom::AMI will be added
to the template with a new name. A suffix `v<version>` is appended
to create the new resource. Any reference to the original Custom::AMI
resource is replaced. It will change:

```yaml
      CustomAMI:
         Type: Custom::AMI
         Properties:
           Filters:
             name: amzn-ami-2017.09.a-amazon-ecs-optimized
           Owners:
             - amazon
      CustomAMIv2:`
         Type: Custom::AMI
         Properties:
           Filters:
             name: amzn-ami-2017.09.b-amazon-ecs-optimized
           Owners:
             - amazon
      Instance:
         Type: AWS::EC2::Instance
         Properties:
            ImageId: !Ref CustomAMIv2
```
to:

```yaml
      CustomAMI:
         Type: Custom::AMI
         Properties:
           Filters:
             name: amzn-ami-2017.09.a-amazon-ecs-optimized
           Owners:
             - amazon
      CustomAMIv2:
         Type: Custom::AMI
         Properties:
           Filters:
             name: amzn-ami-2017.09.b-amazon-ecs-optimized
           Owners:
             - amazon
      CustomAMIv3:
         Type: Custom::AMI
         Properties:
           Filters:
             name: amzn-ami-2017.09.l-amazon-ecs-optimized
           Owners:
             - amazon
      Instance:
         Type: AWS::EC2::Instance
         Properties:
            ImageId: !Ref CustomAMIv3
```


# container-image - Updates the Docker image of ECS Container Definitions.
Updates the schedule expression of an AWS::Events::Rules resources to
reflect the scheduled time in UTC. The required cron rule is taken
from the description. It will update the following resource definition from:

```
DailyTaskSchedule:
  Type: AWS::Events::Rule
  Properties:
    Description: run daily - cron(30 01 * * ? *)
    Name: run daily
    ScheduleExpression: cron(30 01 * * ? *)
    State: ENABLED
```

to:

```
DailyTaskSchedule:
  Type: AWS::Events::Rule
  Properties:
    Description: run daily - cron(30 01 * * ? *)
    Name: run daily
    ScheduleExpression: cron(30 23 * * ? *)
    State: ENABLED
```

with --timezone Europe/Amsterdam and --date 2018-08-01. If the updater is
run with --date 2018-12-01, it will change it to:

```
DailyTaskSchedule:
  Type: AWS::Events::Rule
  Properties:
    Description: run daily - cron(30 01 * * ? *)
    Name: run daily
    ScheduleExpression: cron(30 00 * * ? *)
    State: ENABLED
```


# Installation

Simply run:

```bash
pip install aws-cfn-update
```


# Usage

To use it:
```bash
aws-cfn-update --help
```

