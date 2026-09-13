# [H] CVE-2025-35984

## Summary
Severity: High
Advisory: CVE-2025-35984
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-08-25
Source: https://osv.dev/vulnerability/CVE-2025-35984
Type: osv

## Details
A memory corruption vulnerability exists in the PCX Image Decoding functionality of the SAIL Image Decoding Library v0.9.8. When decoding the image data from a specially crafted .pcx file, a heap-based buffer overflow can occur which allows for remote code execution. An attacker will need to convince the library to read a file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2025-2217
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2217
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/35xxx/CVE-2025-35984.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-35984
