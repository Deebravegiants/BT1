# [M] Emlog: Local File Inclusion in plugin.php via unsanitized plugin parameter

## Summary
Severity: Medium
Advisory: CVE-2026-34787
Aliases: GHSA-7mvq-qj5x-5phm
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-34787
Type: osv

## Details
Emlog is an open source website building system. In versions 2.6.2 and prior, a Local File Inclusion (LFI) vulnerability exists in admin/plugin.php at line 80. The $plugin parameter from the GET request is directly used in a require_once path without proper sanitization. If the CSRF token check can be bypassed (see potential bypass conditions), an attacker can include arbitrary PHP files from the server filesystem, leading to code execution. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34787.json
- https://github.com/emlog/emlog/security/advisories/GHSA-7mvq-qj5x-5phm
- https://nvd.nist.gov/vuln/detail/CVE-2026-34787
