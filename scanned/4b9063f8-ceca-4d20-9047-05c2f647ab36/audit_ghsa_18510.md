# [H] Apache Jena doesn't validate file access paths in configuration files uploaded by users with administrator access

## Summary
Severity: High
Advisory: GHSA-xg9p-p463-3qjp
CVE: CVE-2025-50151
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-21
Source: https://github.com/advisories/GHSA-xg9p-p463-3qjp
Type: github-advisory

## Affected
- Maven: `org.apache.jena:jena` — affected >=0 <5.5.0

## Details
File access paths in configuration files uploaded by users with administrator access are not validated.

This issue affects Apache Jena version up to 5.4.0.

Users are recommended to upgrade to version 5.5.0, which does not allow arbitrary configuration upload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-50151
- https://github.com/apache/jena
- https://lists.apache.org/thread/12gks5z40gh9bszn1xk8mz34gz586xss
- http://www.openwall.com/lists/oss-security/2025/07/21/2
