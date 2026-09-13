# [H] GLPI vulnerable to enumeration of users' email addresses by unauthenticated user

## Summary
Severity: High
Advisory: CVE-2024-43416
Aliases: GHSA-j8gc-xpgr-2ww7
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-11-18
Source: https://osv.dev/vulnerability/CVE-2024-43416
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 0.80 and prior to version 10.0.17, an unauthenticated user can use an application endpoint to check if an email address corresponds to a valid GLPI user. Version 10.0.17 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43416.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-j8gc-xpgr-2ww7
- https://nvd.nist.gov/vuln/detail/CVE-2024-43416
- https://github.com/glpi-project/glpi/commit/9be1466053f829680db318f7e7e5880d2d789c6d
