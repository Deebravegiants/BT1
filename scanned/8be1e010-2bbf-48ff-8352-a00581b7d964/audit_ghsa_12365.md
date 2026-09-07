# [M] Alkacon OpenCMS XSS via Mercury template

## Summary
Severity: Medium
Advisory: GHSA-w62v-q77r-66cc
CVE: CVE-2023-6379
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-w62v-q77r-66cc
Type: github-advisory

## Affected
- Maven: `org.opencms:opencms-core` — affected >=14.0.0 <16.0.0

## Details
Cross-site scripting (XSS) vulnerability in Alkacon Software Open CMS, affecting versions 14 and 15 of the 'Mercury' template. This vulnerability could allow a remote attacker to send a specially crafted JavaScript payload to a victim and partially take control of their browsing session.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6379
- https://github.com/alkacon/opencms-core/commit/d965c18ac6d24ad75bfea272edb8b2efd4290afa
- https://github.com/alkacon/opencms-core
- https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-alkacon-software-opencms
