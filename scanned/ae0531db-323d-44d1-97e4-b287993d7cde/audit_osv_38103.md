# [H] Emlog: Path Traversal in emUnZip() allows arbitrary file write leading to RCE

## Summary
Severity: High
Advisory: CVE-2026-34607
Aliases: GHSA-2jg8-rmhm-xv9m
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-34607
Type: osv

## Details
Emlog is an open source website building system. In versions 2.6.2 and prior, a path traversal vulnerability exists in the emUnZip() function (include/lib/common.php:793). When extracting ZIP archives (plugin/template uploads, backup imports), the function calls $zip->extractTo($path) without sanitizing ZIP entry names. An authenticated admin can upload a crafted ZIP containing entries with ../ sequences to write arbitrary files to the server filesystem, including PHP webshells, achieving Remote Code Execution (RCE). At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34607.json
- https://github.com/emlog/emlog/security/advisories/GHSA-2jg8-rmhm-xv9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-34607
