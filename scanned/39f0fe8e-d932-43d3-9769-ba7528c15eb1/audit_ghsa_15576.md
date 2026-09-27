# [H] Sentry improperly authorizes deletion of user issue alert notifications

## Summary
Severity: High
Advisory: GHSA-54m3-95j9-v89j
CVE: CVE-2024-45605
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-54m3-95j9-v89j
Type: github-advisory

## Affected
- PyPI: `sentry` — affected >=23.9.0 <24.9.0

## Details
### Impact
An authenticated user may delete user issue alert notifications for arbitrary users given a known alert ID. 

### Patches
A patch was issued to ensure authorization checks are properly scoped on requests to delete user alert notifications.

Sentry SaaS users do not need to take any action. [Self-Hosted Sentry](https://github.com/getsentry/self-hosted) users should upgrade to version **24.9.0** or higher.

### References
- [Prevent muting user alerts](https://github.com/getsentry/sentry/pull/77093/)

## References
- https://github.com/getsentry/sentry/security/advisories/GHSA-54m3-95j9-v89j
- https://nvd.nist.gov/vuln/detail/CVE-2024-45605
- https://github.com/getsentry/sentry/pull/77093
- https://github.com/getsentry/sentry/commit/590258255bcb3a5fa4c56f21297b6c99131cfb9d
- https://github.com/getsentry/self-hosted
- https://github.com/getsentry/sentry
