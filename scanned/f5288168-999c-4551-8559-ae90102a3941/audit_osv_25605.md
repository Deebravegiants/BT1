# [M] Potential segfault due to NULL pointer dereference in libvips

## Summary
Severity: Medium
Advisory: CVE-2023-40032
Aliases: GHSA-33qp-9pq7-9584
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-11
Source: https://osv.dev/vulnerability/CVE-2023-40032
Type: osv

## Details
libvips is a demand-driven, horizontally threaded image processing library. A specially crafted SVG input can cause libvips versions 8.14.3 or earlier to segfault when attempting to parse a malformed UTF-8 character. Users should upgrade to libvips version 8.14.4 (or later) when processing untrusted input.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YU2FFC47X2XDEGEHEWAGLU5L3R6FEYD2/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40032.json
- https://github.com/libvips/libvips/security/advisories/GHSA-33qp-9pq7-9584
- https://nvd.nist.gov/vuln/detail/CVE-2023-40032
- https://github.com/libvips/libvips/commit/e091d65835966ef56d53a4105a7362cafdb1582b
- https://github.com/libvips/libvips/pull/3604
