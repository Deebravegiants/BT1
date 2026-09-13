# [M] Snipe-IT Vulnerable to Privilege Escalation for self via API Permissions Assignment

## Summary
Severity: Medium
Advisory: GHSA-52fw-7fw2-fmv5
CVE: CVE-2026-48493
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-52fw-7fw2-fmv5
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.0

## Details
### Impact
A user with only users.edit AND api permissions can send a PATCH to /api/v1/users/{their_own_id} and grant themselves any permission except admin and superuser — for example `assets.view`, `assets.create`, `reports.view`, import, etc.

### Patches
Patched in https://github.com/grokability/snipe-it/pull/19024

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-52fw-7fw2-fmv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-48493
- https://github.com/grokability/snipe-it/pull/19024
- https://github.com/grokability/snipe-it
