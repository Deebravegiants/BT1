# [H] CVE-2025-46407

## Summary
Severity: High
Advisory: CVE-2025-46407
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-08-25
Source: https://osv.dev/vulnerability/CVE-2025-46407
Type: osv

## Details
A memory corruption vulnerability exists in the BMPv3 Palette Decoding functionality of the SAIL Image Decoding Library v0.9.8. When loading a specially crafted .bmp file, an integer overflow can be made to occur which will cause a heap-based buffer to overflow when reading the palette from the image. These conditions can allow for remote code execution. An attacker will need to convince the library to read a file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2025-2215
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2215
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46407.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-46407
