# [M] rConfig < 8.2.13 Path Traversal File Read via FileDownloadController

## Summary
Severity: Medium
Advisory: CVE-2026-64826
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-64826
Type: osv

## Details
rConfig before 8.2.13 contains a path traversal vulnerability that allows authenticated attackers to read arbitrary files by supplying unsanitized directory traversal sequences in the filename GET parameter of the download_export() method. Attackers can craft requests with ../ sequences to escape the exports base directory and access sensitive files readable by the web server process, including application environment files containing encryption keys, database credentials, and mail configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64826.json
- https://github.com/rconfig/rconfig/releases/tag/core-8.2.13
- https://nvd.nist.gov/vuln/detail/CVE-2026-64826
- https://www.vulncheck.com/advisories/rconfig-path-traversal-file-read-via-filedownloadcontroller
- https://github.com/rconfig/rconfig/pull/349
- https://github.com/rconfig/rconfig/commit/d133a466a2df9d065177de9a8ed50f1bfe438aee
- https://github.com/rconfig/rconfig
