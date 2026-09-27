# [H] mod_auth_openidc has out-of-bounds read and write in state cookie parsing

## Summary
Severity: High
Advisory: CVE-2026-54789
Aliases: GHSA-vgr5-qcpp-x2pr
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-54789
Type: osv

## Details
mod_auth_openidc is an OpenID Certified authentication and authorization module for the Apache 2.x HTTP server that implements the OpenID Connect Relying Party functionality. Prior to 2.4.19.4, an out-of-bounds read and a one-byte out-of-bounds write exist in the state-cookie parser of `mod_auth_openidc`. The issue is fixed in version 2.4.19.4 by stopping the scan at the string terminator so a value-less token is rejected. No in-product workarounds are available. As a stop-gap, an upstream reverse proxy or WAF that rejects or normalizes malformed `Cookie` headers (tokens lacking `=`) can reduce exposure, but upgrading is the recommended remediation.

## References
- https://lists.debian.org/debian-lts-announce/2026/09/msg00003.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54789.json
- https://github.com/OpenIDC/mod_auth_openidc/security/advisories/GHSA-vgr5-qcpp-x2pr
- https://nvd.nist.gov/vuln/detail/CVE-2026-54789
- https://github.com/OpenIDC/mod_auth_openidc/commit/8017478471cc071c49aa073c5c9be652a73a8630
