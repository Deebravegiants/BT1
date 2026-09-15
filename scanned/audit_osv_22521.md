# [M] Incorrect Regular Expressions in ldap-account-manager

## Summary
Severity: Medium
Advisory: CVE-2022-31086
Aliases: GHSA-q9pc-x84w-982x
CVSS: 6.6 (CVSS:3.0/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2022-31086
Type: osv

## Details
LDAP Account Manager (LAM) is a webfrontend for managing entries (e.g. users, groups, DHCP settings) stored in an LDAP directory. In versions prior to 8.0 incorrect regular expressions allow to upload PHP scripts to config/templates/pdf. This vulnerability could lead to a Remote Code Execution if the /config/templates/pdf/ directory is accessible for remote users. This is not a default configuration of LAM. This issue has been fixed in version 8.0. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31086.json
- https://github.com/LDAPAccountManager/lam/security/advisories/GHSA-q9pc-x84w-982x
- https://nvd.nist.gov/vuln/detail/CVE-2022-31086
- https://www.debian.org/security/2022/dsa-5177
- https://github.com/LDAPAccountManager/lam/commit/f1d5d04952f39a1b4ea203d3964fa88e1429dfd4
