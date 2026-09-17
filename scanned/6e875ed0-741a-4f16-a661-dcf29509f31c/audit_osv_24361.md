# [M] CVE-2023-0944

## Summary
Severity: Medium
Advisory: CVE-2023-0944
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-04-05
Source: https://osv.dev/vulnerability/CVE-2023-0944
Type: osv

## Details
Bhima version 1.27.0 allows an authenticated attacker with regular user permissions to update arbitrary user session data such as username, email and password. This is possible because the application is vulnerable to IDOR, it does not correctly validate user permissions with respect to certain actions that can be performed by the user.

## References
- https://github.com/IMA-WorldHealth/bhima/
- https://fluidattacks.com/advisories/stewart/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0944.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0944
