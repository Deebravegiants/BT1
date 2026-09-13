# [M] Apache Jena allows users with administrator access to create databases files outside the files area of the Fuseki server

## Summary
Severity: Medium
Advisory: GHSA-jq2c-m8gg-mqcm
CVE: CVE-2025-49656
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-07-21
Source: https://github.com/advisories/GHSA-jq2c-m8gg-mqcm
Type: github-advisory

## Affected
- Maven: `org.apache.jena:jena-fuseki` — affected >=0 <5.5.0

## Details
Users with administrator access can create databases files outside the files area of the Fuseki server.

This issue affects Apache Jena version up to 5.4.0.

Users are recommended to upgrade to version 5.5.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-49656
- https://github.com/apache/jena/commit/03c5265910aa3a27907bf54f6b4aaae3409afa4f
- https://github.com/apache/jena/commit/35350569b4c1fd432d92e7c92af9597c4400debe
- https://github.com/apache/jena
- https://lists.apache.org/thread/qmm21som8zct813vx6dfd1phnfro6mwq
- http://www.openwall.com/lists/oss-security/2025/07/21/1
