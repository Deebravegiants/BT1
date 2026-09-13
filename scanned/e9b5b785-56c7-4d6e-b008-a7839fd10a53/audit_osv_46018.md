# [H] JLSEC-2026-576

## Summary
Severity: High
Advisory: JLSEC-2026-576
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-06
Source: https://osv.dev/vulnerability/JLSEC-2026-576
Type: osv

## Affected
- Julia: `Nettle_jll` — affected >=0 <3.9.1+0

## Details
A flaw was found in the way nettle's RSA decryption functions handled specially crafted ciphertext. An attacker could use this flaw to provide a manipulated ciphertext leading to application crash and denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1967983
- https://lists.debian.org/debian-lts-announce/2021/09/msg00008.html
- https://security.gentoo.org/glsa/202401-24
- https://security.netapp.com/advisory/ntap-20211104-0006/
