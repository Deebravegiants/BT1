# [H] Apache Archiva vulnerable to Sensitive Information Disclosure via anonymous user

## Summary
Severity: High
Advisory: GHSA-463w-hxfv-g9f6
CVE: CVE-2022-40308
CWE: CWE-200, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-15
Source: https://github.com/advisories/GHSA-463w-hxfv-g9f6
Type: github-advisory

## Affected
- Maven: `org.apache.archiva:archiva-common` — affected >=0 <2.2.9

## Details
Apache Archiva prior to 2.2.9 may allow the anonymous user to read arbitrary files. If anonymous read enabled, it's possible to read the database file directly without logging in.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40308
- https://archiva.apache.org/security.html
- https://github.com/apache/archiva
- https://lists.apache.org/thread/x01pnn0jjsw512cscxsbxzrjmz64n4cc
- http://www.openwall.com/lists/oss-security/2022/11/15/2
