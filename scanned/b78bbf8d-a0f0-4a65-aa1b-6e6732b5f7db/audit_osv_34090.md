# [H] glpi-screenshot-plugin exposes local files in /ajax/screenshot.php

## Summary
Severity: High
Advisory: CVE-2025-54780
Aliases: GHSA-x6mp-jhxw-9xrp
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-08-05
Source: https://osv.dev/vulnerability/CVE-2025-54780
Type: osv

## Details
The glpi-screenshot-plugin allows users to take screenshots or screens recording directly from GLPI. In versions below 2.0.2, authenticated user can use the /ajax/screenshot.php endpoint to leak files from the system or use PHP wrappers. This is fixed in version 2.0.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54780.json
- https://github.com/cconard96/glpi-screenshot-plugin/security/advisories/GHSA-x6mp-jhxw-9xrp
- https://nvd.nist.gov/vuln/detail/CVE-2025-54780
- https://github.com/cconard96/glpi-screenshot-plugin/commit/49215b53a05dc792719b69c098df80100208c2c8
