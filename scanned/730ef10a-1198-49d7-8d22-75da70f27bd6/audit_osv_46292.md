# [C] JLSEC-2026-94

## Summary
Severity: Critical
Advisory: JLSEC-2026-94
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/JLSEC-2026-94
Type: osv

## Affected
- Julia: `Kerberos_krb5_jll` — affected >=0 <1.21.3+0

## Details
In MIT Kerberos 5 (aka krb5) before 1.21.3, an attacker can cause invalid memory reads during GSS message token handling by sending message tokens with invalid length fields.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://github.com/krb5/krb5/commit/55fbf435edbe2e92dd8101669b1ce7144bc96fef
- https://security.netapp.com/advisory/ntap-20241108-0009/
- https://security.netapp.com/advisory/ntap-20250124-0010/
- https://web.mit.edu/kerberos/www/advisories/
