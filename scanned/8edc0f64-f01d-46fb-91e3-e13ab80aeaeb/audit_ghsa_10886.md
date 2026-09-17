# [H] Ray Dashboard is vulnerable to path traversal through its static file handling mechanism

## Summary
Severity: High
Advisory: GHSA-j3mh-qmjj-xp83
CVE: CVE-2026-32981
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-j3mh-qmjj-xp83
Type: github-advisory

## Affected
- PyPI: `ray` — affected >=0 <2.8.1

## Details
A path traversal vulnerability was identified in Ray Dashboard (default port 8265) in Ray versions prior to 2.8.1. Due to improper validation and sanitization of user-supplied paths in the static file handling mechanism, an attacker can use traversal sequences (e.g., ../) to access files outside the intended static directory, resulting in local file disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-32981
- https://github.com/pypa/advisory-database/tree/main/vulns/ray/PYSEC-2026-130.yaml
- https://github.com/ray-project/ray
- https://packetstorm.news/files/id/215801
- https://www.vulncheck.com/advisories/ray-dashboard-path-traversal-leading-to-local-file-disclosure
