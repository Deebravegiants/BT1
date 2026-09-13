# [H] CVE-2025-52930

## Summary
Severity: High
Advisory: CVE-2025-52930
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-08-25
Source: https://osv.dev/vulnerability/CVE-2025-52930
Type: osv

## Details
A memory corruption vulnerability exists in the BMPv3 RLE Decoding functionality of the SAIL Image Decoding Library v0.9.8. When decompressing the image data from a specially crafted .bmp file, a heap-based buffer overflow can occur which allows for remote code execution. An attacker will need to convince the library to read a file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2025-2221
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2221
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52930.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52930
