# [H] AWS SDK for PHP has CloudFront Policy Document Injection via Special Characters

## Summary
Severity: High
Advisory: GHSA-27qh-8cxx-2cr5
CWE: CWE-150, CWE-20, CWE-74
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-27qh-8cxx-2cr5
Type: github-advisory

## Affected
- Packagist: `aws/aws-sdk-php` — affected >=3.11.7 <3.371.4

## Details
### Summary

This notification is related to the [CloudFront signing utilities](https://github.com/aws/aws-sdk-php/blob/master/src/CloudFront/Signer.php) in the AWS SDK for PHP, which are used to generate Amazon CloudFront signed URLs and signed cookies. A defense-in-depth enhancement has been implemented to improve handling of special characters, such as double quotes and backslashes, in input values.

### Impact

The CloudFront signing utilities build policy documents that define access restrictions for signed URLs and cookies. If an application passes unsanitized input containing special characters to these utilities, the resulting policy document may not reflect the application's intended access restrictions. While the SDK was functioning safely within the requirements of the shared responsibility model, additional safeguards have been added to support secure customer implementations. Applications that already follow AWS security best practices for input validation are not impacted.

### Impacted versions: 3.11.7 - 3.371.3

### Patches

On 3/3/2026, an enhancement was made to the AWS SDK for PHP version 3.371.4. The enhancement ensures that special characters in input values are correctly handled. It is recommended to upgrade to the latest version.

### Workarounds

No workarounds are needed, but customers should ensure that the application is following security best practices:

- Implement proper input validation in application code before passing values to CloudFront signing utilities
- Update to the latest AWS SDK release on a regular basis
- Follow AWS security best practices for SDK configuration

### References

For any questions or comments about this advisory, it is recommended to contact AWS Security via the [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

### Acknowledgement

The Amazon Inspector Security Research team is thanked for identifying this issue and working through the coordinated process.

## References
- https://github.com/aws/aws-sdk-php/security/advisories/GHSA-27qh-8cxx-2cr5
- https://github.com/aws/aws-sdk-php
- https://github.com/aws/aws-sdk-php/blob/master/src/CloudFront/Signer.php
- https://github.com/aws/aws-sdk-php/releases/tag/3.371.4
