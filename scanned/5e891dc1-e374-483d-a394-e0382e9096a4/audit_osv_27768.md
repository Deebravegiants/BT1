# [H] Unauthorised granting of administrator privileges over arbitrary teams under certain circumstances

## Summary
Severity: High
Advisory: CVE-2024-25632
Aliases: GHSA-6m7p-gh9f-5mgg
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2024-10-01
Source: https://osv.dev/vulnerability/CVE-2024-25632
Type: osv

## Details
eLabFTW is an open source electronic lab notebook for research labs. In the context of eLabFTW, an administrator is a user account with certain privileges to manage users and content in their assigned team/teams. A user may be an administrator in one team and a regular user in another. The vulnerability allows a regular user to become administrator of a team where they are a member, under a reasonable configuration. Additionally, in eLabFTW versions subsequent to v5.0.0, the vulnerability may allow an initially unauthenticated user to gain administrative privileges over an arbitrary team. The vulnerability does not affect system administrator status. Users should upgrade to version 5.1.0. System administrators are advised to turn off local user registration, saml_team_create and not allow administrators to import users into teams, unless strictly required.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25632.json
- https://github.com/elabftw/elabftw/security/advisories/GHSA-6m7p-gh9f-5mgg
- https://nvd.nist.gov/vuln/detail/CVE-2024-25632
