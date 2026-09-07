# [M] Open redirect in Tornado

## Summary
Severity: Medium
Advisory: GHSA-hj3f-6gcp-jg8j
CVE: CVE-2023-28370
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-25
Source: https://github.com/advisories/GHSA-hj3f-6gcp-jg8j
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <6.3.2

## Details
Open redirect vulnerability in Tornado versions 6.3.1 and earlier allows a remote unauthenticated attacker to redirect a user to an arbitrary web site and conduct a phishing attack by having user access a specially crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28370
- https://github.com/tornadoweb/tornado/commit/32ad07c54e607839273b4e1819c347f5c8976b2f
- https://github.com/pypa/advisory-database/tree/main/vulns/tornado/PYSEC-2023-75.yaml
- https://github.com/tornadoweb/tornado
- https://github.com/tornadoweb/tornado/releases/tag/v6.3.2
- https://jvn.jp/en/jp/JVN45127776
- https://lists.debian.org/debian-lts-announce/2025/01/msg00000.html
