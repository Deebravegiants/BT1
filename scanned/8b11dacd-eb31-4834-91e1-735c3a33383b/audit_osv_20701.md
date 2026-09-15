# [H] CVE-2021-36222

## Summary
Severity: High
Advisory: CVE-2021-36222
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-22
Source: https://osv.dev/vulnerability/CVE-2021-36222
Type: osv

## Details
ec_verify in kdc/kdc_preauth_ec.c in the Key Distribution Center (KDC) in MIT Kerberos 5 (aka krb5) before 1.18.4 and 1.19.x before 1.19.2 allows remote attackers to cause a NULL pointer dereference and daemon crash. This occurs because a return value is not properly managed in a certain situation.

## References
- https://github.com/krb5/krb5/releases
- https://security.netapp.com/advisory/ntap-20211022-0003/
- https://security.netapp.com/advisory/ntap-20211104-0007/
- https://web.mit.edu/kerberos/advisories/
- https://www.debian.org/security/2021/dsa-4944
- https://github.com/krb5/krb5/commit/fc98f520caefff2e5ee9a0026fdf5109944b3562
- https://www.oracle.com/security-alerts/cpuoct2021.html
