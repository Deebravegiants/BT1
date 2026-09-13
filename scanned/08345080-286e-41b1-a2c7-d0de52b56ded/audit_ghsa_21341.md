# [C] Heron allows CRLF log injection

## Summary
Severity: Critical
Advisory: GHSA-95w5-q9vp-5vrm
CVE: CVE-2021-42010
CWE: CWE-116
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-24
Source: https://github.com/advisories/GHSA-95w5-q9vp-5vrm
Type: github-advisory

## Affected
- Maven: `org.apache.heron:heron-api` — affected >=0 <0.20.5-incubating

## Details
Heron versions <= 0.20.4-incubating allows CRLF log injection because of the lack of escaping in the log statements. Please update to version 0.20.5-incubating which addresses this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42010
- https://lists.apache.org/thread/j65nwr8n7jchngwqptzh100drcr4ry2q
- http://www.openwall.com/lists/oss-security/2022/10/23/2
