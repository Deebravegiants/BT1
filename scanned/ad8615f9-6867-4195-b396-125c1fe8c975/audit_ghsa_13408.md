# [M] Sentry CORS misconfiguration

## Summary
Severity: Medium
Advisory: GHSA-4xqm-4p72-87h6
CVE: CVE-2023-36829
CWE: CWE-697, CWE-863, CWE-942
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-4xqm-4p72-87h6
Type: github-advisory

## Affected
- PyPI: `sentry` — affected >=23.6.0 <23.6.2

## Details
### Impact
The Sentry API incorrectly returns the `access-control-allow-credentials: true` HTTP header if the `Origin` request header ends with the `system.base-hostname` option of Sentry installation. This only affects installations that have `system.base-hostname` option explicitly set, as it is empty by default.

Impact is limited since recent versions of major browsers have cross-site cookie blocking enabled by default. However, this flaw could allow other multi-step attacks.

### Patches
The patch has been released in [Sentry 23.6.2](https://github.com/getsentry/self-hosted/releases/tag/23.6.2).

### Workarounds

For Sentry SaaS customers, no action is needed.

For self-hosted Sentry installations that have `system.base-hostname` explicitly set, it is recommended to upgrade the installation to 23.6.2 or higher. There are no known workarounds.

### References
- [getsentry/sentry PR #52276](https://github.com/getsentry/sentry/pull/52276)

### Credits
- [@andr0idp4r4n0id](https://twitter.com/andr0idp4r4n0id)

## References
- https://github.com/getsentry/sentry/security/advisories/GHSA-4xqm-4p72-87h6
- https://nvd.nist.gov/vuln/detail/CVE-2023-36829
- https://github.com/getsentry/sentry/pull/52276
- https://github.com/getsentry/sentry/commit/19248fb9802c252665b802aeab02fdc65ed47dc9
- https://github.com/getsentry/sentry/commit/ee44c6be35e5e464bc40637580f39867898acd8b
- https://github.com/getsentry/self-hosted/releases/tag/23.6.2
- https://github.com/getsentry/sentry
- https://github.com/pypa/advisory-database/tree/main/vulns/sentry/PYSEC-2023-115.yaml
