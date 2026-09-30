# [H] glpi Unauthorized access to inventory files

## Summary
Severity: High
Advisory: CVE-2023-22500
Aliases: GHSA-3ghv-p34r-5ghx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-01-25
Source: https://osv.dev/vulnerability/CVE-2023-22500
Type: osv

## Details
GLPI is a Free Asset and IT Management Software package. Versions 10.0.0 and above, prior to 10.0.6 are vulnerable to Incorrect Authorization. This vulnerability allow unauthorized access to inventory files. Thus, if anonymous access to FAQ is allowed, inventory files are accessbile by unauthenticated users. This issue is patched in version 10.0.6. As a workaround, disable native inventory and delete inventory files from server (default location is `files/_inventory`).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22500.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-3ghv-p34r-5ghx
- https://nvd.nist.gov/vuln/detail/CVE-2023-22500
