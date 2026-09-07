# [H] pretalx vulnerable to path traversal in HTML export

## Summary
Severity: High
Advisory: GHSA-wh3w-jcc7-mhmf
CVE: CVE-2023-28459
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-wh3w-jcc7-mhmf
Type: github-advisory

## Affected
- PyPI: `pretalx` — affected >=0 <2.3.2

## Details
pretalx before 2.3.2 allows path traversal in HTML export (a non-default feature). Users were able to upload crafted HTML documents that trigger the reading of arbitrary files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28459
- https://github.com/pretalx/pretalx/commit/60722c43cf975f319e94102e6bff320723776890
- https://github.com/pretalx/pretalx
- https://github.com/pretalx/pretalx/releases/tag/v2.3.2
- https://github.com/pypa/advisory-database/tree/main/vulns/pretalx/PYSEC-2023-41.yaml
- https://pretalx.com/p/news/security-release-232
- https://www.sonarsource.com/blog/pretalx-vulnerabilities-how-to-get-accepted-at-every-conference
