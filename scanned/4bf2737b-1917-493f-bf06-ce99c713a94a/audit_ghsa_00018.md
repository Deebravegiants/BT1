# [H] Improper Restriction of XML External Entity Reference in bedework:bw-webdav

## Summary
Severity: High
Advisory: GHSA-5p52-j8pw-j7x5
CVE: CVE-2018-20000
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-12-19
Source: https://github.com/advisories/GHSA-5p52-j8pw-j7x5
Type: github-advisory

## Affected
- Maven: `org.bedework:bw-webdav` — affected >=4.0.1 <4.0.3

## Details
Apereo Bedework bw-webdav before 4.0.3 allows XXE attacks, as demonstrated by an invite-reply document that reads a local file, related to webdav/servlet/common/MethodBase.java and webdav/servlet/common/PostRequestPars.java.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20000
- https://github.com/Bedework/bw-webdav/pull/1
- https://github.com/Bedework/bw-webdav
- https://github.com/Bedework/bw-webdav/compare/bw-webdav-4.0.2...bw-webdav-4.0.3
- https://github.com/advisories/GHSA-5p52-j8pw-j7x5
