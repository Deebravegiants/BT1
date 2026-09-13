# [C] Crater Invoice 6.0.6 Path Traversal RCE via update/unzip endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-57863
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-57863
Type: osv

## Details
Crater Invoice through 6.0.6 contains a path traversal vulnerability in the self-update API that allows authenticated company owners to write arbitrary files outside the intended extraction directory by supplying crafted ZIP archives with ../ sequences to the unzip endpoint. Attackers can exploit unsanitized ZIP entry names passed to PHP's ZipArchive::extractTo() to write arbitrary PHP files into the web-accessible public directory and achieve remote code execution on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57863.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57863
- https://www.vulncheck.com/advisories/crater-invoice-path-traversal-rce-via-update-unzip-endpoint
- https://github.com/crater-invoice-inc/crater
- https://gist.github.com/sermikr0/cc58727e6a777b6ea1104e923803a0ba
