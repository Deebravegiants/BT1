# [H] hoppscotch: Unauthenticated Onboarding Config Disclosure via Empty Recovery Token

## Summary
Severity: High
Advisory: CVE-2026-44478
Aliases: GHSA-7c8p-hj4p-3q3f
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-44478
Type: osv

## Details
hoppscotch is an open source API development ecosystem. The fix for CVE-2026-28215 in version 2026.2.0 addresses the unauthenticated POST /v1/onboarding/config endpoint by checking onboardingCompleted and canReRunOnboarding before allowing config overwrites. However, GET /v1/onboarding/config still leaks all infrastructure secrets in plaintext to unauthenticated users when the ONBOARDING_RECOVERY_TOKEN stored in the database is an empty string. This vulnerability is fixed in 2026.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44478.json
- https://github.com/hoppscotch/hoppscotch/security/advisories/GHSA-7c8p-hj4p-3q3f
- https://nvd.nist.gov/vuln/detail/CVE-2026-44478
