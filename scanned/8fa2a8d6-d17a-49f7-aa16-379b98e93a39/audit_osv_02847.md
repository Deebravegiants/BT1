# [M] ALPINE-CVE-2023-36054

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-36054
Ecosystem: Alpine:v3.17, Alpine:v3.18
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-08-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-36054
Type: osv

## Affected
- Alpine:v3.17: `krb5` — affected >=0 <1.20.2-r0
- Alpine:v3.18: `krb5` — affected >=0 <1.20.2-r0

## Details
lib/kadm5/kadm_rpc_xdr.c in MIT Kerberos 5 (aka krb5) before 1.20.2 and 1.21.x before 1.21.1 frees an uninitialized pointer. A remote authenticated user can trigger a kadmind crash. This occurs because _xdr_kadm5_principal_ent_rec does not validate the relationship between n_key_data and the key_data array count.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-36054
