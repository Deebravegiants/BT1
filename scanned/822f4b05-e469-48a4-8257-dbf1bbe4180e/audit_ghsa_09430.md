# [C] Amazon Redshift Vulnerable to Remote Code Execution via Unsafe Class Loading

## Summary
Severity: Critical
Advisory: GHSA-wmmv-vvg5-993q
CVE: CVE-2026-8178
CWE: CWE-470
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-wmmv-vvg5-993q
Type: github-advisory

## Affected
- Maven: `com.amazon.redshift:redshift-jdbc42` — affected >=0 <2.2.2

## Details
### Summary
Amazon Redshift JDBC Driver is a Type 4 JDBC driver that provides database connectivity through the standard JDBC application program interfaces (APIs). An issue exists in versions prior to 2.2.2 where the driver could load arbitrary classes when processing certain connection URL parameters, potentially allowing code execution in the application context.

### Impact
When a JDBC connection URL contains certain parameters, the driver processes the parameter values in a way that could trigger the execution of code from classes available on the application's classpath. An actor who can influence the JDBC connection URL could leverage this to execute code in the context of the application's JVM process. Successful exploitation could allow the actor to read sensitive data, modify application state, or disrupt service availability with the privileges of the application process.

Impacted versions: Amazon Redshift JDBC Driver < 2.2.2

### Patches
This issue has been addressed in Amazon Redshift JDBC Driver version [2.2.2](https://github.com/aws/amazon-redshift-jdbc-driver/releases/tag/v2.2.2). We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

### References
If you have any questions or comments about this advisory, we ask that you contact AWS Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

### Acknowledgement
We would like to thank [Fushuling](https://github.com/Fushuling) for collaborating on this issue through the coordinated issue disclosure process.

## References
- https://github.com/aws/amazon-redshift-jdbc-driver/security/advisories/GHSA-wmmv-vvg5-993q
- https://nvd.nist.gov/vuln/detail/CVE-2026-8178
- https://aws.amazon.com/security/security-bulletins/2026-028-aws
- https://github.com/aws/amazon-redshift-jdbc-driver
- https://github.com/aws/amazon-redshift-jdbc-driver/releases/tag/v2.2.2
