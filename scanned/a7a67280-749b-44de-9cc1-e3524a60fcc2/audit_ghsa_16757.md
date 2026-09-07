# [M] silverstripe/framework's `Member.Name` is not escaped

## Summary
Severity: Medium
Advisory: GHSA-r9vp-fp72-xgf7
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-r9vp-fp72-xgf7
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.1.9-rc1 <3.1.20
- Packagist: `silverstripe/framework` — affected >=3.2.4-rc1 <3.2.5
- Packagist: `silverstripe/framework` — affected >=3.3.2-rc1 <3.3.3
- Packagist: `silverstripe/framework` — affected >=3.4.0-rc1 <3.4.1

## Details
The core template `framework/templates/Includes/GridField_print.ss` uses "Printed by $Member.Name".

If the currently logged in members first name or surname contain XSS, this prints the raw HTML out, because Member->getName() just returns the raw FirstName + Surname as a string, which is injected directly.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/281b0de571fe0ae159ac47891c02acf2214fa619
- https://github.com/silverstripe/silverstripe-framework/commit/6817c57f64b9eb2b271b81662cd83b074a3daee4
- https://github.com/silverstripe/silverstripe-framework/commit/83e3302c0425d9b0e4fe42e82e3df03379f4dca5
- https://github.com/silverstripe/silverstripe-framework/commit/8bbf1caae665a07b3e44e8d5d32556a03d38c296
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2016-013-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2016-013
