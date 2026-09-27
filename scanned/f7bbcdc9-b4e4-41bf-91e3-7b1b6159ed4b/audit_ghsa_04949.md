# [H] Astro: Host header SSRF in prerendered error page fetch

## Summary
Severity: High
Advisory: GHSA-2pvr-wf23-7pc7
CVE: CVE-2026-54299
CWE: CWE-20, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-2pvr-wf23-7pc7
Type: github-advisory

## Affected
- npm: `astro` — affected >=0 <6.4.6

## Details
## Summary

Astro SSR apps with prerendered error pages (`/404` or `/500` using `export const prerender = true`) fetch those pages over HTTP at runtime when an error occurs. The URL for this fetch is derived from `request.url`, which in turn gets its origin from the incoming `Host` header. When the `Host` header is not validated against `allowedDomains`, an attacker can point the fetch at an arbitrary host and read the response.

## Who is affected

This affects SSR deployments that:

1. Have a prerendered 404 or 500 page
2. Use `createRequestFromNodeRequest` from `astro/app/node` with `app.render()` **without** overriding `prerenderedErrorPageFetch` — this includes custom servers built on the public API and third-party adapters

**Not affected:**
- `@astrojs/node` >= 9.5.4 (reads error pages from disk)
- `@astrojs/cloudflare` (uses the ASSETS binding)
- The dev server (renders error pages in-process)

## How it works

`createRequestFromNodeRequest` builds `request.url` from the raw `Host` / `:authority` header. The `allowedDomains` option is accepted but only gates `X-Forwarded-For` — it does not constrain the URL origin. (The public `createRequest` does fall back to `localhost` for unvalidated hosts; this internal builder did not.)

When `app.render()` encounters a 404 or 500 with a prerendered error route, `default-handler.ts` constructs the error page URL using the origin from `request.url` and fetches it via `prerenderedErrorPageFetch`, which defaults to global `fetch`. The response body is served to the client.

An attacker sends a request with `Host: attacker-host:port`, triggers an error (e.g., requesting a nonexistent path for a 404), and receives the response from the attacker-controlled host reflected back.

## Remediation

The error page fetch origin is now validated against `allowedDomains` before use. When the host is validated, the original origin is preserved. Otherwise, it falls back to `localhost`. The fetch is also wrapped in a try/catch so that connection failures degrade gracefully to a plain error response.

## Credit

5ud0 / Tarmo Technologies

## References
- https://github.com/withastro/astro/security/advisories/GHSA-2pvr-wf23-7pc7
- https://nvd.nist.gov/vuln/detail/CVE-2026-54299
- https://github.com/withastro/astro
