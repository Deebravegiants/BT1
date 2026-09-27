# [H] Out-of-bounds heap read during SM2/SM3 certificate signature verification

## Summary
Severity: High
Advisory: JLSEC-2026-700
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-700
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.7.2+0 <5.9.2+0

## Details
Out-of-bounds heap read during SM2/SM3 certificate signature verification. When parsing a certificate with an SM3wSM2 signature, the Subject Key Identifier computation reads the trailing 65 bytes of the public key without checking that the key is at least that long. A public key shorter than 65 bytes results in an out-of-bounds heap read, leading to a potential crash (denial of service); there is no out-of-bounds write. Note this only affects builds with SM2 support (--enable-sm2 or --enable-all).

## References
- https://github.com/advisories/GHSA-q349-x427-xg3w
- https://github.com/wolfSSL/wolfssl/pull/10641
- https://nvd.nist.gov/vuln/detail/CVE-2026-12340
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
