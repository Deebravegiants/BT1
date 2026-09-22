# [H] AWS SDK for .NET: Improper escaping of special characters in CloudFront policy document construction

## Summary
Severity: High
Advisory: GHSA-mvm6-f9r3-fgfx
CWE: CWE-116, CWE-20
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-mvm6-f9r3-fgfx
Type: github-advisory

## Affected
- NuGet: `AWSSDK.CloudFront` — affected >=0 <3.7.510.7
- NuGet: `AWSSDK.Extensions.CloudFront.Signers` — affected >=4.0.0.0 <4.0.0.26

## Details
### Summary 
This notification is related to the CloudFront signing utilities in the AWS SDK for .NET, which are used to generate Amazon CloudFront signed URLs and signed cookies. A defense-in-depth enhancement has been implemented to improve handling of special characters, such as double quotes and backslashes, in input values. 

### Impact 
The CloudFront signing utilities build policy documents that define access restrictions for signed URLs and cookies. If an application passes unsanitized input containing special characters to these utilities, the resulting policy document may not reflect the application's intended access restrictions. While the SDK was functioning safely within the requirements of the shared responsibility model, additional safeguards have been added to support secure customer implementations. Applications that already follow AWS security best practices for input validation are not impacted. 

### Impacted versions: 
- AWS SDK for .NET V3 (`AWSSDK.CloudFront`): < 3.7.510.7
- AWS SDK for .NET V4 (`AWSSDK.Extensions.CloudFront.Signers`): 4.0.0.0 - 4.0.0.25 

### Patches 
On February 25th, 2026, an enhancement was made to the AWS SDK for .NET CloudFront signing utilities. The enhancement ensures that special characters in input values are correctly handled. We recommend upgrading to the latest version. 

### Workarounds 
No workarounds are needed, but customers should ensure that your application is following security best practices: 
- Implement proper input validation in your application code before passing values to CloudFront signing utilities 
- Update to the latest AWS SDK release on a regular basis 
- Follow AWS security best practices for SDK configuration

### References 
If there are any questions or comments about this advisory, contact AWS Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

### Acknowledgement
AWS SDK for .NET thanks the Amazon Inspector Security Research team for identifying this issue and working through the coordinated process together.

## References
- https://github.com/aws/aws-sdk-net/security/advisories/GHSA-mvm6-f9r3-fgfx
- https://github.com/aws/aws-sdk-net
