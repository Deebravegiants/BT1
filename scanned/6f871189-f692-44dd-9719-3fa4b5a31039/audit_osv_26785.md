# [C] Ever Gauzy v0.281.9 JWT Authentication Weakness via HMAC Secret

## Summary
Severity: Critical
Advisory: CVE-2023-53951
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-19
Source: https://osv.dev/vulnerability/CVE-2023-53951
Type: osv

## Details
Ever Gauzy v0.281.9 contains a JWT authentication vulnerability that allows attackers to exploit weak HMAC secret key implementation. Attackers can leverage the exposed JWT token to authenticate and gain unauthorized access with administrative permissions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53951.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53951
- https://www.vulncheck.com/advisories/ever-gauzy-jwt-authentication-weakness-via-hmac-secret
- https://github.com/ever-co/ever-gauzy
- https://www.exploit-db.com/exploits/51354
