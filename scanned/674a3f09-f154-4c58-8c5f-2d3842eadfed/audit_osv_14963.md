# [C] CVE-2019-12723

## Summary
Severity: Critical
Advisory: CVE-2019-12723
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-10
Source: https://osv.dev/vulnerability/CVE-2019-12723
Type: osv

## Details
An issue was discovered in the Teclib Fields plugin through 1.9.2 for GLPI. it allows SQL Injection via container_id and old_order parameters to ajax/reorder.php by an unauthenticated user.

## References
- https://github.com/pluginsGLPI/fields/blob/master/ajax/reorder.php
- https://github.com/pluginsGLPI/fields/pull/317
- https://github.com/pluginsGLPI/fields/releases/tag/1.10.0
