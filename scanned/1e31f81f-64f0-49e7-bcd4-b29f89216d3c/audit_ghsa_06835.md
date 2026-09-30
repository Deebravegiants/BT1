# [M] Apollo Portal: There is a risk of unauthorized access to the Apollo configuration center

## Summary
Severity: Medium
Advisory: GHSA-jxpj-9j24-w337
CVE: CVE-2025-32781
CWE: CWE-639, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-jxpj-9j24-w337
Type: github-advisory

## Affected
- Maven: `com.ctrip.framework.apollo:apollo` — affected >=0

## Details
### Summary

Apollo Portal versions before 2.5.0 do not verify application and namespace permissions when an authenticated user requests a release by ID through `GET /envs/{env}/releases/{releaseId}`.

When `configView.memberOnly.envs` is enabled for the requested environment, a low-privileged Portal user can supply a valid release ID belonging to an application or namespace they are not authorized to view. The endpoint returns the release data without calling `UserPermissionValidator.shouldHideConfigToCurrentUser(...)`.

### Impact

An authenticated attacker who obtains or guesses a valid release ID can read configuration data from other applications and namespaces. Exposed configuration may contain sensitive values such as credentials or service endpoints. The issue does not allow configuration modification and does not directly affect availability.

### Affected versions

Apollo Portal versions earlier than 2.5.0 are affected when `configView.memberOnly.envs` is enabled.

### Patches

The issue is fixed in Apollo 2.5.0. The fix adds the missing application and namespace permission check before returning release data.

- Fix: https://github.com/apolloconfig/apollo/pull/5378
- Fix commit: https://github.com/apolloconfig/apollo/commit/362735ded4f13b62f6ab9df135d7096066e8e291
- Patched release: https://github.com/apolloconfig/apollo/releases/tag/v2.5.0

### Workarounds

Upgrade to Apollo 2.5.0 or later. If an immediate upgrade is not possible, backport the permission check from [PR #5378](https://github.com/apolloconfig/apollo/pull/5378) and restrict Apollo Portal access to trusted users until the fix is deployed.

### Credits

Apollo Portal thanks [@lesignals](https://github.com/lesignals) for reporting this issue.

## References
- https://github.com/apolloconfig/apollo/security/advisories/GHSA-jxpj-9j24-w337
- https://nvd.nist.gov/vuln/detail/CVE-2025-32781
- https://github.com/apolloconfig/apollo/pull/5378
- https://github.com/apolloconfig/apollo/commit/362735ded4f13b62f6ab9df135d7096066e8e291
- https://github.com/apolloconfig/apollo
- https://github.com/apolloconfig/apollo/releases/tag/v2.5.0
