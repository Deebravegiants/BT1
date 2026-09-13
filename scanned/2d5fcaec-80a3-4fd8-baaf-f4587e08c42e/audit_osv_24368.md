# [H] CVE-2023-0996

## Summary
Severity: High
Advisory: CVE-2023-0996
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-02-24
Source: https://osv.dev/vulnerability/CVE-2023-0996
Type: osv

## Details
There is a vulnerability in the strided image data parsing code in the emscripten wrapper for libheif. An attacker could exploit this through a crafted image file to cause a buffer overflow in linear memory during a memcpy call.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0996.json
- https://govtech-csg.github.io/security-advisories/2023/02/24/CVE-2023-0996.html
- https://nvd.nist.gov/vuln/detail/CVE-2023-0996
- https://github.com/strukturag/libheif/pull/759
- https://github.com/strukturag/libheif
