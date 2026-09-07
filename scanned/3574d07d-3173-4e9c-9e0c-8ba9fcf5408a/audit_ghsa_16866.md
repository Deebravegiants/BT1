# [M] Summernote vulnerable to cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-4wh3-3wf2-39m9
CVE: CVE-2024-29504
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-04-11
Source: https://github.com/advisories/GHSA-4wh3-3wf2-39m9
Type: github-advisory

## Affected
- npm: `summernote` — affected >=0

## Details
Cross Site Scripting vulnerability in Summernote v.0.8.18 and before allows a remote attacker to execute arbtirary code via a crafted payload to the `codeview` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29504
- https://github.com/summernote/summernote/pull/3782
- https://gist.github.com/phoenix118go/a9192281efcfa518daa709ab7638712b
- https://github.com/summernote/summernote
