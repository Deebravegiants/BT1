# [M] HMAC-BLAKE2 final discards message when key length exceeds block size

## Summary
Severity: Medium
Advisory: CVE-2026-8720
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-8720
Type: osv

## Details
wc_Blake2bHmacFinal and wc_Blake2sHmacFinal discard the message when the key length exceeds the block size, producing a MAC that is independent of the input. When the supplied key is longer than the BLAKE2 block size the key-hashing branch reinitialized the running hash state, discarding the accumulated message data, so the resulting MAC depended only on the key and not on the message being authenticated. This bug is specific to the HMAC-BLAKE2 APIs that were added in wolfSSL version 5.9.0.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8720.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8720
- https://github.com/wolfSSL/wolfssl/pull/10447
- https://github.com/wolfSSL/wolfssl
