# [M] AWS CDK CLI prints AWS credentials retrieved by custom credential plugins

## Summary
Severity: Medium
Advisory: GHSA-v63m-x9r9-8gqp
CVE: CVE-2025-2598
CWE: CWE-497
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-21
Source: https://github.com/advisories/GHSA-v63m-x9r9-8gqp
Type: github-advisory

## Affected
- npm: `aws-cdk` — affected >=2.172.0 <2.178.2
- npm: `cdk` — affected >=2.172.0 <2.178.2

## Details
## Summary

The AWS Cloud Development Kit (AWS CDK) [1] is an open-source software development framework for defining cloud infrastructure in code and provisioning it through AWS CloudFormation. The AWS CDK CLI [2] is a command line tool for interacting with CDK applications. Customers can use the CDK CLI to create, manage, and deploy their AWS CDK projects. 

An issue exists in the AWS CDK CLI where, under certain conditions, AWS credentials may be returned in the console output. Plugins that return an `expiration `property in the credentials object are affected by this issue. Plugins that omit the `expiration` property are not affected. 

## Impact

When customers run AWS CDK CLI commands with credential plugins and configure those plugins to return temporary credentials by including an `expiration` property, the AWS credentials retrieved by the plugin may be returned in the console output. Any user with access where the CDK CLI was ran would have access to this output. 

The following are examples of configuring a custom credential plugin: 

_Via command line option:_

`cdk deploy --plugin /path/to/plugin`

_Via configuration file [3]:_

```json
{
  "plugin": "/path/to/plugin"
}
```

Plugins that return an `expiration` property in the credentials object, such as the following example, are affected:

```console
return {
    accessKeyId: '<access-key>',
    secretAccessKey: '<secret-access-key>',
    sessionToken: '<session-token>',
    expiration: <date>,
};
```

The `expiration` property indicates that the provided credentials are temporary. 

Please refer to our "AWS CDK CLI Library" guide for more information about custom credential plugins [4].

## Impacted versions:  >=2.172.0 and <2.178.2

## Patches

The issue has been addressed in version 2.178.2 [5]. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes. 

## Workarounds

If you are unable to upgrade to version 2.178.2 or later, you can downgrade to version 2.171.1. If you are unable to downgrade, but have access to the code of the credential plugin you use, you can remove the `expiration` property from the object returned by the plugin.

For example, change the code from returning this:

```javascript
return {
    accessKeyId: assumeRoleOutput.Credentials.AccessKeyId,
    secretAccessKey: assumeRoleOutput.Credentials.SecretAccessKey,
    sessionToken: assumeRoleOutput.Credentials.SessionToken,

    // Expiration indicates to the CLI that this is temporary
    expiration: assumeRoleOutput.Credentials.Expiration,
};
```

To return this:

```javascript
return {
    accessKeyId: assumeRoleOutput.Credentials.AccessKeyId,
    secretAccessKey: assumeRoleOutput.Credentials.SecretAccessKey,
    sessionToken: assumeRoleOutput.Credentials.SessionToken,
};
```

Note that this will prevent the CDK CLI from refreshing the credentials when needed, and may cause your workflow to fail on an expired credentials error. 

## References

[1] https://docs.aws.amazon.com/cdk/v2/guide/home.html

[2] https://docs.aws.amazon.com/cdk/v2/guide/cli.html

[3] https://docs.aws.amazon.com/cdk/v2/guide/cli.html#cli-config

[4] https://www.npmjs.com/package/@aws-cdk/cli-plugin-contract

[5] https://github.com/aws/aws-cdk/releases/tag/v2.178.2

## References
- https://github.com/aws/aws-cdk/security/advisories/GHSA-v63m-x9r9-8gqp
- https://nvd.nist.gov/vuln/detail/CVE-2025-2598
- https://aws.amazon.com/security/security-bulletins/AWS-2025-005
- https://github.com/aws/aws-cdk
- https://github.com/aws/aws-cdk/releases/tag/v2.178.2
