# [H] Backend.AI Missing Authorization vulnerability

## Summary
Severity: High
Advisory: GHSA-h889-475r-wfmm
CVE: CVE-2025-49651
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-09
Source: https://github.com/advisories/GHSA-h889-475r-wfmm
Type: github-advisory

## Affected
- PyPI: `backend.ai` — affected >=0

## Details
Missing Authorization in Lablup's BackendAI allows attackers to takeover all active sessions; Accessing, stealing, or altering any data accessible in the session. This vulnerability exists in all current versions of BackendAI.

NOTE: The maintainers of BackendAI do not consider this report to fit with their threat model and advise users to follow security advice from https://github.com/lablup/backend.ai/pull/7587 in their instances to protect themselves from the conditions that would lead to the situation described in the CVE record.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-49651
- https://github.com/lablup/backend.ai/pull/7587
- https://github.com/lablup/backend.ai
- https://hiddenlayer.com/sai_security_advisor/2025-05-backendai-49653
- https://hiddenlayer.com/sai_security_advisor/2025-06-backendai
