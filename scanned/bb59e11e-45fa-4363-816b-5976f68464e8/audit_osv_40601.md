# [M] Emlog: Zip Slip Path Traversal in Plugin/Template ZIP Upload Enables RCE

## Summary
Severity: Medium
Advisory: CVE-2026-53757
Aliases: GHSA-gjj4-37r4-mf5g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-53757
Type: osv

## Details
Emlog is an open source website building system. In versions 2.6.29 and prior, the emUnZip() function extracts all ZIP entries via ZipArchive::extractTo() without validating entry paths for ../ traversal sequences. Only the first entry's subdirectory structure is checked. An attacker can overwrite arbitrary files on the server filesystem, including config.php for immediate RCE. At time of publication, there are no publicly known patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53757.json
- https://github.com/emlog/emlog/security/advisories/GHSA-gjj4-37r4-mf5g
- https://nvd.nist.gov/vuln/detail/CVE-2026-53757
