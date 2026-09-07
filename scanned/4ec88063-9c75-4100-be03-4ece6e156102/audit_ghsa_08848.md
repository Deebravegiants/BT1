# [H] Inngest TypeScript SDK exposes environment variables via serve() handler on unhandled HTTP methods

## Summary
Severity: High
Advisory: GHSA-2jf5-6wwv-vhxx
CVE: CVE-2026-42047
CWE: CWE-200, CWE-497
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-2jf5-6wwv-vhxx
Type: github-advisory

## Affected
- npm: `inngest` — affected >=3.22.0 <3.54.0

## Details
# Summary

A vulnerability in the Inngest TypeScript SDK versions `3.22.0` through `3.53.1` allows unauthenticated remote attackers to exfiltrate environment variables from the host process via the `serve()` HTTP handler.

The `serve()` handler implements `GET`, `POST`, and `PUT` methods. Requests using `PATCH`, `OPTIONS`, or `DELETE` fall through to a generic handler that returns diagnostic information. A change introduced in `v3.22.0` caused this diagnostic response to include the contents of `process.env`, exposing any secrets, API keys, or credentials present in the environment.

# Who is affected

An application is vulnerable if **all** of the following are true:

- It uses `inngest` SDK version `>= 3.22.0, <= 3.53.1` (inclusive)
- Its `serve()` endpoint is reachable via `PATCH`, `OPTIONS`, or `DELETE` requests.

Please check your framework's implementation for the serve handler ([documentation](https://www.inngest.com/docs/learn/serving-inngest-functions)) to asses whether it handles these HTTP methods. Common vulnerable configurations include:

- Next.js Pages Router, which forwards all HTTP methods to the handler.
- Express via `app.use('/api/inngest', serve(...))`, which routes `PATCH` and `OPTIONS` to the handler by default.

The following are **not** affected:

- Next.js App Router handlers that explicitly export only `GET`, `POST`, and `PUT`.
- Applications using the `connect` worker method.
- SDK versions `< 3.22.0` and `>= 3.54.0`, including all `4.x` releases.

The vulnerability was responsibly disclosed by an Inngest user. At this time, there are no known reports of exploitation.

# Remediation

1. Upgrade to `inngest@3.54.0` or later. The fix is backwards compatible with the `3.x` release line. The `4.x` line is also unaffected.
2. Rotate any secrets that were presence in environment variables (`process.env`) within affected environments including Inngest signing keys and event keys
3. Search logs for any requests to your `serve` endpoints using the `PATCH`, `OPTIONS`, `DELETE` http methods to assess if any environment variables may have been exposed.

## Additional recommendations

Users on platforms with long-lived deployments (e.g. Vercel, Cloudflare Workers) should be aware that prior deployments remain reachable at their immutable URLs and may continue to expose the vulnerability even after a new deployment is promoted. For example, Vercel offers security features such as "[Deployment Protection](https://vercel.com/docs/deployment-protection#standard-protection)" and [the ability to delete older deployments](https://vercel.com/kb/guide/how-do-i-delete-an-individual-deployment) which can help immediately mitigate impact.

For additional security, users can also adjust firewall or proxy rules to only allow requests to their `serve` endpoint from Inngest IP addresses available here: http://inngest.com/ips-v4, http://inngest.com/ips-v6

### Workarounds

If upgrading is not immediately possible, restrict the `serve()` endpoint at the framework or reverse-proxy layer to accept only `GET`, `POST`, and `PUT`. The Inngest `serve()` endpoint does not require any other HTTP methods.

### Resources

- Rotating Inngest keys: https://www.inngest.com/docs/platform/manage/rotating-keys
- Inngest signing keys: https://www.inngest.com/docs/platform/signing-keys
- Inngest event keys: https://www.inngest.com/docs/events/creating-an-event-key
- Inngest security best practices: https://www.inngest.com/docs/learn/security

### Credits

- Ben Hylak - an independent security researcher, discovered and responsibly disclosed the vulnerability.

## References
- https://github.com/inngest/inngest-js/security/advisories/GHSA-2jf5-6wwv-vhxx
- https://nvd.nist.gov/vuln/detail/CVE-2026-42047
- https://github.com/inngest/inngest-js
- https://github.com/inngest/inngest-js/releases/tag/inngest%403.54.1
- https://vercel.com/docs/deployment-protection#standard-protection
- https://vercel.com/kb/guide/how-do-i-delete-an-individual-deployment
- https://www.inngest.com/docs/events/creating-an-event-key
- https://www.inngest.com/docs/learn/security
- https://www.inngest.com/docs/learn/serving-inngest-functions
- https://www.inngest.com/docs/platform/manage/rotating-keys
- https://www.inngest.com/docs/platform/signing-keys
