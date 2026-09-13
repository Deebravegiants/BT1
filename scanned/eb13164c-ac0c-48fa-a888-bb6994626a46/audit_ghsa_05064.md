# [M] Apache Fesod is vulnerable to Server-Side Request Forgery through its UrlImageConverter component

## Summary
Severity: Medium
Advisory: GHSA-vqc2-c9jh-3jjv
CVE: CVE-2026-49328
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-vqc2-c9jh-3jjv
Type: github-advisory

## Affected
- Maven: `org.apache.fesod:fesod-sheet` — affected >=0 <2.0.2-incubating

## Details
Server-Side Request Forgery (SSRF) in the UrlImageConverter component of Apache Fesod (Incubating) fesod-sheet before 2.0.2-incubating allows attackers to cause outbound network requests to internal or otherwise restricted resources via a user-supplied image URL. Users are recommended to upgrade to version 2.0.2-incubating, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49328
- https://github.com/apache/fesod/pull/917
- https://fesod.apache.org/docs/download
- https://github.com/apache/fesod
- https://github.com/apache/fesod/releases/tag/2.0.2-incubating
- https://lists.apache.org/thread/c1pb5b66h02p9tlrnfbwcgcz85v16fkj
- http://www.openwall.com/lists/oss-security/2026/06/01/4
