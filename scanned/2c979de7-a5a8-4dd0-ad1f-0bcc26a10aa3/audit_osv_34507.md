# [M] CVE-2025-61154

## Summary
Severity: Medium
Advisory: CVE-2025-61154
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-12
Source: https://osv.dev/vulnerability/CVE-2025-61154
Type: osv

## Details
Heap buffer overflow vulnerability in LibreDWG versions v0.13.3.7571 up to v0.13.3.7835 allows a crafted DWG file to cause a Denial of Service (DoS) via the function decompress_R2004_section at decode.c.

## References
- https://davizin.com/cves/CVE-2025-61154.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61154.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-61154
- https://github.com/LibreDWG/libredwg/issues/1180
