# [H] Apache UIMA Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-xgqr-5wqw-9fpv
CVE: CVE-2022-32287
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-11-03
Source: https://github.com/advisories/GHSA-xgqr-5wqw-9fpv
Type: github-advisory

## Affected
- Maven: `org.apache.uima:uimaj-core` — affected >=0 <3.3.1

## Details
A relative path traversal vulnerability in a FileUtil class used by the PEAR management component of Apache UIMA allows an attacker to create files outside the designated target directory using carefully crafted ZIP entry names. This issue affects Apache UIMA Apache UIMA version 3.3.0 and prior versions. Note that PEAR files should never be installed into an UIMA installation from untrusted sources because PEAR archives are executable plugins that will be able to perform any actions with the same privileges as the host Java Virtual Machine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32287
- https://lists.apache.org/thread/57vk0d79j94d0lk0vol8xn935yv1shdd
- http://www.openwall.com/lists/oss-security/2022/11/03/4
