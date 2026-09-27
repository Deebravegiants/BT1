# [H] HMAC zero-length tag forgery in `EVP_DigestVerifyFinal`, where a zero-length tag could be accepted...

## Summary
Severity: High
Advisory: JLSEC-2026-749
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-749
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
HMAC zero-length tag forgery in `EVP_DigestVerifyFinal`, where a zero-length tag could be accepted as valid during HMAC verification. In the OpenSSL-compatibility HMAC verify path the supplied signature length was only checked as not exceeding the MAC length, so a zero-length or otherwise truncated tag could pass verification. The fix requires the supplied tag length to exactly equal the MAC length and rejects a zero-length MAC, so a forged short or empty tag is no longer accepted.

## References
- https://github.com/advisories/GHSA-5hpf-pc4x-3jcf
- https://github.com/wolfSSL/wolfssl/pull/10192
- https://nvd.nist.gov/vuln/detail/CVE-2026-6331
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
