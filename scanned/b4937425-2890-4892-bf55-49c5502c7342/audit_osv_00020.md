# [H] ALPINE-CVE-2015-8630

## Summary
Severity: High
Advisory: ALPINE-CVE-2015-8630
Ecosystem: Alpine:v3.4
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2015-8630
Type: osv

## Affected
- Alpine:v3.4: `krb5` — affected >=0 <1.14-r1

## Details
The (1) kadm5_create_principal_3 and (2) kadm5_modify_principal functions in lib/kadm5/srv/svr_principal.c in kadmind in MIT Kerberos 5 (aka krb5) 1.12.x and 1.13.x before 1.13.4 and 1.14.x before 1.14.1 allow remote authenticated users to cause a denial of service (NULL pointer dereference and daemon crash) by specifying KADM5_POLICY with a NULL policy name.

## References
- https://security.alpinelinux.org/vuln/CVE-2015-8630
