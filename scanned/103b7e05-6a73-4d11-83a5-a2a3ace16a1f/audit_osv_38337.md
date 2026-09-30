# [M] CVE-2026-39103

## Summary
Severity: Medium
Advisory: CVE-2026-39103
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-39103
Type: osv

## Details
Buffer Overflow vulnerability in GPAC before commit v391dc7f4d234988ea0bc3cc294eb725eddf8f702 allows an attacker to cause a denial of service via the src/scenegraph/svg_attributes.c, svg_parse_strings(), gf_svg_parse_attribute()

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39103.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-39103
- https://github.com/gpac/gpac/issues/3506
- https://github.com/gpac/gpac/commit/391dc7f4d234988ea0bc3cc294eb725eddf8f702
