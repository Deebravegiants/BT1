# [H] BackendAI vulnerable to Exposure of Sensitive Information to an Unauthorized Actor

## Summary
Severity: High
Advisory: GHSA-hxvr-gg2w-j48x
CVE: CVE-2025-49653
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-09
Source: https://github.com/advisories/GHSA-hxvr-gg2w-j48x
Type: github-advisory

## Affected
- PyPI: `backend.ai` — affected >=0

## Details
Exposure of sensitive data in active sessions in Lablup's BackendAI allows attackers to retrieve credentials for users on the management platform.

NOTE: The maintainers of BackendAI do not consider this report to fit with their threat model and advise users to follow security advice from https://github.com/lablup/backend.ai/pull/7587 in their instances to protect themselves from the conditions that would lead to the situation described in the CVE record.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-49653
- https://github.com/lablup/backend.ai/pull/7587
- https://github.com/lablup/backend.ai
- https://hiddenlayer.com/sai_security_advisor/2025-05-backendai-49653
- https://hiddenlayer.com/sai_security_advisor/2025-06-backendai
