# [M] CVE-2021-39211

## Summary
Severity: Medium
Advisory: CVE-2021-39211
Aliases: GHSA-xx66-v3g5-w825
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-09-15
Source: https://osv.dev/vulnerability/CVE-2021-39211
Type: osv

## Details
GLPI is a free Asset and IT management software package. Starting in version 9.2 and prior to version 9.5.6, the telemetry endpoint discloses GLPI and server information. This issue is fixed in version 9.5.6. As a workaround, remove the file `ajax/telemetry.php`, which is not needed for usual functions of GLPI.

## References
- https://github.com/glpi-project/glpi/releases/tag/9.5.6
- https://github.com/glpi-project/glpi/security/advisories/GHSA-xx66-v3g5-w825
