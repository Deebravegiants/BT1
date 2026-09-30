# [M] JLSEC-2026-92

## Summary
Severity: Medium
Advisory: JLSEC-2026-92
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/JLSEC-2026-92
Type: osv

## Affected
- Julia: `Kerberos_krb5_jll` — affected >=0 <1.21.3+0

## Details
`lib/kadm5/kadm_rpc_xdr.c` in MIT Kerberos 5 (aka krb5) before 1.20.2 and 1.21.x before 1.21.1 frees an uninitialized pointer. A remote authenticated user can trigger a kadmind crash. This occurs because `_xdr_kadm5_principal_ent_rec` does not validate the relationship between `n_key_data` and the `key_data` array count.

## References
- https://github.com/krb5/krb5/commit/ef08b09c9459551aabbe7924fb176f1583053cdd
- https://github.com/krb5/krb5/compare/krb5-1.20.1-final...krb5-1.20.2-final
- https://github.com/krb5/krb5/compare/krb5-1.21-final...krb5-1.21.1-final
- https://lists.debian.org/debian-lts-announce/2023/10/msg00031.html
- https://security.netapp.com/advisory/ntap-20230908-0004/
- https://web.mit.edu/kerberos/www/advisories/
