# [H] com.amazon.redshift:redshift-jdbc42 vulnerable to remote command execution

## Summary
Severity: High
Advisory: GHSA-jc69-hjw2-fm86
CVE: CVE-2022-41828
CWE: CWE-704
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2022-10-12
Source: https://github.com/advisories/GHSA-jc69-hjw2-fm86
Type: github-advisory

## Affected
- Maven: `com.amazon.redshift:redshift-jdbc42` — affected >=0 <2.1.0.8

## Details
### Impact

A potential remote command execution issue exists within `redshift-jdbc42` versions 2.1.0.7 and below. When plugins are used with the driver, it instantiates plugin instances based on Java class names provided via the `sslhostnameverifier`, `socketFactory`, `sslfactory`, and `sslpasswordcallback` connection properties. In affected versions, the driver does not verify if a plugin class implements the expected interface before instantiatiaton. This can lead to loading of arbitrary Java classes, which a knowledgeable attacker with control over the JDBC URL can use to achieve remote code execution.

### Patches

This issue is patched within `redshift-jdbc-42` 2.1.0.8 and above.

### Workarounds

We advise customers using plugins to upgrade to `redshift-jdbc42` version 2.1.0.8 or above. There are no known workarounds for this issue.

### For more information

If you have any questions or comments about this advisory, please contact AWS Security at [aws-security@amazon.com](mailto:aws-security@amazon.com).

## References
- https://github.com/aws/amazon-redshift-jdbc-driver/security/advisories/GHSA-jc69-hjw2-fm86
- https://nvd.nist.gov/vuln/detail/CVE-2022-41828
- https://github.com/aws/amazon-redshift-jdbc-driver/commit/40b143b4698faf90c788ffa89f2d4d8d2ad068b5
- https://github.com/aws/amazon-redshift-jdbc-driver/commit/9999659bbc9f3d006fb02a0bf39d5bcf3b503605
- https://github.com/aws/amazon-redshift-jdbc-driver
