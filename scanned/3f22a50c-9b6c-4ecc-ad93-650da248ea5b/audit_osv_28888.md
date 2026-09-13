# [H] CVE-2024-37370

## Summary
Severity: High
Advisory: CVE-2024-37370
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-28
Source: https://osv.dev/vulnerability/CVE-2024-37370
Type: osv

## Details
In MIT Kerberos 5 (aka krb5) before 1.21.3, an attacker can modify the plaintext Extra Count field of a confidential GSS krb5 wrap token, causing the unwrapped token to appear truncated to the application.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37370.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-37370
- https://security.netapp.com/advisory/ntap-20241108-0007/
- https://web.mit.edu/kerberos/www/advisories/
- https://github.com/krb5/krb5/commit/55fbf435edbe2e92dd8101669b1ce7144bc96fef
