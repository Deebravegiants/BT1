# [M] ALPINE-CVE-2015-8629

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2015-8629
Ecosystem: Alpine:v3.4
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-02-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2015-8629
Type: osv

## Affected
- Alpine:v3.4: `krb5` — affected >=0 <1.14-r1

## Details
The xdr_nullstring function in lib/kadm5/kadm_rpc_xdr.c in kadmind in MIT Kerberos 5 (aka krb5) before 1.13.4 and 1.14.x before 1.14.1 does not verify whether '\0' characters exist as expected, which allows remote authenticated users to obtain sensitive information or cause a denial of service (out-of-bounds read) via a crafted string.

## References
- https://security.alpinelinux.org/vuln/CVE-2015-8629
