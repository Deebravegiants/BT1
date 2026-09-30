# [H] CVE-2016-2849

## Summary
Severity: High
Advisory: CVE-2016-2849
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-05-13
Source: https://osv.dev/vulnerability/CVE-2016-2849
Type: osv

## Details
Botan before 1.10.13 and 1.11.x before 1.11.29 do not use a constant-time algorithm to perform a modular inverse on the signature nonce k, which might allow remote attackers to obtain ECDSA secret keys via a timing side-channel attack.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183669.html
- http://botan.randombit.net/security.html
- http://marc.info/?l=botan-devel&m=146185420505943&w=2
- http://www.debian.org/security/2016/dsa-3565
- https://security.gentoo.org/glsa/201701-23
