# [M] Sentry Next.js vulnerable to SSRF via Next.js SDK tunnel endpoint

## Summary
Severity: Medium
Advisory: GHSA-2rmr-xw8m-22q9
CVE: CVE-2023-46729
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-11-09
Source: https://github.com/advisories/GHSA-2rmr-xw8m-22q9
Type: github-advisory

## Affected
- npm: `@sentry/nextjs` — affected >=7.26.0 <7.77.0

## Details
### Impact
An unsanitized input of Next.js SDK tunnel endpoint allows sending HTTP requests to arbitrary URLs and reflecting the response back to the user. This could open door for other attack vectors:
* client-side vulnerabilities: XSS/CSRF in the context of the trusted domain;
* interaction with internal network;
* read cloud metadata endpoints (AWS, Azure, Google Cloud, etc.);
* local/remote port scan.

This issue only affects users who have [Next.js SDK tunneling feature](https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/#configure-tunneling-to-avoid-ad-blockers) enabled.

### Patches
The problem has been fixed in [sentry/nextjs@7.77.0](https://www.npmjs.com/package/@sentry/nextjs/v/7.77.0)

### Workarounds
Disable tunneling by removing the `tunnelRoute` option from Sentry Next.js SDK config — `next.config.js` or `next.config.mjs`.

### References
* [Sentry Next.js tunneling feature](https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/#configure-tunneling-to-avoid-ad-blockers)
* [The fix](https://github.com/getsentry/sentry-javascript/pull/9415)
* [More Information](https://blog.sentry.io/next-js-sdk-security-advisory-cve-2023-46729/)

### Credits
* [Praveen Kumar](https://hackerone.com/mr_x_strange)

## References
- https://github.com/getsentry/sentry-javascript/security/advisories/GHSA-2rmr-xw8m-22q9
- https://nvd.nist.gov/vuln/detail/CVE-2023-46729
- https://github.com/getsentry/sentry-javascript/pull/9415
- https://github.com/getsentry/sentry-javascript/commit/ddbda3c02c35aba8c5235e0cf07fc5bf656f81be
- https://blog.sentry.io/next-js-sdk-security-advisory-cve-2023-46729
- https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/#configure-tunneling-to-avoid-ad-blockers
- https://github.com/getsentry/sentry-javascript
- https://www.npmjs.com/package/@sentry/nextjs/v/7.77.0
