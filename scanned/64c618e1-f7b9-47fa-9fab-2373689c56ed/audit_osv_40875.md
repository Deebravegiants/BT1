# [M] Un-negotiated Raw Public Key (RFC 7250) accepted in place of X.509, bypassing chain validation

## Summary
Severity: Medium
Advisory: CVE-2026-55960
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-55960
Type: osv

## Details
Un-negotiated Raw Public Key (RFC 7250) accepted in place of an X.509 certificate, bypassing chain validation. A raw public key has no chain, so ParseCertRelative() accepts it without performing any trust verification; it must therefore only be accepted when RPK was actually negotiated for that peer. The check now defaults the expected type to X.509 (per RFC 7250/8446) when no type was negotiated, comparing against the received server certificate type on the client and the selected client certificate type on the server, and rejects any mismatch, including an un-negotiated raw public key, with UNSUPPORTED_CERTIFICATE. Only affects builds with Raw Public Key support (HAVE_RPK) enabled - disabled by default in a standalone build, but included in --enable-all.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55960.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55960
- https://github.com/wolfSSL/wolfssl/pull/10702
- https://github.com/wolfSSL/wolfssl
