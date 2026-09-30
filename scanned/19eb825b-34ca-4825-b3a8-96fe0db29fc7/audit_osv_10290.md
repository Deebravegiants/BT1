# [M] CVE-2017-14737

## Summary
Severity: Medium
Advisory: CVE-2017-14737
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-09-26
Source: https://osv.dev/vulnerability/CVE-2017-14737
Type: osv

## Details
A cryptographic cache-based side channel in the RSA implementation in Botan before 1.10.17, and 1.11.x and 2.x before 2.3.0, allows a local attacker to recover information about RSA secret keys, as demonstrated by CacheD. This occurs because an array is indexed with bits derived from a secret key.

## References
- https://lists.debian.org/debian-lts-announce/2021/11/msg00006.html
- https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/wang-shuai
- https://github.com/randombit/botan/issues/1222
