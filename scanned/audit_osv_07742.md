# [C] Apache Tomcat: Redirect after FORM auth may bypass method specific constraints

## Summary
Severity: Critical
Advisory: BIT-tomcat-2026-68525
Aliases: CVE-2026-68525, GHSA-h3x4-894j-xpx5
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-68525
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.25

## Details
Incorrect Authorization vulnerability in Apache Tomcat's FORM authentication process allows the bypassing of a security constraint that limits user has access to a resource POST but not GET.







This issue affects Apache Tomcat: from 11.0.0 through 11.0.24, from 10.1.0 through 10.1.57, from 9.0.0 through 9.0.120.







The following versions were EOL at the time the CVE was created but are 
known to be affected: from 8.5.0 through 8.5.100, from 7.0.0 through 7.0.109. Other unsupported versions may also be affected.















Users are recommended to upgrade to version 11.0.25, 10.1.58 or 9.0.121, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/26/7
- https://lists.apache.org/thread/x1y2lfsgzxwzc456f8954vbvgn03zhd7
- https://nvd.nist.gov/vuln/detail/CVE-2026-68525
