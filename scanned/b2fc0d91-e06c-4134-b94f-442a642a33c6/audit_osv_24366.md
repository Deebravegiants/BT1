# [M] CVE-2023-0967

## Summary
Severity: Medium
Advisory: CVE-2023-0967
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-05
Source: https://osv.dev/vulnerability/CVE-2023-0967
Type: osv

## Details
Bhima version 1.27.0 allows an attacker authenticated with normal user permissions to view sensitive data of other application users and data that should only be viewed by the administrator. This is possible because the application is vulnerable to IDOR, it does not properly validate user permissions with respect to certain actions the user can perform.

## References
- https://github.com/IMA-WorldHealth/bhima/
- https://fluidattacks.com/advisories/ingrosso/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0967.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0967
