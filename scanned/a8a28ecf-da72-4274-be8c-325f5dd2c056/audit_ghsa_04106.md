# [H] Improper Authentication in Apache Zeppelin

## Summary
Severity: High
Advisory: GHSA-9x2h-hvg6-4r5p
CVE: CVE-2018-1317
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-04-24
Source: https://github.com/advisories/GHSA-9x2h-hvg6-4r5p
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin` — affected >=0 <0.8.0

## Details
In Apache Zeppelin prior to 0.8.0 the cron scheduler was enabled by default and could allow users to run paragraphs as other users without authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1317
- https://lists.apache.org/thread.html/ff6b995a5a3ba8db4d6b14b4d9dd487e7bf2e3bdd5b375b64a25fd06@%3Cusers.zeppelin.apache.org%3E
- https://zeppelin.apache.org/releases/zeppelin-release-0.8.0.html
- http://www.openwall.com/lists/oss-security/2019/04/23/1
