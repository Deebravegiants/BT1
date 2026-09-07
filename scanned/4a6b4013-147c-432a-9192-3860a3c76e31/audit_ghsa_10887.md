# [H] AWS SDK for Java 2.0: Improper Handling of Special Characters in CloudFront Signing Utilities

## Summary
Severity: High
Advisory: GHSA-443w-3rq3-5m5h
CWE: CWE-116, CWE-20
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-443w-3rq3-5m5h
Type: github-advisory

## Affected
- Maven: `software.amazon.awssdk:cloudfront` — affected >=2.18.33 <2.41.30

## Details
### Summary
This notification is related to the [CloudFront signing utilities](https://github.com/aws/aws-sdk-java-v2/blob/master/services/cloudfront/src/main/java/software/amazon/awssdk/services/cloudfront/CloudFrontUtilities.java) in the AWS SDK for Java v2, which are used to generate Amazon CloudFront signed URLs and signed cookies. A defense-in-depth enhancement has been implemented to improve handling of special characters, such as double quotes and backslashes, in input values.
### Impact
The CloudFront signing utilities build policy documents that define access restrictions for signed URLs and cookies. If an application passes unsanitized input containing special characters to these utilities, the resulting policy document may not reflect the application's intended access restrictions. While the SDK was functioning safely within the requirements of the shared responsibility model, additional safeguards have been added to support secure customer implementations. Applications that already follow AWS security best practices for input validation are not impacted.
### Impacted versions: 
2.18.33 - 2.41.29
### Patches
On 2026.02.16, an enhancement was made to AWS SDK for Java v2 version 2.41.30. The enhancement ensures that special characters in input values are correctly handled. We recommend upgrading to the latest version.
### Workarounds
No workarounds are needed, but customers should ensure that your application is following security best practices:

* Implement proper input validation in your application code before passing values to CloudFront signing utilities
* Update to the latest AWS SDK release on a regular basis
* Follow [AWS security best practices for SDK configuration](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/security.html)

### Resources
If there are any questions or comments about this advisory, contact [AWS/Amazon] Security via our vulnerability reporting page or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.
### Acknowledgement
AWS SDK for Java 2.0 thanks the Amazon Inspector Security Research team for identifying this issue and working with us through the coordinated process.

## References
- https://github.com/aws/aws-sdk-java-v2/security/advisories/GHSA-443w-3rq3-5m5h
- https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/security.html
- https://github.com/aws/aws-sdk-java-v2
- https://github.com/aws/aws-sdk-java-v2/blob/master/services/cloudfront/src/main/java/software/amazon/awssdk/services/cloudfront/CloudFrontUtilities.java
