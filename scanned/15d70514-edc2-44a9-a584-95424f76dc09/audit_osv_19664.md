# [H] CVE-2021-23434

## Summary
Severity: High
Advisory: CVE-2021-23434
Aliases: GHSA-v39p-96qg-c8rf
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2021-08-27
Source: https://osv.dev/vulnerability/CVE-2021-23434
Type: osv

## Details
This affects the package object-path before 0.11.6. A type confusion vulnerability can lead to a bypass of CVE-2020-15256 when the path components used in the path parameter are arrays. In particular, the condition currentPath === '__proto__' returns false if currentPath is ['__proto__']. This is because the === operator returns always false when the type of the operands is different.

## References
- https://lists.debian.org/debian-lts-announce/2023/01/msg00031.html
- https://github.com/mariocasciaro/object-path/commit/7bdf4abefd102d16c163d633e8994ef154cab9eb
- https://github.com/mariocasciaro/object-path%230116
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1570423
- https://snyk.io/vuln/SNYK-JS-OBJECTPATH-1569453
