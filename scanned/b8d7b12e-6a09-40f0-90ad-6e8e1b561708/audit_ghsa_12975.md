# [H] Privilege escalation via ApiTokensEndpoint

## Summary
Severity: High
Advisory: GHSA-9jcq-jf57-c62c
CVE: CVE-2023-39349
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-08-08
Source: https://github.com/advisories/GHSA-9jcq-jf57-c62c
Type: github-advisory

## Affected
- PyPI: `sentry` — affected >=22.1.0 <23.7.2

## Details
### Impact
An attacker with access to a token with few or no scopes can query `/api/0/api-tokens/` for a list of all tokens created by a user, including tokens with greater scopes, and use those tokens in other requests.

There is no evidence that the issue was exploited on https://sentry.io. For self-hosted users, it is advised to rotate user auth tokens via `https://your-self-hosted-sentry-installation/settings/account/api/auth-tokens/`.

### Patches
The issue was fixed in https://github.com/getsentry/sentry/pull/53850 and is available in the release 23.7.2 of [sentry](https://github.com/getsentry/sentry/releases/tag/23.7.2) and [self-hosted](https://github.com/getsentry/self-hosted/releases/tag/23.7.2).

### Workarounds
There are no known workarounds.

## References
- https://github.com/getsentry/sentry/security/advisories/GHSA-9jcq-jf57-c62c
- https://nvd.nist.gov/vuln/detail/CVE-2023-39349
- https://github.com/getsentry/sentry/pull/53850
- https://github.com/getsentry/sentry/commit/fad12c1150d1135edf9666ea72ca11bc110c1083
- https://github.com/getsentry/self-hosted/releases/tag/23.7.2
- https://github.com/getsentry/sentry
- https://github.com/getsentry/sentry/releases/tag/23.7.2
