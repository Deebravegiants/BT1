# [H] CVE-2023-29578

## Summary
Severity: High
Advisory: CVE-2023-29578
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-29578
Type: osv

## Details
mp4v2 v2.0.0 was discovered to contain a heap buffer overflow via the mp4v2::impl::MP4StringProperty::~MP4StringProperty() function at src/mp4property.cpp.

## References
- https://github.com/z1r00/fuzz_vuln/blob/main/mp4v2/heap-buffer-overflow/mp4property.cpp/readme.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29578.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29578
- https://github.com/TechSmith/mp4v2/issues/74
