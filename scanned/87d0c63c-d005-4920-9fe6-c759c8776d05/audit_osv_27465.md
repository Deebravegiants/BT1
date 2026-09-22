# [C] CVE-2024-22088

## Summary
Severity: Critical
Advisory: CVE-2024-22088
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/CVE-2024-22088
Type: osv

## Details
Lotos WebServer through 0.1.1 (commit 3eb36cc) has a use-after-free in buffer_avail() at buffer.h via a long URI, because realloc is mishandled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22088.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-22088
- https://github.com/chendotjs/lotos/issues/7
