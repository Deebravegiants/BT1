# [H] Heap buffer overflow in CertFromX509 via AuthorityKeyIdentifier size confusion

## Summary
Severity: High
Advisory: JLSEC-2026-723
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-723
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
Heap buffer overflow in CertFromX509 via AuthorityKeyIdentifier size confusion. A heap buffer overflow occurs when converting an X.509 certificate internally due to incorrect size handling of the AuthorityKeyIdentifier extension.

## References
- https://github.com/advisories/GHSA-mx4j-fjqx-f8qj
- https://github.com/wolfSSL/wolfssl/pull/10112
- https://nvd.nist.gov/vuln/detail/CVE-2026-5447
