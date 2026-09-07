# [M] Pandao Editor.md vulnerable to cross-site scripting (XSS) in iframe src parameter

## Summary
Severity: Medium
Advisory: GHSA-w974-rq9x-mh3v
CVE: CVE-2020-19697
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-04
Source: https://github.com/advisories/GHSA-w974-rq9x-mh3v
Type: github-advisory

## Affected
- npm: `editor.md` — affected >=0

## Details
Cross-site Scripting vulnerability found in Pandao Editor.md v.1.5.0 allows a remote attacker to execute arbitrary code via a crafted script in the `<iframe> src` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-19697
- https://github.com/pandao/editor.md/issues/701
- https://github.com/pandao/editor.md/pull/860
- https://github.com/pandao/editor.md
