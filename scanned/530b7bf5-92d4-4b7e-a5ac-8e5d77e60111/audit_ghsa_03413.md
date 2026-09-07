# [M] Cross-site scripting in SiCKRAGE

## Summary
Severity: Medium
Advisory: GHSA-rmp7-f2vp-3rq4
CVE: CVE-2021-25925
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-20
Source: https://github.com/advisories/GHSA-rmp7-f2vp-3rq4
Type: github-advisory

## Affected
- PyPI: `sickrage` — affected >=4.2.0 <10.0.11.dev2

## Details
in SiCKRAGE, versions 4.2.0 to 10.0.11.dev1 are vulnerable to Stored Cross-Site-Scripting (XSS) due to user input not being validated properly when processed by the server. Therefore, an attacker can inject arbitrary JavaScript code inside the application, and possibly steal a user’s sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25925
- https://github.com/SiCKRAGE/SiCKRAGE/commit/9f42426727e16609ad3d1337f6637588b8ed28e4
- https://github.com/SiCKRAGE/SiCKRAGE
- https://github.com/pypa/advisory-database/tree/main/vulns/sickrage/PYSEC-2021-147.yaml
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25925
