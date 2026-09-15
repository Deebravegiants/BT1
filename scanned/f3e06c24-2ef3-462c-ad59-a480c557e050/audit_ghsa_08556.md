# [C] amazon-redshift-python-driver vulnerable to Remote Code Execution via eval() Injection

## Summary
Severity: Critical
Advisory: GHSA-29h4-r29x-hchv
CVE: CVE-2026-8838
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-29h4-r29x-hchv
Type: github-advisory

## Affected
- PyPI: `redshift-connector` — affected >=0 <2.1.14

## Details
### Summary
amazon-redshift-python-driver is the official Python connector for Amazon Redshift. In versions 2.1.13 and earlier, the driver insufficiently validates data received from the server during query result processing. A rogue server or man-in-the-middle could leverage this to execute arbitrary code on the client.

### Impact
When a client connects to a rogue server implementing the PostgreSQL wire protocol, the server can send specially crafted query responses that the driver processes without adequate input validation. This could result in arbitrary code execution in the client process, potentially enabling command execution, file system access, or credential theft with the privileges of the client application.

Impacted versions: <=2.1.13

### Patches
This has been addressed in amazon-redshift-python-driver version 2.1.14 (https://github.com/aws/amazon-redshift-python-driver/releases/tag/v2.1.14). Amazon Redshift recommends upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

### References
If there are any questions or comments about this advisory, contact AWS Security via the issue reporting page or directly via email to aws-security@amazon.com. Please do not create a public GitHub issue.

### Acknowledgement
Amazon Redshift would like to thank Kexin Chen (@ckx-sec) for collaborating through the coordinated disclosure process.

## References
- https://github.com/aws/amazon-redshift-python-driver/security/advisories/GHSA-29h4-r29x-hchv
- https://nvd.nist.gov/vuln/detail/CVE-2026-8838
- https://github.com/aws/amazon-redshift-python-driver/commit/69a69dfdead75918e20384da52bcd760ded8dbca
- https://aws.amazon.com/security/security-bulletins/2026-033-aws
- https://github.com/aws/amazon-redshift-python-driver
- https://github.com/aws/amazon-redshift-python-driver/releases/tag/v2.1.14
