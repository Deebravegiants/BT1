# [H] aiven-extras PostgreSQL Privilege Escalation Through Overloaded Search Path

## Summary
Severity: High
Advisory: CVE-2023-32305
Aliases: GHSA-7r4w-fw4h-67gp
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-05-12
Source: https://osv.dev/vulnerability/CVE-2023-32305
Type: osv

## Details
aiven-extras is a PostgreSQL extension. Versions prior to 1.1.9 contain a privilege escalation vulnerability, allowing elevation to superuser inside PostgreSQL databases that use the aiven-extras package. The vulnerability leverages missing schema qualifiers on privileged functions called by the aiven-extras extension. A low privileged user can create objects that collide with existing function names, which will then be executed instead. Exploiting this vulnerability could allow a low privileged user to acquire `superuser` privileges, which would allow full, unrestricted access to all data and database functions. And could lead to arbitrary code execution or data access on the underlying host as the `postgres` user. The issue has been patched as of version 1.1.9.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32305.json
- https://github.com/aiven/aiven-extras/security/advisories/GHSA-7r4w-fw4h-67gp
- https://nvd.nist.gov/vuln/detail/CVE-2023-32305
- https://security.netapp.com/advisory/ntap-20230616-0006/
- https://github.com/aiven/aiven-extras/commit/8682ae01bec0791708bf25791786d776e2fb0250
