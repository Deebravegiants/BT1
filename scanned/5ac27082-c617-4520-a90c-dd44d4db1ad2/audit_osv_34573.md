# [H] OctoPrint-SpoolManager Plugin APIs do not enforce authentication

## Summary
Severity: High
Advisory: CVE-2025-62169
Aliases: GHSA-2rrc-f24f-94f6
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-23
Source: https://osv.dev/vulnerability/CVE-2025-62169
Type: osv

## Details
OctoPrint-SpoolManager is a plugin for managing spools and all their usage metadata. In versions 1.8.0a2 and older of the testing branch and versions 1.7.7 and older of the stable branch, the APIs of the OctoPrint-SpoolManager plugin do not correctly enforce authentication or authorization checks. This issue has been patched in versions 1.8.0a3 of the testing branch and 1.7.8 of the stable branch. The impact of this vulnerability is greatly reduced when using OctoPrint version 1.11.2 and newer.

## References
- https://github.com/WildRikku/OctoPrint-SpoolManager/releases/tag/1.7.8
- https://github.com/WildRikku/OctoPrint-SpoolManager/releases/tag/1.8.0a3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62169.json
- https://github.com/WildRikku/OctoPrint-SpoolManager/security/advisories/GHSA-2rrc-f24f-94f6
- https://nvd.nist.gov/vuln/detail/CVE-2025-62169
- https://github.com/WildRikku/OctoPrint-SpoolManager/commit/b725e113316e177ce81238a2dbbbdb63d92c40b0
