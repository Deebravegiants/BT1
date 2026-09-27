# [C] CVE-2021-24115

## Summary
Severity: Critical
Advisory: CVE-2021-24115
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-22
Source: https://osv.dev/vulnerability/CVE-2021-24115
Type: osv

## Details
In Botan before 2.17.3, constant-time computations are not used for certain decoding and encoding operations (base32, base58, base64, and hex).

## References
- https://botan.randombit.net/news.html
- https://github.com/randombit/botan/compare/2.17.2...2.17.3
- https://github.com/randombit/botan/pull/2549
