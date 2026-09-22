# [H] CVE-2018-18854

## Summary
Severity: High
Advisory: CVE-2018-18854
Aliases: GHSA-q8xj-8xg3-w432
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-31
Source: https://osv.dev/vulnerability/CVE-2018-18854
Type: osv

## Details
Lightbend Spray spray-json through 1.3.4 allows remote attackers to cause a denial of service (resource consumption) because of Algorithmic Complexity during the parsing of many JSON object fields (with keys that have the same hash code).

## References
- https://github.com/spray/spray-json/issues/277
