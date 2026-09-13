# [C] CVE-2024-37371

## Summary
Severity: Critical
Advisory: CVE-2024-37371
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-06-28
Source: https://osv.dev/vulnerability/CVE-2024-37371
Type: osv

## Details
In MIT Kerberos 5 (aka krb5) before 1.21.3, an attacker can cause invalid memory reads during GSS message token handling by sending message tokens with invalid length fields.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37371.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-37371
- https://security.netapp.com/advisory/ntap-20241108-0009/
- https://security.netapp.com/advisory/ntap-20250124-0010/
- https://web.mit.edu/kerberos/www/advisories/
- https://github.com/krb5/krb5/commit/55fbf435edbe2e92dd8101669b1ce7144bc96fef
