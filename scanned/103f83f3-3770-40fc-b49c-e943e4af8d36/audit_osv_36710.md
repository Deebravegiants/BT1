# [M] CVE-2026-25210

## Summary
Severity: Medium
Advisory: CVE-2026-25210
CVSS: 6.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-01-30
Source: https://osv.dev/vulnerability/CVE-2026-25210
Type: osv

## Details
In libexpat before 2.7.4, the doContent function does not properly determine the buffer size bufSize because there is no integer overflow check for tag buffer reallocation.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://github.com/libexpat/libexpat/pull/1075/commits/9c2d990389e6abe2e44527eeaa8b39f16fe859c7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25210.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25210
- https://github.com/libexpat/libexpat/pull/1075
