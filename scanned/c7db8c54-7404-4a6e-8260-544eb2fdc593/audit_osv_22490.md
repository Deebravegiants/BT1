# [M] Privilege escalation from administrator in eLabFTW

## Summary
Severity: Medium
Advisory: CVE-2022-31007
Aliases: GHSA-937c-m7p3-775v
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-05-31
Source: https://osv.dev/vulnerability/CVE-2022-31007
Type: osv

## Details
eLabFTW is an electronic lab notebook manager for research teams. Prior to version 4.3.0, a vulnerability allows an authenticated user with an administrator role in a team to assign itself system administrator privileges within the application, or create a new system administrator account. The issue has been corrected in eLabFTW version 4.3.0. In the context of eLabFTW, an administrator is a user account with certain privileges to manage users and content in their assigned team/teams. A system administrator account can manage all accounts, teams and edit system-wide settings within the application. The impact is not deemed as high, as it requires the attacker to have access to an administrator account. Regular user accounts cannot exploit this to gain admin rights. A workaround for one if the issues is removing the ability of administrators to create accounts.

## References
- https://github.com/elabftw/elabftw/releases/tag/4.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31007.json
- https://github.com/elabftw/elabftw/security/advisories/GHSA-937c-m7p3-775v
- https://nvd.nist.gov/vuln/detail/CVE-2022-31007
