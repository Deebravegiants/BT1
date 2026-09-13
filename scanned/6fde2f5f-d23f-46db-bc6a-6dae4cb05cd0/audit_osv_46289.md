# [H] JLSEC-2026-93

## Summary
Severity: High
Advisory: JLSEC-2026-93
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/JLSEC-2026-93
Type: osv

## Affected
- Julia: `Kerberos_krb5_jll` — affected >=0 <1.21.3+0

## Details
In MIT Kerberos 5 (aka krb5) before 1.21.3, an attacker can modify the plaintext Extra Count field of a confidential GSS krb5 wrap token, causing the unwrapped token to appear truncated to the application.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://github.com/krb5/krb5/commit/55fbf435edbe2e92dd8101669b1ce7144bc96fef
- https://security.netapp.com/advisory/ntap-20241108-0007/
- https://web.mit.edu/kerberos/www/advisories/
