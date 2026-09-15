# [H] Firebird: DoS via malicious slice descriptor in slice packet

## Summary
Severity: High
Advisory: CVE-2026-35215
Aliases: GHSA-g99w-prq5-29c6
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-35215
Type: osv

## Details
Firebird is an open-source relational database management system. In versions prior to 5.0.4, 4.0.7 and 3.0.14, the sdl_desc() function does not validate the length of a decoded SDL descriptor from a slice packet. A zero-length descriptor is later used to calculate the number of slice items, causing a division by zero. An unauthenticated attacker can exploit this by sending a crafted slice packet to crash the server. This issue has been fixed in versions 5.0.4, 4.0.7 and 3.0.14.

## References
- https://github.com/FirebirdSQL/firebird/releases/tag/v3.0.14
- https://github.com/FirebirdSQL/firebird/releases/tag/v4.0.7
- https://github.com/FirebirdSQL/firebird/releases/tag/v5.0.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35215.json
- https://github.com/FirebirdSQL/firebird/security/advisories/GHSA-g99w-prq5-29c6
- https://nvd.nist.gov/vuln/detail/CVE-2026-35215
