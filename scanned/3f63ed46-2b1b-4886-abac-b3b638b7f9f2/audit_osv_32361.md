# [M] CVE-2025-28162

## Summary
Severity: Medium
Advisory: CVE-2025-28162
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2025-28162
Type: osv

## Details
Buffer Overflow vulnerability in libpng 1.6.43-1.6.46 allows a local attacker to cause a denial of service via the pngimage with AddressSanitizer (ASan), the program leaks memory in various locations, eventually leading to high memory usage and causing the program to become unresponsive

## References
- https://gist.github.com/kittener/fbfdb9b5610c6b3db0d5dea045a07c60
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/28xxx/CVE-2025-28162.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-28162
- https://github.com/pnggroup/libpng/issues/656
