# [M] Quivr Prompt Endpoints Missing Ownership Validation

## Summary
Severity: Medium
Advisory: CVE-2026-82280
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82280
Type: osv

## Details
Quivr through 0.0.322 fails to validate ownership in prompt endpoints, allowing authenticated users to modify any prompt by identifier. Attackers with read-only access to shared brains can read exposed prompt identifiers and overwrite system prompts affecting all brain users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82280.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82280
- https://www.vulncheck.com/advisories/quivr-prompt-endpoints-missing-ownership-validation
- https://github.com/QuivrHQ/quivr/issues/3698
- https://github.com/QuivrHQ/quivr
- https://github.com/QuivrHQ/quivr/blob/v0.0.322/backend/api/quivr_api/modules/prompt/controller/prompt_routes.py
- https://github.com/The-Vibe-Company/Quivr/issues/3698
