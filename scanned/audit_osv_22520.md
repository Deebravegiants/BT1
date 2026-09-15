# [M] Missing Encryption of Sensitive Data in ldap-account-manager

## Summary
Severity: Medium
Advisory: CVE-2022-31085
Aliases: GHSA-6m3q-5c84-6h6j
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2022-31085
Type: osv

## Details
LDAP Account Manager (LAM) is a webfrontend for managing entries (e.g. users, groups, DHCP settings) stored in an LDAP directory. In versions prior to 8.0 the session files include the LDAP user name and password in clear text if the PHP OpenSSL extension is not installed or encryption is disabled by configuration. This issue has been fixed in version 8.0. Users unable to upgrade should install the PHP OpenSSL extension and make sure session encryption is enabled in LAM main configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31085.json
- https://github.com/LDAPAccountManager/lam/security/advisories/GHSA-6m3q-5c84-6h6j
- https://nvd.nist.gov/vuln/detail/CVE-2022-31085
- https://www.debian.org/security/2022/dsa-5177
- https://github.com/LDAPAccountManager/lam/commit/f1d5d04952f39a1b4ea203d3964fa88e1429dfd4
