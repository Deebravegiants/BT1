# [H] OctoPrint Incorrect Access Control

## Summary
Severity: High
Advisory: GHSA-x9rq-fjp5-qgm9
CVE: CVE-2021-32560
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x9rq-fjp5-qgm9
Type: github-advisory

## Affected
- PyPI: `OctoPrint` — affected >=0 <1.6.0

## Details
The Logging subsystem in OctoPrint before 1.6.0 has incorrect access control because it attempts to manage files that are not `*.log` files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32560
- https://github.com/OctoPrint/OctoPrint
- https://github.com/OctoPrint/OctoPrint/releases/tag/1.6.0
- https://github.com/pypa/advisory-database/tree/main/vulns/octoprint/PYSEC-2021-29.yaml
- https://octoprint.org/blog/2021/04/27/new-release-1.6.0
- https://www.brzozowski.io
- https://www.brzozowski.io/web-applications/2021/05/11/the-insecure-story-of-octoprint.html
