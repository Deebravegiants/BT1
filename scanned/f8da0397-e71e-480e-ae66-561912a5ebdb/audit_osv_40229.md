# [H] wolfSSL ECDSA Certificate Verification

## Summary
Severity: High
Advisory: CVE-2026-5194
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:H/SI:L/SA:L/U:Red)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-5194
Type: osv

## Details
Missing hash/digest size and OID checks allow digests smaller than allowed when verifying ECDSA certificates, or smaller than is appropriate for the relevant key type, to be accepted by signature verification functions. This could lead to reduced security of ECDSA certificate-based authentication if the public CA key used is also known. This affects ECDSA/ECC verification when EdDSA or ML-DSA is also enabled.

## References
- https://www.anthropic.com/research/glasswing-initial-update
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5194.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5194
- https://github.com/wolfSSL/wolfssl/pull/10131
- https://github.com/wolfSSL/wolfssl
