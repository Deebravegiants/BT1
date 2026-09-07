# [M] Inventree vulnerable to Stored Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-62g7-fpv9-v95f
CVE: CVE-2022-3355
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-30
Source: https://github.com/advisories/GHSA-62g7-fpv9-v95f
Type: github-advisory

## Affected
- PyPI: `inventree` — affected >=0 <0.8.3

## Details
Inventree prior to 0.8.3 is vulnerable to stored cross-site scripting by uploading SVG files. Version 0.8.3 contains a patch for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3355
- https://github.com/inventree/inventree/commit/5a08ef908dd5344b4433436a4679d122f7f99e41
- https://github.com/inventree/InvenTree/releases/tag/0.8.3
- https://github.com/inventree/inventree
- https://huntr.dev/bounties/4b7fb92c-f06b-4bbf-82dc-9f013b30b6a6
