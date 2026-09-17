# [H] CVE-2022-0137

## Summary
Severity: High
Advisory: CVE-2022-0137
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-11-14
Source: https://osv.dev/vulnerability/CVE-2022-0137
Type: osv

## Details
A heap buffer overflow in image_set_mask function of HTMLDOC before 1.9.15 allows an attacker to write outside the buffer boundaries.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0137.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-0137
- https://github.com/michaelrsweet/htmldoc/issues/461
- https://github.com/michaelrsweet/htmldoc/commit/71fe87878c9cbc3db429f5e5c70f28e4b3d96e3b
- https://github.com/michaelrsweet/htmldoc
