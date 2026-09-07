# [M] aws-cdk-lib has Insertion of Sensitive Information into Log File vulnerability when using Cognito UserPoolClient Construct

## Summary
Severity: Medium
Advisory: GHSA-qq4x-c6h6-rfxh
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-31
Source: https://github.com/advisories/GHSA-qq4x-c6h6-rfxh
Type: github-advisory

## Affected
- npm: `aws-cdk-lib` — affected >=2.37.0 <2.187.0

## Details
### Summary
The [AWS Cloud Development Kit (CDK)](https://aws.amazon.com/cdk/) is an open-source framework for defining cloud infrastructure using code. Customers use it to create their own applications which are converted to AWS CloudFormation templates during deployment to a customer’s AWS account. CDK contains pre-built components called "[constructs](https://docs.aws.amazon.com/cdk/v2/guide/constructs.html)" that are higher-level abstractions providing defaults and best practices. This approach enables developers to use familiar programming languages to define complex cloud infrastructure more efficiently than writing raw CloudFormation templates.

The CDK [Cognito UserPool](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cognito.UserPool.html) construct deploys an AWS cognito user pool. An [Amazon Cognito user pool](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools.html) is a user directory for web and mobile app authentication and authorization. Customers can deploy a client under this user pool through construct ‘[UserPoolClient](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cognito.UserPoolClient.html)’ or through helper method '[addClient](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cognito.UserPool.html#addwbrclientid-options)'. A user pool client resource represents an Amazon [Cognito user pool client](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-client-apps.html) which is a configuration within a user pool that interacts with one mobile or web application authenticating with Amazon Cognito. 


When users of the 'cognito.UserPoolClient' construct generate a secret value for the application client in AWS CDK, they can then reference the generated secrets in their stack. The CDK had an issue where, when the custom resource performed an SDK API call to 'DescribeCognitoUserPoolClient' to retrieve the generated secret, the full response was logged in the associated lambda function's log group. Any user authenticated in the account where logs of the custom resource are accessible and who has read-only permission could view the secret written to those logs. 

This issue does not affect customers who are generating the secret value outside of the CDK as the secret is not referenced or logged.

### Impact
To leverage this issue, an actor has to be authenticated in the account where logs of the custom resource Custom::DescribeCognitoUserPoolClient are accessible and have read-only permission for lambda function logs. 

Users can review access to their log group through AWS CloudTrail logs to detect any unexpected access to read the logs.

**Impacted versions: >2.37.0 and <=2.187.0**

### Patches
The patches are included in the AWS CDK Library release v2.187.0. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes. To fully address this issue, users should rotate the secret by generating a new secret stored in AWS Secrets Manager. References to the secret will use the new secret on update. 

When new CDK applications using the latest version are initialized, they will use the new behavior with updated logging. 

Existing applications must upgrade to the latest version, change the [feature flag](https://github.com/aws/aws-cdk/blob/main/packages/aws-cdk-lib/cx-api/FEATURE_FLAGS.md) (@aws-cdk/cognito:logUserPoolClientSecretValue) to false, redeploy the application to apply this fix and use the new implementation with updated logging behavior.

### Workarounds
Users can override the implementation changing Logging to be Logging.withDataHidden(). For example define class CustomUserPoolClient extends UserPoolClient and  in the new class define get userPoolClientSecret() to use Logging.withDataHidden().



Example

    export class CustomUserPoolClient extends UserPoolClient {

      private readonly customUserPool : UserPool;
      private readonly customuserPoolClientId : string;
      constructor(scope: Construct, id: string, props: UserPoolClientProps) {
        super(scope, id, props);

        this.customUserPool = new UserPool(this, 'pool', {
          removalPolicy: RemovalPolicy.DESTROY,
        });

        const client = this.customUserPool.addClient('client', { generateSecret: true });
      }



      // Override the userPoolClientSecret getter to always return the secret
      public get userPoolClientSecret(): SecretValue {
        // Create the Custom Resource that assists in resolving the User Pool Client secret
        const secretValue = SecretValue.resourceAttribute(new AwsCustomResource(
          this,
          'DescribeCognitoUserPoolClient',
          {
        resourceType: 'Custom::DescribeCognitoUserPoolClient',
        onUpdate: {
          region: cdk.Stack.of(this).region,
          service: 'CognitoIdentityServiceProvider',
          action: 'describeUserPoolClient',
          parameters: {
            UserPoolId: this.customUserPool.userPoolId,
            ClientId: this.customUserPool,
          },
          physicalResourceId: PhysicalResourceId.of(this.userPoolClientId),
          // Disable logging of sensitive data
          logging: Logging.withDataHidden(),
        },
        policy: AwsCustomResourcePolicy.fromSdkCalls({
          resources: [this.customUserPool.userPoolArn],
        }),
        installLatestAwsSdk: false,
          },
        ).getResponseField('UserPoolClient.ClientSecret'));
        
        return secretValue;
      }
    }



### References
If you have any questions or comments about this advisory please contact AWS/Amazon Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/aws-cdk/security/advisories/GHSA-qq4x-c6h6-rfxh
- https://github.com/aws/aws-cdk/commit/d02e64aac18a72195ddcdb973defea7f32382c33
- https://github.com/aws/aws-cdk
