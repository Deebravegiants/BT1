# [H] Firebird has Pre-Auth DOS when Processing Out of Order CNCT_specific_data Segments

## Summary
Severity: High
Advisory: CVE-2026-27890
Aliases: GHSA-6crx-4g37-7j49
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-27890
Type: osv

## Details
Firebird is an open-source relational database management system. In versions prior to 5.0.4, 4.0.7 and 3.0.14, when processing CNCT_specific_data segments during authentication, the server assumes segments arrive in strictly ascending order. If segments arrive out of order, the Array class's grow() method computes a negative size value, causing a SIGSEGV crash. An unauthenticated attacker who knows only the server's IP and port can exploit this to crash the server. This issue has been fixed in versions 5.0.4, 4.0.7 and 3.0.14.

## References
- https://github.com/FirebirdSQL/firebird/releases/tag/v3.0.14
- https://github.com/FirebirdSQL/firebird/releases/tag/v4.0.7
- https://github.com/FirebirdSQL/firebird/releases/tag/v5.0.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27890.json
- https://github.com/FirebirdSQL/firebird/security/advisories/GHSA-6crx-4g37-7j49
- https://nvd.nist.gov/vuln/detail/CVE-2026-27890
