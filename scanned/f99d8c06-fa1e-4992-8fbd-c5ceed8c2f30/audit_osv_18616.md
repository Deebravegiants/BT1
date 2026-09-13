# [C] CVE-2020-29006

## Summary
Severity: Critical
Advisory: CVE-2020-29006
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-24
Source: https://osv.dev/vulnerability/CVE-2020-29006
Type: osv

## Details
MISP before 2.4.135 lacks an ACL check, related to app/Controller/GalaxyElementsController.php and app/Model/GalaxyElement.php.

## References
- https://github.com/MISP/MISP/compare/v2.4.134...v2.4.135
- https://github.com/MISP/MISP/commit/423750573d07f1a463f115ef37182c1825080da4
