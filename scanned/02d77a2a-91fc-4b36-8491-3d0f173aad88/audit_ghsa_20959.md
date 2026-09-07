# [M] Markdown-Nice v1.8.22 vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-462r-wxvm-jvxh
CVE: CVE-2022-38639
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-10
Source: https://github.com/advisories/GHSA-462r-wxvm-jvxh
Type: github-advisory

## Affected
- npm: `markdown-nice` — affected >=0

## Details
A cross-site scripting (XSS) vulnerability in Markdown-Nice v1.8.22 allows attackers to execute arbitrary web scripts or HTML via a crafted payload injected into the Community Posting field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38639
- https://github.com/mdnice/markdown-nice/issues/327
- https://github.com/mdnice/markdown-nice
