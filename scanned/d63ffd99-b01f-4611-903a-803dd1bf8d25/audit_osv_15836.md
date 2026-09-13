# [M] CVE-2019-19963

## Summary
Severity: Medium
Advisory: CVE-2019-19963
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-12-25
Source: https://osv.dev/vulnerability/CVE-2019-19963
Type: osv

## Details
An issue was discovered in wolfSSL before 4.3.0 in a non-default configuration where DSA is enabled. DSA signing uses the BEEA algorithm during modular inversion of the nonce, leading to a side-channel attack against the nonce.

## References
- https://github.com/wolfSSL/wolfssl/releases/tag/v4.3.0-stable
- https://github.com/wolfSSL/wolfssl/commit/7e391f0fd57f2ef375b1174d752a56ce34b2b190
