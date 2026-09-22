# [C] Unauthenticated Remote Code Execution in ldap-account-manager

## Summary
Severity: Critical
Advisory: CVE-2022-31084
Aliases: GHSA-r387-grjx-qgvw
CVSS: 9.0 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2022-31084
Type: osv

## Details
LDAP Account Manager (LAM) is a webfrontend for managing entries (e.g. users, groups, DHCP settings) stored in an LDAP directory. In versions prior to 8.0 There are cases where LAM instantiates objects from arbitrary classes. An attacker can inject the first constructor argument. This can lead to code execution if non-LAM classes are instantiated that execute code during object creation. This issue has been fixed in version 8.0.

## References
- https://swarm.ptsecurity.com/exploiting-arbitrary-object-instantiations/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31084.json
- https://github.com/LDAPAccountManager/lam/security/advisories/GHSA-r387-grjx-qgvw
- https://nvd.nist.gov/vuln/detail/CVE-2022-31084
- https://www.debian.org/security/2022/dsa-5177
- https://github.com/LDAPAccountManager/lam/commit/f1d5d04952f39a1b4ea203d3964fa88e1429dfd4
