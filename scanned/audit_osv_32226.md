# [M] CVE-2025-26058

## Summary
Severity: Medium
Advisory: CVE-2025-26058
CVSS: 4.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2025-26058
Type: osv

## Details
Webkul QloApps v1.6.1 exposes authentication tokens in URLs during redirection. When users access the admin panel or other protected areas, the application appends sensitive authentication tokens directly to the URL.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26058.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-26058
- https://github.com/mano257200/QloApps-VUL
