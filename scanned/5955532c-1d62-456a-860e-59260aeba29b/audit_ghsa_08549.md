# [H] Docling's JATS XML backend is vulnerable to XML Entity Expansion (XXE) attacks

## Summary
Severity: High
Advisory: GHSA-cr42-rg2m-mq4q
CVE: CVE-2026-31247
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-cr42-rg2m-mq4q
Type: github-advisory

## Affected
- PyPI: `docling` — affected >=0

## Details
Docling's JATS XML backend is vulnerable to XML Entity Expansion (XXE) attacks thru 2.61.0. The backend uses etree.parse() to parse XML files without disabling entity resolution. An attacker can craft a malicious XML file containing a nested entity expansion payload (XML Bomb). When processed by Docling, the exponential expansion of entities leads to excessive resource consumption, resulting in a denial of service (DoS) condition on the system running the Docling parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31247
- https://github.com/docling-project/docling
- https://www.notion.so/CVE-2026-31247-35d1e1393188818fa654c116c6a470bb
