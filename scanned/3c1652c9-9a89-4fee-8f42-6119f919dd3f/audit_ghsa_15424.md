# [M] AWS CDK RestApi not generating authorizationScope correctly in resultant CFN template

## Summary
Severity: Medium
Advisory: GHSA-qj85-69xf-2vxq
CVE: CVE-2024-45037
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-27
Source: https://github.com/advisories/GHSA-qj85-69xf-2vxq
Type: github-advisory

## Affected
- npm: `aws-cdk` — affected >=2.142.0 <2.148.1

## Details
### Summary
The AWS Cloud Development Kit (CDK) is an open-source framework for defining cloud infrastructure using code. Customers use it to create their own applications which are converted to AWS CloudFormation templates during deployment to a customer’s AWS account. CDK contains pre-built components called "constructs" that are higher-level abstractions providing defaults and best practices. This approach enables developers to use familiar programming languages to define complex cloud infrastructure more efficiently than writing raw CloudFormation templates. 

We identified an issue in AWS Cloud Development Kit (CDK) which, under certain conditions, can result in granting authenticated Amazon Cognito users broader than intended access. Specifically, if a CDK application uses the "RestApi" construct with "CognitoUserPoolAuthorizer" as the authorizer and uses authorization scopes to limit access. This issue does not affect the availability of the specific API resources. 

### Impact
Authenticated Cognito users may gain unintended access to protected API resources or methods, leading to potential data disclosure, and modification issues. 

Impacted versions: >=2.142.0;<=2.148.0

### Patches
The patch is included in CDK version >=2.148.1.

### Recommended Actions
* Upgrade your AWS CDK version to 2.148.1 or newer and re-deploy your application(s) to address this issue.
* If you are using older CDK versions before 2.142.0, you are not affected by this issue, however it is recommended to upgrade to the latest version to receive the latest features and fixes.
* Confirm whether your application(s) is affected by searching for "CognitoUserPoolsAuthorizer" in your CDK application. If it is referenced inside the "RestApi" construct, and the "RestApi" resource or method utilize authorization scopes to limit access, and you deployed your applications using the impacted versions of CDK, your application is affected.



### References
* AWS CDK Documentation: https://docs.aws.amazon.com/cdk/v2/guide/home.html
* AWS CDK RestApi Construct Documentation: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-[lib.aws](http://lib.aws/)_apigateway.RestApi.html
* AWS CDK CognitoUserPoolsAuthorizer Documentation: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk- [lib.aws](http://lib.aws/)_apigateway.CognitoUserPoolsAuthorizer.html 
* AWS CDK v2.148.1 Release Notes: https://github.com/aws/aws-cdk/releases/tag/v2.148.1

If you have any questions or comments about this advisory we ask that you contact AWS/Amazon Security via our vulnerability reporting page [1] or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

[1] Vulnerability reporting page: https://aws.amazon.com/security/vulnerability-reporting

## References
- https://github.com/aws/aws-cdk/security/advisories/GHSA-qj85-69xf-2vxq
- https://nvd.nist.gov/vuln/detail/CVE-2024-45037
- https://github.com/aws/aws-cdk/commit/4bee768f07e73ab5fe466f9ad3d1845456a0513b
- https://docs.aws.amazon.com/cdk/v2/guide/home.html
- https://github.com/aws/aws-cdk
- https://github.com/aws/aws-cdk/releases/tag/v2.148.1
