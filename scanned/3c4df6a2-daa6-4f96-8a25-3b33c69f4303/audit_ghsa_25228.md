# [H] Play Framework's Assets controller vulnerable to directory traversal

## Summary
Severity: High
Advisory: GHSA-v4mq-p756-p4f5
CVE: CVE-2018-13864
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-v4mq-p756-p4f5
Type: github-advisory

## Affected
- Maven: `com.typesafe.play:play_2.12` — affected >=2.6.12 <2.6.16

## Details
A directory traversal vulnerability has been found in the Assets controller in Play Framework 2.6.12 through 2.6.15 (fixed in 2.6.16) when running on Windows. It allows a remote attacker to download arbitrary files from the target server via specially crafted HTTP requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-13864
- https://discuss.lightbend.com/t/play-2-6-16-released/1575
- https://www.playframework.com/security/vulnerability/CVE-2018-13864-PathTraversal
