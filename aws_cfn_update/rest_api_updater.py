#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   Copyright 2018 binx.io B.V.
import sys

from .cfn_updater import CfnUpdater
from ruamel.yaml import YAML


class RestAPIUpdater(CfnUpdater):
    """
    Updates the body of a REST API Resource, merging the official swagger
    API definiition with the AWS API Gateway extensions.
    """

    def __init__(self):
        super(RestAPIUpdater, self).__init__()
        self.resource_name = None
        self.swagger_file = None
        self.api_gateway_extension = None
        self.template = None
        self.verbose = False
        self.dry_run = False

    def load_and_merge_swagger_body(self):
        yaml = YAML()
        with open(self.swagger_file, 'r') as f:
            body = yaml.load(f)
        with open(self.api_gateway_extension, 'r') as f:
            extensions = yaml.load(f)

        for path, path_configuration in body['paths'].items():
            for operation, operation_configuration in path_configuration.items():
                if path in extensions['paths']:
                    if operation in extensions['paths'][path]:
                        for name, value in extensions['paths'][path][operation].items():
                            if name in operation_configuration:
                                sys.stderr.write(
                                    'WARN: overwriting property {} on operation {} in path {}\n'.format(name, operation,
                                                                                                        path))
                            operation_configuration[name] = value
                    else:
                        sys.stderr.write(
                            'WARN: API Gateway does not provide support for operation {} on path {}\n'.format(operation,
                                                                                                              path))
                else:
                    sys.stderr.write(
                        'WARN: API Gateway does not provide support for operations on path {}\n'.format(path))
        return body

    def update_template(self):
        rest_api_gateway = self.template['Resources'][self.resource_name] if self.resource_name in self.template[
            'Resources'] else None
        type = rest_api_gateway['Type'] if rest_api_gateway and 'Type' in rest_api_gateway else None

        if not rest_api_gateway:
            sys.stderr.write(
                'ERROR: no resource found with the name {} in template {}\n'.format(self.resource_name, self.filename))
            sys.exit(1)

        if not type or type != 'AWS::ApiGateway::RestApi':
            sys.stderr.write(
                'ERROR: resource {} in template {} is not of type AWS::ApiGateway::RestApi\n'.format(self.resource_name,
                                                                                                     self.filename))
            sys.exit(1)

        body = self.load_and_merge_swagger_body()
        current_body = rest_api_gateway['Properties']['Body'] if 'Body' in rest_api_gateway['Properties'] else {}

        if body != current_body:
            sys.stderr.write('INFO: updating swagger body of {} in template {}'.format(self.resource_name,self.filename))
            if self.dry_run:
                return
            if not 'Properties' in rest_api_gateway:
                rest_api_gateway['Properties'] = {}

            rest_api_gateway['Properties']['Body'] = body
            self.dirty = True
        else:
            sys.stderr.write('INFO: no changes of swagger body of {} in template {}'.format(self.resource_name,self.filename))


    def main(self, resource_name, swagger_file, api_gateway_extension, template, dry_run, verbose):
        self.dry_run = dry_run
        self.verbose = verbose
        self.resource_name = resource_name
        self.swagger_file = swagger_file
        self.api_gateway_extension = api_gateway_extension
        self.update([template])
