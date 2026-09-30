# [H] Streama Subtitle Download Path Traversal and SSRF Leading to Arbitrary File Write

## Summary
Severity: High
Advisory: CVE-2025-34452
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:L/SI:L/SA:N)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-34452
Type: osv

## Details
Streama versions 1.10.0 through 1.10.5 and prior to commit b7c8767 contain a combination of path traversal and server-side request forgery (SSRF) vulnerabilities in that allow an authenticated attacker to write arbitrary files to the server filesystem. The issue exists in the subtitle download functionality, where user-controlled parameters are used to fetch remote content and construct file paths without proper validation. By supplying a crafted subtitle download URL and a path traversal sequence in the file name, an attacker can write files to arbitrary locations on the server, potentially leading to remote code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34452.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34452
- https://www.vulncheck.com/advisories/streama-subtitle-download-path-traversal-and-ssrf-leading-to-arbitrary-file-write
- https://github.com/streamaserver/streama/commit/b7c8767
- https://github.com/streamaserver/streama
- https://chocapikk.com/posts/2025/streama-path-traversal-ssrf/
