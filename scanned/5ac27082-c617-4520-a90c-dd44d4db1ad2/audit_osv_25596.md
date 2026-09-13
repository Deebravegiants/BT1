# [H] CVE-2023-39975

## Summary
Severity: High
Advisory: CVE-2023-39975
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-16
Source: https://osv.dev/vulnerability/CVE-2023-39975
Type: osv

## Details
kdc/do_tgs_req.c in MIT Kerberos 5 (aka krb5) 1.21 before 1.21.2 has a double free that is reachable if an authenticated user can trigger an authorization-data handling failure. Incorrect data is copied from one ticket to another.

## References
- https://github.com/krb5/krb5/compare/krb5-1.21.1-final...krb5-1.21.2-final
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39975.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-39975
- https://security.netapp.com/advisory/ntap-20230915-0014/
- https://security.netapp.com/advisory/ntap-20240201-0005/
- https://security.netapp.com/advisory/ntap-20240201-0008/
- https://web.mit.edu/kerberos/www/advisories/
- https://github.com/krb5/krb5/commit/88a1701b423c13991a8064feeb26952d3641d840
