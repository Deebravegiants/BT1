# [H] Sentry's Astro SDK vulnerable to ReDoS

## Summary
Severity: High
Advisory: GHSA-x3v3-8xg8-8v72
CVE: CVE-2023-50249
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-18
Source: https://github.com/advisories/GHSA-x3v3-8xg8-8v72
Type: github-advisory

## Affected
- npm: `@sentry/astro` — affected >=7.78.0 <7.87.0

## Details
### Impact
A ReDoS (Regular expression Denial of Service) vulnerability has been identified in Sentry's Astro SDK 7.78.0-7.86.0. Under certain conditions, this vulnerability allows an attacker to cause excessive computation times on the server, leading to denial of service (DoS).

Applications that are using Sentry's Astro SDK are affected if:

1. They're using Sentry instrumentation:
   - they have [manually registered](https://docs.sentry.io/platforms/javascript/guides/astro/manual-setup/#manually-add-server-instrumentation) Sentry Middleware (affected versions 7.78.0-7.86.0);
   - or [configured](https://docs.sentry.io/platforms/javascript/guides/astro/manual-setup/#configure-server-instrumentation) Astro in SSR (server) or hybrid mode, use Astro 3.5.0 and newer and didn’t [disable the automatic server instrumentation](https://docs.sentry.io/platforms/javascript/guides/astro/manual-setup/#disable-auto-server-instrumentation) (affected versions 7.82.0-7.86.0).
2. They have configured routes with at least two path params (e.g. `/foo/[p1]/bar/[p2]`).

### Patches
The problem has been patched in [@sentry/astro@7.87.0](https://www.npmjs.com/package/@sentry/astro/v/7.87.0).
The corresponding PR: https://github.com/getsentry/sentry-javascript/pull/9815

### Workarounds
We strongly recommend upgrading to the latest SDK version. However, if it's not possible, the steps to mitigate the vulnerability without upgrade are:
* [disable auto instrumentation](https://docs.sentry.io/platforms/javascript/guides/astro/manual-setup/#disable-auto-server-instrumentation) if you're using Astro 3.5.0 or newer
* and remove the manually added Sentry middleware (if it was [added](https://docs.sentry.io/platforms/javascript/guides/astro/manual-setup/#manually-add-server-instrumentation) before).

After these changes, Sentry error reporting will still be functional, but some details such as server-side transactions (and consequently, distributed traces between client and server) will be omitted. We therefore still recommend to update to 7.87.0 as soon as you can. 

### References
* [Sentry docs: Manual Setup for Astro](https://docs.sentry.io/platforms/javascript/guides/astro/manual-setup/)
* [Release notes: sentry-javascript 7.87.0](https://github.com/getsentry/sentry-javascript/releases/tag/7.87.0)
* [npm: @sentry/astro@7.87.0](https://www.npmjs.com/package/@sentry/astro/v/7.87.0)

## References
- https://github.com/getsentry/sentry-javascript/security/advisories/GHSA-x3v3-8xg8-8v72
- https://nvd.nist.gov/vuln/detail/CVE-2023-50249
- https://github.com/getsentry/sentry-javascript/pull/9815
- https://github.com/getsentry/sentry-javascript/commit/fe24eb5eefa9d27b14b2b6f9ebd1debca1c208fb
- https://docs.sentry.io/platforms/javascript/guides/astro/manual-setup/#disable-auto-server-instrumentation
- https://github.com/getsentry/sentry-javascript
- https://www.npmjs.com/package/@sentry/astro/v/7.87.0
