# [M] Expat Out-of-Bounds Read via dtdCopy

## Summary
Severity: Medium
Advisory: CVE-2026-76641
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-76641
Type: osv

## Details
Expat through 2.8.3 contains an out-of-bounds read vulnerability that allows attackers to trigger memory corruption by processing XML with external entity parsers created via XML_ExternalEntityParserCreate. A struct size mismatch between ELEMENT_TYPE members causes storeAtts to read the attIndex member past allocated memory boundaries, resulting in failure to normalize whitespace in non-CDATA attributes or a wild pointer dereference causing a segfault. This vulnerability was introduced by the fix for CVE-2026-66046.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76641.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-76641
- https://www.vulncheck.com/advisories/expat-out-of-bounds-read-via-dtdcopy
- https://github.com/libexpat/libexpat/pull/1331
- https://github.com/libexpat/libexpat/commit/98599f6dcc2b460410881fe420f5f55d6bec63bf
- https://github.com/libexpat/libexpat
