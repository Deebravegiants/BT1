# [M] Arbitrary config values override in lam

## Summary
Severity: Medium
Advisory: CVE-2024-52792
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-12-17
Source: https://osv.dev/vulnerability/CVE-2024-52792
Type: osv

## Details
LDAP Account Manager (LAM) is a php webfrontend for managing entries (e.g. users, groups, DHCP settings) stored in an LDAP directory. In affected versions LAM does not properly sanitize configuration values, that are set via `mainmanage.php` and `confmain.php`. This allows setting arbitrary config values and thus effectively bypassing `mitigation` of CVE-2024-23333/GHSA-fm9w-7m7v-wxqv. Configuration values for the main config or server profiles are set via `mainmanage.php` and `confmain.php`.
The values are written to `config.cfg` or `serverprofile.conf` in the format of `settingsName: settingsValue` line-by-line.
An attacker can smuggle arbitrary config values in a config file, by inserting a newline into certain config fields, followed by the value. This vulnerability has been addressed in version 9.0. All users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/LDAPAccountManager/lam/blob/fd665fef3b222bf8205154b14f676815d2d6ae20/lam/templates/config/mainmanage.php#L263
- https://github.com/LDAPAccountManager/lam/releases/tag/9.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52792.json
- https://github.com/LDAPAccountManager/lam/security/advisories/GHSA-6cp9-j5r7-xhcc
- https://github.com/LDAPAccountManager/lam/security/advisories/GHSA-fm9w-7m7v-wxqv
- https://nvd.nist.gov/vuln/detail/CVE-2024-52792
