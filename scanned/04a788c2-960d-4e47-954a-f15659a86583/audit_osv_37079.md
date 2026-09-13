# [H] Firebird Null Pointer Dereference via CryptCallback causes DOS

## Summary
Severity: High
Advisory: CVE-2026-28224
Aliases: GHSA-xrcw-wpjx-pr95
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-28224
Type: osv

## Details
Firebird is an open-source relational database management system. In versions prior to 5.0.4, 4.0.7 and 3.0.14, when the server receives an op_crypt_key_callback packet without prior authentication, the port_server_crypt_callback handler is not initialized, resulting in a null pointer dereference and server crash. An unauthenticated attacker who knows only the server's IP and port can exploit this to crash the server. This issue has been fixed in versions 5.0.4, 4.0.7 and 3.0.14.

## References
- https://github.com/FirebirdSQL/firebird/releases/tag/v3.0.14
- https://github.com/FirebirdSQL/firebird/releases/tag/v4.0.7
- https://github.com/FirebirdSQL/firebird/releases/tag/v5.0.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28224.json
- https://github.com/FirebirdSQL/firebird/security/advisories/GHSA-xrcw-wpjx-pr95
- https://nvd.nist.gov/vuln/detail/CVE-2026-28224
