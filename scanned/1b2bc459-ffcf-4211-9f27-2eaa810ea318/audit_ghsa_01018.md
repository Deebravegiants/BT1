# [M] Lack of URL normalization may lead to authorization bypass when URL access rules are used

## Summary
Severity: Medium
Advisory: GHSA-x44x-r84w-8v67
CVE: CVE-2020-24660
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-09
Source: https://github.com/advisories/GHSA-x44x-r84w-8v67
Type: github-advisory

## Affected
- npm: `lemonldap-ng-handler` — affected >=0 <0.5.2

## Details
### Impact
When access rules are used inside a protected host, some URL encodings may bypass filtering system.

### Patches
Version 0.5.2 includes a patch that fixes the vulnerability

### Workarounds
No way for users to fix or remediate the vulnerability without upgrading

### References
https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/issues/2290

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [this repository](https://github.com/LemonLDAPNG/node-lemonldap-ng-handler/issues) or [LemonLDAP::NG GitLab](https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/issues)
* Email us at [lemonldap-ng-users@ow2.org](mailto:lemonldap-ng-users@ow2.org)

## References
- https://github.com/LemonLDAPNG/node-lemonldap-ng-handler/security/advisories/GHSA-x44x-r84w-8v67
- https://nvd.nist.gov/vuln/detail/CVE-2020-24660
- https://github.com/LemonLDAPNG/node-lemonldap-ng-handler/commit/136aa83ed431462fa42ce17b7f9b24e056de06be
- https://github.com/LemonLDAPNG/node-lemonldap-ng-handler
- https://github.com/LemonLDAPNG/node-lemonldap-ng-handler/releases/tag/0.5.2
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/issues/2290
- https://snyk.io/vuln/SNYK-JS-NODELEMONLDAPNGHANDLER-655999
- https://www.debian.org/security/2020/dsa-4762
- https://www.npmjs.com/package/lemonldap-ng-handler
