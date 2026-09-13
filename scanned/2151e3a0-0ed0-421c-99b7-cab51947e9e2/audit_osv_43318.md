# [H] Mongoose Built-in TLS: CA-bundle certificate chain accepted without any signature verification

## Summary
Severity: High
Advisory: CVE-2026-73251
Aliases: GHSA-qj6j-2692-v2r8
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-73251
Type: osv

## Details
Mongoose is an embedded web server and network library. Prior to 7.23, a network attacker can impersonate a TLS server to a Mongoose client configured with a multi-certificate CA bundle. In src/tls_builtin.c, the mg_tls_init() function stores the bundle in tls->ca_bundle_der while tls->ca_der.len remains zero, and mg_tls_recv_cert() uses tls_bundle_find() to accept a Common Name match without calling mg_tls_verify_cert_signature(). A forged self-signed certificate can therefore satisfy hostname and CertificateVerify checks and enable interception, credential disclosure, traffic modification, and malicious responses. This issue is fixed in version 7.23.

## References
- https://github.com/cesanta/mongoose/releases/tag/7.23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73251.json
- https://github.com/cesanta/mongoose/security/advisories/GHSA-qj6j-2692-v2r8
- https://nvd.nist.gov/vuln/detail/CVE-2026-73251
- https://github.com/cesanta/mongoose/commit/2988bc9df3a5efc9539471cb7455975fa25df483
