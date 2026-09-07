# [M] CI4MS has a Deactivated User Session Bypass (active=0)

## Summary
Severity: Medium
Advisory: GHSA-5hfv-c864-qcq9
CVE: CVE-2026-41891
CWE: CWE-613
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-5hfv-c864-qcq9
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0.26.0 <0.31.8.0

## Details
### Summary
The auth filter has the deactivated/banned user check commented out. 

### Details
CodeIgniter Shield's `loggedIn()` re-checks the `status` field (catching `status='banned'`), but does **not** re-check the `active` field for existing sessions. When an admin deactivates a user (`active=0`) after they have already logged in:
- Their session cookie remains valid
- `auth()->loggedIn()` still returns `true`
- The commented-out code is the only mechanism that would have checked `!$user->active`

### Evidence
<img width="981" height="654" alt="image" src="https://github.com/user-attachments/assets/6f75d144-5bcf-4a3f-bc35-bb0715c3ed05" />


### Impact
- User deactivation does NOT immediately revoke backend access
- Deactivated user retains full access until session expires (default: 7200s)

### Additional note
The commented-out block appears to be a deferred placeholder — it was written but disabled from the very first commit that introduced the filter, and has never been active. The later addition of SessionTracker (v0.31.4.0) suggests the dev was aware of the session revocation gap, but account-level deactivation (users.active = 0) remains unenforced. Could you verify if this is intentionally pending or simply forgotten and not documented?.

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-5hfv-c864-qcq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-41891
- https://github.com/ci4-cms-erp/ci4ms/commit/2f38284281ce6b435ea42003951f14109ac2cea7
- https://github.com/ci4-cms-erp/ci4ms
- https://github.com/ci4-cms-erp/ci4ms/releases/tag/0.31.8.0
