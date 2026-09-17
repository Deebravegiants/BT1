# [H] Amazon.IonDotnet is vulnerable to Denial of Service attacks

## Summary
Severity: High
Advisory: GHSA-q5r6-9qwq-g2wj
CVE: CVE-2025-11573
CWE: CWE-1286, CWE-400
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-09
Source: https://github.com/advisories/GHSA-q5r6-9qwq-g2wj
Type: github-advisory

## Affected
- NuGet: `Amazon.IonDotnet` — affected >=0 <1.3.2

## Details
### Summary
Amazon.IonDotnet is a library for the Dotnet language that is used to read and write Amazon Ion data. An issue exists where, under certain circumstances, the library could an infinite loop, resulting in denial of service. As of August 20, 2025, this library has been deprecated and will not receive further updates.

### Impact
An infinite loop issue in Amazon.IonDotnet library versions <v1.3.2 may allow a threat actor to cause a denial of service through a specially crafted text input. This invalid input triggered an error condition in the parser that was handled improperly, resulting in an infinite loop.

### Impacted versions:
<1.3.2

### Patches
This issue has been addressed in Amazon.IonDotnet version [1.3.2](https://www.nuget.org/packages/Amazon.IonDotnet/1.3.2). We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

### Workarounds
Only accept data from trusted sources, written using a supported Ion library.

### References
If you have any questions or comments about this advisory, we ask that you contact AWS Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/amazon-ion/ion-dotnet/security/advisories/GHSA-q5r6-9qwq-g2wj
- https://nvd.nist.gov/vuln/detail/CVE-2025-11573
- https://github.com/amazon-ion/ion-dotnet/pull/160
- https://github.com/amazon-ion/ion-dotnet/commit/edaff75fe5abbb71e647bed812c608c0c5e2fbab
- https://aws.amazon.com/security/security-bulletins/AWS-2025-022
- https://github.com/amazon-ion/ion-dotnet
- https://github.com/amazon-ion/ion-dotnet/releases/tag/v1.3.2
