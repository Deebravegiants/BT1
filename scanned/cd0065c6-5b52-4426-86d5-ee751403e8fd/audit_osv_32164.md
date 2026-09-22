# [M] GLPI allows unauthorized access to debug mode

## Summary
Severity: Medium
Advisory: CVE-2025-25192
Aliases: GHSA-86cx-hcfc-8mm8
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-02-25
Source: https://osv.dev/vulnerability/CVE-2025-25192
Type: osv

## Details
GLPI is a free asset and IT management software package. Prior to version 10.0.18, a low privileged user can enable debug mode and access sensitive information. Version 10.0.18 contains a patch. As a workaround, one may delete the `install/update.php` file.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.18
- https://www.vicarius.io/vsociety/posts/cve-2025-25192-detection-glpi-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2025-25192-mitigation-glpi-vulnerability
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25192.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-86cx-hcfc-8mm8
- https://nvd.nist.gov/vuln/detail/CVE-2025-25192
