# [H] Sentry vulnerable to stored Cross-Site Scripting (XSS)

## Summary
Severity: High
Advisory: GHSA-fm88-hc3v-3www
CVE: CVE-2024-41656
CWE: CWE-79, CWE-80
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-23
Source: https://github.com/advisories/GHSA-fm88-hc3v-3www
Type: github-advisory

## Affected
- PyPI: `sentry` — affected >=10.0.0 <24.7.1

## Details
### Impact
An unsanitized payload sent by an Integration platform integration allows the storage of arbitrary HTML tags on the Sentry side. This payload could subsequently be rendered on the Issues page, creating a Stored Cross-Site Scripting (XSS) vulnerability. This vulnerability might lead to the execution of arbitrary scripts in the context of a user’s browser.

Self-hosted Sentry users may be impacted if untrustworthy Integration platform integrations send external issues to their Sentry instance.

### Patches
The patch has been released in [Sentry 24.7.1](https://github.com/getsentry/self-hosted/releases/tag/24.7.1)

### Workarounds
For Sentry SaaS customers, no action is needed. This has been patched on July 22, and even prior to the fix, the exploitation was not possible due to the strict Content Security Policy deployed on sentry.io site.

For self-hosted users, we strongly recommend upgrading Sentry to the latest version. If it is not possible, you could [enable CSP on your self-hosted installation](https://develop.sentry.dev/self-hosted/csp/) with `CSP_REPORT_ONLY = False` (enforcing mode). This will mitigate the risk of XSS.

### References
* Sentry Docs: [Integration platform / Create an External Issue](https://docs.sentry.io/api/integration/create-an-external-issue/)
* Sentry Docs: [Self-hosted CSP](https://develop.sentry.dev/self-hosted/csp/)
* The fix: https://github.com/getsentry/sentry/pull/74648
* PortSwigger: [Stored XSS](https://portswigger.net/web-security/cross-site-scripting/stored)

## References
- https://github.com/getsentry/sentry/security/advisories/GHSA-fm88-hc3v-3www
- https://nvd.nist.gov/vuln/detail/CVE-2024-41656
- https://github.com/getsentry/sentry/pull/74648
- https://github.com/getsentry/sentry/commit/5c679521f1539eabfb81287bfc30f34dbecd373e
- https://github.com/getsentry/self-hosted/releases/tag/24.7.1
- https://github.com/getsentry/sentry
