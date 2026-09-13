# [H] Sentry vulnerable to leaking superuser cleartext password in logs

## Summary
Severity: High
Advisory: GHSA-6cjm-4pxw-7xp9
CVE: CVE-2024-32474
CWE: CWE-117, CWE-312
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-04-18
Source: https://github.com/advisories/GHSA-6cjm-4pxw-7xp9
Type: github-advisory

## Affected
- PyPI: `sentry` — affected >=24.3.0 <24.4.1

## Details
### Impact
When authenticating as a superuser to a self-hosted Sentry instance with a username and password, the password is leaked as cleartext in logs under the _event_: `auth-index.validate_superuser`. An attacker with access to the log data could use these leaked credentials to login to the Sentry system as superuser.

### Patches
- Self-hosted users on affected versions should upgrade to 24.4.1 or later.
- Sentry SaaS users do not need to take any action. This vulnerability is not applicable to SaaS.

### Workarounds
Users can configure the logging level to exclude logs of the `INFO` level and only generate logs for levels at `WARNING` or higher. For details on configuring self-hosted Sentry's logging level see our documentation at: https://develop.sentry.dev/config/#logging

### References
- Bug introduced in https://github.com/getsentry/sentry/pull/66393
- Security fix in https://github.com/getsentry/sentry/pull/69148

## References
- https://github.com/getsentry/sentry/security/advisories/GHSA-6cjm-4pxw-7xp9
- https://nvd.nist.gov/vuln/detail/CVE-2024-32474
- https://github.com/getsentry/sentry/pull/66393
- https://github.com/getsentry/sentry/pull/69148
- https://github.com/getsentry/sentry/commit/d5b34568d9f1c41362ccb62141532a0a2169512f
- https://github.com/getsentry/sentry
