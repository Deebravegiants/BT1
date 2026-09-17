# [M] PYSEC-2023-195

## Summary
Severity: Medium
Advisory: PYSEC-2023-195
Aliases: CVE-2023-41047, GHSA-fwfg-vprh-97ph
Ecosystem: PyPI
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-10-09
Source: https://osv.dev/vulnerability/PYSEC-2023-195
Type: osv

## Affected
- PyPI: `octoprint` — affected >=0 <d0072cff894509c77e243d6562245ad3079e17db, >=0 <1.9.3

## Details
OctoPrint is a web interface for 3D printers. OctoPrint versions up until and including 1.9.2 contain a vulnerability that allows malicious admins to configure a specially crafted GCODE script that will allow code execution during rendering of that script. An attacker might use this to extract data managed by OctoPrint, or manipulate data managed by OctoPrint, as well as execute arbitrary commands with the rights of the OctoPrint process on the server system. OctoPrint versions from 1.9.3 onward have been patched. Administrators of OctoPrint instances are advised to make sure they can trust all other administrators on their instance and to also not blindly configure arbitrary GCODE scripts found online or provided to them by third parties.

## References
- https://github.com/OctoPrint/OctoPrint/commit/d0072cff894509c77e243d6562245ad3079e17db
- https://github.com/OctoPrint/OctoPrint/releases/tag/1.9.3
- https://github.com/OctoPrint/OctoPrint/security/advisories/GHSA-fwfg-vprh-97ph
