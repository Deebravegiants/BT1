# [C] CVE-2020-36177

## Summary
Severity: Critical
Advisory: CVE-2020-36177
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-06
Source: https://osv.dev/vulnerability/CVE-2020-36177
Type: osv

## Details
RsaPad_PSS in wolfcrypt/src/rsa.c in wolfSSL before 4.6.0 has an out-of-bounds write for certain relationships between key size and digest size.

## References
- https://github.com/wolfSSL/wolfssl/releases/tag/v4.6.0-stable
- https://github.com/wolfSSL/wolfssl/commit/63bf5dc56ccbfc12a73b06327361687091a4c6f7
- https://github.com/wolfSSL/wolfssl/commit/fb2288c46dd4c864b78f00a47a364b96a09a5c0f
- https://github.com/wolfSSL/wolfssl/pull/3426
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=26567
