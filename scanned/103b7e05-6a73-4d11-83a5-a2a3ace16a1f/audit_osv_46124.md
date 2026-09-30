# [M] JLSEC-2026-703

## Summary
Severity: Medium
Advisory: JLSEC-2026-703
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-703
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
An integer overflow vulnerability existed in the static function `wolfssl_add_to_chain`, that caused heap corruption when certificate data was written out of bounds of an insufficiently sized certificate buffer. `wolfssl_add_to_chain` is called by these API: `wolfSSL_CTX_add_extra_chain_cert`, `wolfSSL_CTX_add1_chain_cert`, `wolfSSL_add0_chain_cert`. These API are enabled for 3rd party compatibility features: enable-opensslall, enable-opensslextra, enable-lighty, enable-stunnel, enable-nginx, enable-haproxy. This issue is not remotely exploitable, and would require that the application context loading certificates is compromised.

## References
- https://github.com/wolfSSL/wolfssl/pull/9827
