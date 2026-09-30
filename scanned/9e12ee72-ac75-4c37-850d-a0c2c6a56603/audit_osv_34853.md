# [C] CVE-2025-65834

## Summary
Severity: Critical
Advisory: CVE-2025-65834
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-65834
Type: osv

## Details
Meltytech Shotcut 25.10.31 is vulnerable to Buffer Overflow. A memory access violation occurs when processing MLT project files with manipulated width and height parameters. By setting these values to extremely large numbers, the application attempts to allocate excessive memory during image processing, triggering a buffer overflow in the mlt_image_fill_white function.

## References
- https://bytescan.net/CVE/cve-2025-65834.html
- https://sourceforge.net/projects/shotcut/files/v25.10.31/shotcut-macos-25.10.31.dmg/download
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65834.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65834
