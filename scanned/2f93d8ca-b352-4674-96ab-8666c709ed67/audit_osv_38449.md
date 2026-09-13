# [M] Cacti: Arbitrary File Read via Path Traversal in Report `format_file` Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-40084
Aliases: GHSA-mjvw-mhj5-9jcj
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-40084
Type: osv

## Details
Cacti is an open source performance and fault management framework. Versions 1.2.30 and prior are vulnerable to Path Traversal  through the Report format_file Parameter, causing arbitrary file read. This vulnerability occurs in two stages. In the first stage (stored injection), lib/html_reports.php at line 283 stores $save['format_file'] =  $post['format_file'] directly into the database without any validation. In the second stage (file read), lib/reports.php at line 667 concatenates  CACTI_PATH_FORMATS . '/' . $format_file, and line 670 then calls file($format_file), reading arbitrary files from the filesystem. This issue has been fixed in version 1.2.31.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40084.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-mjvw-mhj5-9jcj
- https://nvd.nist.gov/vuln/detail/CVE-2026-40084
- https://github.com/Cacti/cacti/commit/4c09efaebf3a9faec66969d0b5c4aceaf397f37f
