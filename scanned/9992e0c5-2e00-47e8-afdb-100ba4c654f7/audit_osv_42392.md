# [M] marimo < 0.23.15 API Key Exfiltration via Malicious Notebook PEP-723 Metadata

## Summary
Severity: Medium
Advisory: CVE-2026-67618
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-67618
Type: osv

## Details
marimo before 0.23.15 contains a configuration injection vulnerability that allows notebook authors to exfiltrate operator API keys by embedding a malicious base_url in PEP-723 inline script metadata, which is merged into session configuration with higher precedence than the operator's own settings due to insufficient sanitization in sanitize_pyproject_dict. When an operator opens the crafted notebook and makes an AI request, marimo resolves the attacker-controlled base_url from the notebook config while falling back to the operator's OPENAI_API_KEY environment variable for authentication, transmitting the API key to the attacker-controlled endpoint without requiring any cell execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67618.json
- https://github.com/marimo-team/marimo/releases/tag/0.23.15
- https://nvd.nist.gov/vuln/detail/CVE-2026-67618
- https://www.vulncheck.com/advisories/marimo-api-key-exfiltration-via-malicious-notebook-pep-723-metadata
- https://github.com/marimo-team/marimo/pull/10281
- https://github.com/marimo-team/marimo/commit/1a21bd71e258438d2511136b5edacc94c08855f4
- https://github.com/marimo-team/marimo
