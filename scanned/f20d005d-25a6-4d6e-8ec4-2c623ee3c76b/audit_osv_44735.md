# [C] TEN Framework 0.11.71 Unauthenticated File Read/Write via TMAN Designer

## Summary
Severity: Critical
Advisory: CVE-2026-85688
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85688
Type: osv

## Details
TEN Framework 0.11.71 contains unauthenticated arbitrary file read and write vulnerabilities in the TMAN Designer file-content API endpoints. Attackers can submit POST and PUT requests to the /api/designer/v1/file-content endpoints to read arbitrary files or write malicious content to system paths, enabling code execution through authorized_keys, cron files, or executable graph files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85688.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85688
- https://www.vulncheck.com/advisories/ten-framework-0.11.71-unauthenticated-file-read-write-via-tman-designer
- https://github.com/TEN-framework/ten-framework/issues/2187
- https://github.com/TEN-framework/ten-framework
- https://github.com/TEN-framework/ten-framework/blob/0.11.71/core/src/ten_manager/src/designer/file_content/mod.rs
