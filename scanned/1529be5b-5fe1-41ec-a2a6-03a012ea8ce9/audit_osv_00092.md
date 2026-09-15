# [M] ALPINE-CVE-2016-3119

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-3119
Ecosystem: Alpine:v3.4
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-03-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-3119
Type: osv

## Affected
- Alpine:v3.4: `krb5` — affected >=0 <1.14-r2

## Details
The process_db_args function in plugins/kdb/ldap/libkdb_ldap/ldap_principal2.c in the LDAP KDB module in kadmind in MIT Kerberos 5 (aka krb5) through 1.13.4 and 1.14.x through 1.14.1 mishandles the DB argument, which allows remote authenticated users to cause a denial of service (NULL pointer dereference and daemon crash) via a crafted request to modify a principal.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-3119
