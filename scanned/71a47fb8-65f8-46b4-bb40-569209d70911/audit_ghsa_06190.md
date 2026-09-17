# [H] Snipe-IT: Tenant Isolation Bypass in FMCS Floater Mode

## Summary
Severity: High
Advisory: GHSA-c6w2-j4wq-mvwg
CVE: CVE-2026-55643
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-c6w2-j4wq-mvwg
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.3

## Details
### Impact
Due to inconsistent authorization checks, a company-scoped user can bypass tenant boundaries to read, mutate, and soft-delete users who do not belong to any company (company_id = null). While direct instance authorization (isCurrentUserHasAccess) correctly denies access to these out-of-scope users, multiple API endpoints and bulk action web routes fail to enforce this restriction, relying instead on class-level permissions or broad scoped queries.
Impact: 

A malicious user scoped to a specific company (e.g., Company A) can:

Data Leakage: Extract PII and assigned licenses of users outside their tenant via the API (/api/v1/users and `/api/v1/users/{id}/licenses)`.

Data Modification: Mutate out-of-scope user profiles (e.g., changing city, notes) via the /users/bulkeditsave web route.

Data Deletion & Asset Theft: Soft-delete out-of-scope users and transfer their assigned assets to themselves via the /users/merge web route.


### Patches
Patched in https://github.com/grokability/snipe-it/commit/fbe05a8df4742729a9b0756c016d45f48246cc7b,

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-c6w2-j4wq-mvwg
- https://nvd.nist.gov/vuln/detail/CVE-2026-55643
- https://github.com/grokability/snipe-it/commit/fbe05a8df4742729a9b0756c016d45f48246cc7b
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.3
