# [M] XML External Entities Vulnerability in CVRF-CSAF-Converter

## Summary
Severity: Medium
Advisory: GHSA-m8gq-83gh-v42v
CVE: CVE-2022-27193
CWE: CWE-552, CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-m8gq-83gh-v42v
Type: github-advisory

## Affected
- PyPI: `cvrf2csaf` — affected >=0 <1.0.0rc2

## Details
CVRF-CSAF-Converter before 1.0.0-rc2 resolves XML External Entities (XXE). This leads to the inclusion of arbitrary (local) file content into the generated output document. An attacker can exploit this to disclose information from the system running the converter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27193
- https://github.com/csaf-tools/CVRF-CSAF-Converter
- https://github.com/csaf-tools/CVRF-CSAF-Converter/releases/tag/1.0.0-rc2
