# [M] Out of Bounds read in libjxl

## Summary
Severity: Medium
Advisory: CVE-2023-0645
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-11
Source: https://osv.dev/vulnerability/CVE-2023-0645
Type: osv

## Details
An out of bounds read exists in libjxl. An attacker using a specifically crafted file could cause an out of bounds read in the exif handler. We recommend upgrading to version 0.8.1 or past commit  https://github.com/libjxl/libjxl/pull/2101/commits/d95b050c1822a5b1ede9e0dc937e43fca1b10159 https://github.com/libjxl/libjxl/pull/2101/commits/d95b050c1822a5b1ede9e0dc937e43fca1b10159

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/3
- https://github.com/libjxl/libjxl/pull/2101/commits/d95b050c1822a5b1ede9e0dc937e43fca1b10159
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0645.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0645
- https://github.com/libjxl/libjxl/pull/2101
- https://github.com/libjxl/libjxl
