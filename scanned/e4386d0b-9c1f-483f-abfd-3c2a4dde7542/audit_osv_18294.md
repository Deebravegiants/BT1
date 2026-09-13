# [M] CVE-2020-25860

## Summary
Severity: Medium
Advisory: CVE-2020-25860
Aliases: GHSA-cgf3-h62j-w9vv
CVSS: 6.6 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-21
Source: https://osv.dev/vulnerability/CVE-2020-25860
Type: osv

## Details
The install.c module in the Pengutronix RAUC update client prior to version 1.5 has a Time-of-Check Time-of-Use vulnerability, where signature verification on an update file takes place before the file is reopened for installation. An attacker who can modify the update file just before it is reopened can install arbitrary code on the device.

## References
- https://github.com/rauc/rauc/security/advisories/GHSA-cgf3-h62j-w9vv
- https://www.vdoo.com/blog/cve-2020-25860-significant-vulnerability-discovered-rauc-embedded-firmware-update-framework
