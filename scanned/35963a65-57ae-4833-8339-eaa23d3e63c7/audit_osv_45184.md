# [H] A flaw was found in cairo's image-compositor.c in all versions prior to 1.17.4

## Summary
Severity: High
Advisory: JLSEC-2025-17
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-17
Type: osv

## Affected
- Julia: `Cairo_jll` — affected >=0 <1.18.0+0

## Details
A flaw was found in cairo's image-compositor.c in all versions prior to 1.17.4. This flaw allows an attacker who can provide a crafted input file to cairo's image-compositor (for example, by convincing a user to open a file in an application using cairo, or if an application uses cairo on untrusted input) to cause a stack buffer overflow -> out-of-bounds WRITE. The highest impact from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1898396
- https://security.gentoo.org/glsa/202305-21
