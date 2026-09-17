# [H] Firebird: DoS via `op_response` packet from client

## Summary
Severity: High
Advisory: CVE-2026-34232
Aliases: GHSA-7jq3-6j3c-5cm2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-34232
Type: osv

## Details
Firebird is an open-source relational database management system. In versions prior to 5.0.4, 4.0.7 and 3.0.14, the xdr_status_vector() function does not handle the isc_arg_cstring type when decoding an op_response packet, causing a server crash when one is encountered in the status vector. An unauthenticated attacker can exploit this by sending a crafted op_response packet to the server. This issue has been fixed in versions 5.0.4, 4.0.7 and 3.0.14.

## References
- https://github.com/FirebirdSQL/firebird/releases/tag/v3.0.14
- https://github.com/FirebirdSQL/firebird/releases/tag/v4.0.7
- https://github.com/FirebirdSQL/firebird/releases/tag/v5.0.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34232.json
- https://github.com/FirebirdSQL/firebird/security/advisories/GHSA-7jq3-6j3c-5cm2
- https://nvd.nist.gov/vuln/detail/CVE-2026-34232
