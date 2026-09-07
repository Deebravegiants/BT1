# [M] Open WebUI Stored Cross-Site Scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5jp3-wp5v-5363
CVE: CVE-2024-6706
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-08
Source: https://github.com/advisories/GHSA-5jp3-wp5v-5363
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
Attackers can craft a malicious prompt that coerces the language model into executing arbitrary JavaScript in the context of the web page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6706
- https://github.com/open-webui/open-webui
- https://korelogic.com/Resources/Advisories/KL-001-2024-005.txt
