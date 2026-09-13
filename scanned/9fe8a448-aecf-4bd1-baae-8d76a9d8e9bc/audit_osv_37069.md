# [H] Firebird has potential server crash via null pointer dereference when processing op_slice packet

## Summary
Severity: High
Advisory: CVE-2026-28212
Aliases: GHSA-9884-9qm3-hqch
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-28212
Type: osv

## Details
Firebird is an open-source relational database management system. In versions prior to 6.0.0, 5.0.4, 4.0.7 and 3.0.14, when processing an op_slice network packet, the server passes an unprepared structure containing a null pointer to the SDL_info() function, resulting in a null pointer dereference and server crash. An unauthenticated attacker can trigger this by sending a crafted packet to the server port. This issue has been fixed in versions 6.0.0, 5.0.4, 4.0.7 and 3.0.14.

## References
- https://github.com/FirebirdSQL/firebird/releases/tag/v3.0.14
- https://github.com/FirebirdSQL/firebird/releases/tag/v4.0.7
- https://github.com/FirebirdSQL/firebird/releases/tag/v5.0.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28212.json
- https://github.com/FirebirdSQL/firebird/security/advisories/GHSA-9884-9qm3-hqch
- https://nvd.nist.gov/vuln/detail/CVE-2026-28212
