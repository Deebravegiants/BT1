# [C] CVE-2024-45508

## Summary
Severity: Critical
Advisory: CVE-2024-45508
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-01
Source: https://osv.dev/vulnerability/CVE-2024-45508
Type: osv

## Details
HTMLDOC before 1.9.19 has an out-of-bounds write in parse_paragraph in ps-pdf.cxx because of an attempt to strip leading whitespace from a whitespace-only node.

## References
- https://github.com/michaelrsweet/htmldoc/blob/2d5b2ab9ddbf2aee2209010cebc11efdd1cab6e2/CHANGES.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45508.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45508
- https://github.com/michaelrsweet/htmldoc/issues/528
- https://github.com/michaelrsweet/htmldoc/commit/2d5b2ab9ddbf2aee2209010cebc11efdd1cab6e2
