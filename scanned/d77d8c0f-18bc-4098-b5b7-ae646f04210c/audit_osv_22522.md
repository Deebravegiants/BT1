# [H] Incorrect Default Permissions in ldap-account-manager

## Summary
Severity: High
Advisory: CVE-2022-31087
Aliases: GHSA-q8g5-45m4-q95p
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2022-31087
Type: osv

## Details
LDAP Account Manager (LAM) is a webfrontend for managing entries (e.g. users, groups, DHCP settings) stored in an LDAP directory. In versions prior to 8.0 the tmp directory, which is accessible by /lam/tmp/, allows interpretation of .php (and .php5/.php4/.phpt/etc) files. An attacker capable of writing files under www-data privileges can write a web-shell into this directory, and gain a Code Execution on the host. This issue has been fixed in version 8.0. Users unable to upgrade should disallow executing PHP scripts in (/var/lib/ldap-account-manager/)tmp directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31087.json
- https://github.com/LDAPAccountManager/lam/security/advisories/GHSA-q8g5-45m4-q95p
- https://nvd.nist.gov/vuln/detail/CVE-2022-31087
- https://www.debian.org/security/2022/dsa-5177
- https://github.com/LDAPAccountManager/lam/commit/f1d5d04952f39a1b4ea203d3964fa88e1429dfd4
