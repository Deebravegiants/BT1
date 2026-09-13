# [M] Unauthenticated LDAP Injection in ldap-account-manager

## Summary
Severity: Medium
Advisory: CVE-2022-31088
Aliases: GHSA-wxf8-9x99-6gp4
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2022-31088
Type: osv

## Details
LDAP Account Manager (LAM) is a webfrontend for managing entries (e.g. users, groups, DHCP settings) stored in an LDAP directory. In versions prior to 8.0 the user name field at login could be used to enumerate LDAP data. This is only the case for LDAP search configuration. This issue has been fixed in version 8.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31088.json
- https://github.com/LDAPAccountManager/lam/security/advisories/GHSA-wxf8-9x99-6gp4
- https://nvd.nist.gov/vuln/detail/CVE-2022-31088
- https://www.debian.org/security/2022/dsa-5177
- https://github.com/LDAPAccountManager/lam/commit/f1d5d04952f39a1b4ea203d3964fa88e1429dfd4
