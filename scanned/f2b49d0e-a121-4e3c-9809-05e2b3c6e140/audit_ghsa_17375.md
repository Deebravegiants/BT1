# [H] Better Auth affected by external request basePath modification DoS

## Summary
Severity: High
Advisory: GHSA-569q-mpph-wgww
CVE: CVE-2025-71401
CWE: CWE-73, CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-12-01
Source: https://github.com/advisories/GHSA-569q-mpph-wgww
Type: github-advisory

## Affected
- npm: `better-auth` — affected >=0 <1.4.2

## Details
# Summary

Affected versions of Better Auth allow an external request to configure `baseURL` when it isn’t defined through any other means. This can be abused to poison the router’s base path, causing all routes to return 404 for all users.

This issue is only exploitable when `baseURL` is not explicitly configured (e.g., `BETTER_AUTH_URL` is missing) *and* the attacker is able to make the very first request to the server after startup. In properly configured environments or typical managed hosting platforms, this fallback behavior cannot be reached.

# Details

A combination of `X-Forwarded-Host` and `X-Forwarded-Proto` is implicitly trusted. This allows the first request to configure baseURL whenever it is not explicitly configured.

Here's the code that reads the headers:

<img width="631" height="219" alt="headers" src="https://github.com/user-attachments/assets/b3fb0078-a62f-4058-9d0b-4afbd30c4953" />

Here's the call to `getBaseURL()`, the result is assigned to `ctx.baseURL`.

<img width="838" height="414" alt="write" src="https://github.com/user-attachments/assets/a7b4dd17-75c3-49ef-9d08-6a2079d6a0ea" />

Here's the router receiving the poisoned `basePath`:

<img width="594" height="372" alt="router" src="https://github.com/user-attachments/assets/5fdf2862-9cd1-4b96-b146-18e67d904157" />

`X-Forwarded-Host` and `X-Forwarded-Proto` can be used to modify the pathname of a parsed URL object which forms `baseURL`. `basePath` is then derived from the pathname of `baseURL`. Once the router `basePath` is poisoned it fails to match & route incoming requests.

# Repro

Start a better-auth server with no `baseURL` configuration.

Send the following request as the first request to the server:

```curl
curl -i --location 'https://example.com/api/auth/ok' \
--header 'X-Forwarded-Proto: some:' \
--header 'X-Forwarded-Host: junk'
```

The better-auth API check endpoint returns 404.

Now send a regular request without the `X-Forwarded-Proto` and `X-Forwarded-Host` headers.

```curl
curl -i --location 'https://example.com/api/auth/ok'
```

The better-auth API check endpoint still returns 404.

_Example result_

<img width="662" height="307" alt="attack" src="https://github.com/user-attachments/assets/5a9cfdb5-3db7-4504-9f0a-b3c32a6dc823" />

We have modified the `basePath` for the router until the server is restarted. An attacker can repeatedly send these attack requests aiming to persistently exploit the vulnerability.

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-569q-mpph-wgww
- https://nvd.nist.gov/vuln/detail/CVE-2025-71401
- https://github.com/ray-project/ray/commit/70e7c72780bdec075dba6cad1afe0832772bfe09
- https://github.com/better-auth/better-auth
- https://github.com/better-auth/better-auth/releases/tag/v1.4.2
- https://www.vulncheck.com/advisories/better-auth-before-basepath-modification-dos
