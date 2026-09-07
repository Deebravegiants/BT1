# [H] SkyWalking OAP /debugging/config/dump endpoint may leak sensitive configuration information

## Summary
Severity: High
Advisory: GHSA-27h3-crw2-q36w
CVE: CVE-2026-30778
CWE: CWE-202
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-27h3-crw2-q36w
Type: github-advisory

## Affected
- Maven: `org.apache.skywalking:server-core` — affected >=9.7.0 <10.4.0

## Details
The SkyWalking OAP /debugging/config/dump endpoint may leak sensitive configuration information of MySQL/PostgreSQL.

This issue affects Apache SkyWalking: from 9.7.0 through 10.3.0.

Users are recommended to upgrade to version 10.4.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-30778
- https://github.com/apache/skywalking/commit/5a3f6260e4dd681a9132204e5299064bef079886
- https://github.com/apache/skywalking
- https://lists.apache.org/thread/pvf35o3tp1rqhmrhzj6fg31gvqrqcvn3
- http://www.openwall.com/lists/oss-security/2026/04/15/2
