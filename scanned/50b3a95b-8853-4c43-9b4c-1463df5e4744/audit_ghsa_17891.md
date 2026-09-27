# [H] XGrammar affected by Denial of Service by infinite recursion grammars

## Summary
Severity: High
Advisory: GHSA-5cmr-4px5-23pc
CVE: CVE-2025-57809
CWE: CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-08-25
Source: https://github.com/advisories/GHSA-5cmr-4px5-23pc
Type: github-advisory

## Affected
- PyPI: `xgrammar` — affected >=0 <0.1.21

## Details
### Summary
This issue: http://github.com/mlc-ai/xgrammar/issues/250 should have it's own security advisory. Since several tools accept and pass user supplied grammars to xgrammar, and it is so easy to trigger it seems like a High.

## References
- https://github.com/mlc-ai/xgrammar/security/advisories/GHSA-5cmr-4px5-23pc
- https://nvd.nist.gov/vuln/detail/CVE-2025-57809
- https://github.com/mlc-ai/xgrammar/issues/250
- https://github.com/mlc-ai/xgrammar/commit/b943feacb5a1caf4d39de8ec3bf7c7ce066dcee5
- https://github.com/mlc-ai/xgrammar
