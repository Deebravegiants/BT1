# [C] CVE-2024-22087

## Summary
Severity: Critical
Advisory: CVE-2024-22087
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/CVE-2024-22087
Type: osv

## Details
route in main.c in Pico HTTP Server in C through f3b69a6 has an sprintf stack-based buffer overflow via a long URI, leading to remote code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22087.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-22087
- https://github.com/foxweb/pico/issues/31
- https://github.com/foxweb/pico/commit/7a5e4e242121c839cb77f5b9003e735a852f4e58
- https://github.com/foxweb/pico/commit/e2d172f
