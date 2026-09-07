# [M] Subrion CMS Cross-site scripting in search

## Summary
Severity: Medium
Advisory: GHSA-xjr9-2wf2-3v4w
CVE: CVE-2014-9120
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xjr9-2wf2-3v4w
Type: github-advisory

## Affected
- Packagist: `intelliants/subrion` — affected >=0 <3.2.3

## Details
A cross-site scripting (XSS) vulnerability in Subrion CMS before 3.2.3 allows remote attackers to inject arbitrary web script or HTML via the `PATH_INFO` to `subrion/search/`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9120
- https://www.netsparker.com/xss-vulnerability-in-subrion-cms
- http://dev.subrion.org/versions/130
