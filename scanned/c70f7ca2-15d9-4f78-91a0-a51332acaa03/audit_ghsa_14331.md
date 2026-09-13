# [M] pretalx allows path traversal in HTML export

## Summary
Severity: Medium
Advisory: GHSA-23fx-92m6-4f2g
CVE: CVE-2023-28458
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-23fx-92m6-4f2g
Type: github-advisory

## Affected
- PyPI: `pretalx` — affected >=2.3.1 <2.3.2

## Details
pretalx 2.3.1 before 2.3.2 allows path traversal in HTML export (a non-default feature). Organizers can trigger the overwriting (with the standard pretalx 404 page content) of an arbitrary file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28458
- https://github.com/pretalx/pretalx/commit/60722c43cf975f319e94102e6bff320723776890
- https://github.com/pretalx/pretalx
- https://github.com/pretalx/pretalx/releases/tag/v2.3.2
- https://github.com/pypa/advisory-database/tree/main/vulns/pretalx/PYSEC-2023-40.yaml
- https://pretalx.com/p/news/security-release-232
- https://www.sonarsource.com/blog/pretalx-vulnerabilities-how-to-get-accepted-at-every-conference
