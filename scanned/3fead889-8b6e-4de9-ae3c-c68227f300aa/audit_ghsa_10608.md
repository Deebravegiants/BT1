# [M] Weblate Doesn't Invalidate API Token on Password Change

## Summary
Severity: Medium
Advisory: GHSA-6j8j-4qp3-36p2
CVE: CVE-2026-41519
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-6j8j-4qp3-36p2
Type: github-advisory

## Affected
- PyPI: `weblate` — affected >=0 <5.17.1

## Details
### Impact
When a user changes their password, browser sessions are correctly invalidated via `cycle_session_keys()`, but DRF API tokens (`wlu_*` prefix) stored in `authtoken_token` are not revoked.

### Patches
* https://github.com/WeblateOrg/weblate/pull/19057

### Resources
Weblate thanks Sang Yu Jeon for reporting this via GitHub.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-6j8j-4qp3-36p2
- https://nvd.nist.gov/vuln/detail/CVE-2026-41519
- https://github.com/WeblateOrg/weblate/pull/19057
- https://github.com/WeblateOrg/weblate/commit/649a2da81700542f95c0807b3c625fc3bb0eaf95
- https://github.com/WeblateOrg/weblate
- https://github.com/WeblateOrg/weblate/releases/tag/weblate-5.17.1
