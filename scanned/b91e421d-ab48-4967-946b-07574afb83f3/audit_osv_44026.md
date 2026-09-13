# [M] rConfig Core 8.0.0 < 8.2.13 Core Path Traversal via Export Download Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-77914
Aliases: GHSA-m5rw-jcrm-mmwc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-77914
Type: osv

## Details
rConfig Core 8.0.0 before 8.2.13 contains a path traversal vulnerability that allows authenticated users to read arbitrary files by supplying crafted filenames containing directory traversal sequences to the export download endpoint. Attackers can manipulate the filename parameter with traversal sequences to escape the intended export directory and access files outside it that are readable by the application process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77914.json
- https://github.com/rconfig/rconfig/releases/tag/core-8.2.13
- https://github.com/rconfig/rconfig/security/advisories/GHSA-m5rw-jcrm-mmwc
- https://nvd.nist.gov/vuln/detail/CVE-2026-77914
- https://www.vulncheck.com/advisories/rconfig-v8-core-path-traversal-via-export-download-endpoint
- https://github.com/rconfig/rconfig
