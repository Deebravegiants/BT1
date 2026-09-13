# [C] CVE-2017-11329

## Summary
Severity: Critical
Advisory: CVE-2017-11329
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-11329
Type: osv

## Details
GLPI before 9.1.5 allows SQL injection via an ajax/getDropdownValue.php request with an entity_restrict parameter that is not a list of integers.

## References
- https://github.com/glpi-project/glpi/issues/2456
- https://github.com/glpi-project/glpi/releases/tag/9.1.5
