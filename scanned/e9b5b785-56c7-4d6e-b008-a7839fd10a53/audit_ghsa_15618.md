# [H] Guardrails AI vulnerable to Improper Restriction of XML External Entity Reference

## Summary
Severity: High
Advisory: GHSA-f8hx-f4xw-c646
CVE: CVE-2024-6961
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-21
Source: https://github.com/advisories/GHSA-f8hx-f4xw-c646
Type: github-advisory

## Affected
- PyPI: `guardrails-ai` — affected >=0 <0.5.0

## Details
RAIL documents are an XML-based format invented by Guardrails AI to enforce formatting checks on LLM outputs. Guardrails users that consume RAIL documents from external sources are vulnerable to XXE, which may cause leakage of internal file data via the SYSTEM entity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6961
- https://github.com/guardrails-ai/guardrails/pull/922
- https://github.com/guardrails-ai/guardrails/commit/f3d806afee31e2e3f97af682d16c3c1bc0d3c380
- https://github.com/guardrails-ai/guardrails
- https://research.jfrog.com/vulnerabilities/guardrails-rail-xxe-jfsa-2024-001035519
