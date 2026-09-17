# [M] CVE-2018-5710

## Summary
Severity: Medium
Advisory: CVE-2018-5710
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-16
Source: https://osv.dev/vulnerability/CVE-2018-5710
Type: osv

## Details
An issue was discovered in MIT Kerberos 5 (aka krb5) through 1.16. The pre-defined function "strlen" is getting a "NULL" string as a parameter value in plugins/kdb/ldap/libkdb_ldap/ldap_principal2.c in the Key Distribution Center (KDC), which allows remote authenticated users to cause a denial of service (NULL pointer dereference) via a modified kadmin client.

## References
- https://github.com/poojamnit/Kerberos-V5-1.16-Vulnerabilities/tree/master/Denial%20Of%20Service%28DoS%29
