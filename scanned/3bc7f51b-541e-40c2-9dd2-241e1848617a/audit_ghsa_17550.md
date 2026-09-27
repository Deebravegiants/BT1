# [C] BackendAI Missing Authentication for Critical Function

## Summary
Severity: Critical
Advisory: GHSA-ww28-4m4v-cq4j
CVE: CVE-2025-49652
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-09
Source: https://github.com/advisories/GHSA-ww28-4m4v-cq4j
Type: github-advisory

## Affected
- PyPI: `backend.ai` — affected >=0 <25.15.6
- PyPI: `backend.ai` — affected >=25.16.0rc1 <25.19.0rc1

## Details
Missing Authentication in the registration feature of Lablup's BackendAI allows arbitrary users to create user accounts that can access private data even when registration is disabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-49652
- https://github.com/lablup/backend.ai/commit/37fc8f70f9bad2dd01fe2e288f9006e96f9914ed
- https://github.com/lablup/backend.ai/commit/b6d3ddd9e285a7ce59722a37585b9298681eb82f
- https://github.com/lablup/backend.ai/commit/d7704f506e319acff205d91bfca6e2ca92939983
- https://github.com/lablup/backend.ai
- https://hiddenlayer.com/sai_security_advisor/2025-05-backendai-49653
- https://hiddenlayer.com/sai_security_advisor/2025-06-backendai
