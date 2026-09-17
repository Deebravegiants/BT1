# [H] CVE-2025-53510

## Summary
Severity: High
Advisory: CVE-2025-53510
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-08-25
Source: https://osv.dev/vulnerability/CVE-2025-53510
Type: osv

## Details
A memory corruption vulnerability exists in the PSD Image Decoding functionality of the SAIL Image Decoding Library v0.9.8. When loading a specially crafted .psd file, an integer overflow can be made to occur when calculating the stride for decoding. Afterwards, this will cause a heap-based buffer to overflow when decoding the image which can lead to remote code execution. An attacker will need to convince the library to read a file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2025-2218
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2218
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53510.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-53510
