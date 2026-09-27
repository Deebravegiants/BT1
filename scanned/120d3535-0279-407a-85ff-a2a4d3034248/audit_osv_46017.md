# [H] JLSEC-2026-575

## Summary
Severity: High
Advisory: JLSEC-2026-575
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-06
Source: https://osv.dev/vulnerability/JLSEC-2026-575
Type: osv

## Affected
- Julia: `Nettle_jll` — affected >=0 <3.7.2+0

## Details
A flaw was found in Nettle in versions before 3.7.2, where several Nettle signature verification functions (GOST DSA, EDDSA & ECDSA) result in the Elliptic Curve Cryptography point (ECC) multiply function being called with out-of-range scalers, possibly resulting in incorrect results. This flaw allows an attacker to force an invalid signature, causing an assertion failure or possible validation. The highest threat to this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1942533
- https://lists.debian.org/debian-lts-announce/2021/09/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MQKWVVMAIDAJ7YAA3VVO32BHLDOH2E63/
- https://security.gentoo.org/glsa/202105-31
- https://security.netapp.com/advisory/ntap-20211022-0002/
- https://www.debian.org/security/2021/dsa-4933
