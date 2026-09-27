# [H] CVE-2016-10578

## Summary
Severity: High
Advisory: CVE-2016-10578
Aliases: GHSA-qjf4-7642-c57p
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-29
Source: https://osv.dev/vulnerability/CVE-2016-10578
Type: osv

## Details
unicode loads unicode data downloaded from unicode.org into nodejs. Unicode before 9.0.0 downloads binary resources over HTTP, which leaves it vulnerable to MITM attacks.

## References
- https://nodesecurity.io/advisories/161
