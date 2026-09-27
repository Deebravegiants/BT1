# [H] Firebird has a buffer overflow when parsing corrupted slice packets

## Summary
Severity: High
Advisory: CVE-2026-33337
Aliases: GHSA-89mq-229g-x47p
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-33337
Type: osv

## Details
Firebird is an open-source relational database management system. In versions prior to 5.0.4, 4.0.7 and 3.0.14, when deserializing a slice packet, the xdr_datum() function does not validate that a cstring length conforms to the slice descriptor bounds, allowing a cstring longer than the allocated buffer to overflow it. An unauthenticated attacker can exploit this by sending a crafted packet to the server, potentially causing a crash or other security impact. This issue has been fixed in versions 5.0.4, 4.0.7 and 3.0.14.

## References
- https://github.com/FirebirdSQL/firebird/releases/tag/v3.0.14
- https://github.com/FirebirdSQL/firebird/releases/tag/v4.0.7
- https://github.com/FirebirdSQL/firebird/releases/tag/v5.0.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33337.json
- https://github.com/FirebirdSQL/firebird/security/advisories/GHSA-89mq-229g-x47p
- https://nvd.nist.gov/vuln/detail/CVE-2026-33337
