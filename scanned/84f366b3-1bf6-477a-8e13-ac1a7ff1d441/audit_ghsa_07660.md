# [M] Angular SSR has an Open Redirect via X-Forwarded-Prefix

## Summary
Severity: Medium
Advisory: GHSA-xh43-g2fq-wjrj
CVE: CVE-2026-27738
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-xh43-g2fq-wjrj
Type: github-advisory

## Affected
- npm: `@angular/ssr` — affected >=21.2.0-next.0 <21.2.0-rc.1
- npm: `@angular/ssr` — affected >=21.0.0-next.0 <21.1.5
- npm: `@angular/ssr` — affected >=20.0.0-next.0 <20.3.17
- npm: `@angular/ssr` — affected >=19.0.0-next.0 <19.2.21

## Details
An Open Redirect vulnerability exists in the internal URL processing logic in Angular SSR. The logic normalizes URL segments by stripping leading slashes; however, it only removes a single leading slash.

When an Angular SSR application is deployed behind a proxy that passes the `X-Forwarded-Prefix` header, an attacker can provide a value starting with three slashes (e.g., `///evil.com`).

1. The application processes a redirect (e.g., from a router `redirectTo` or i18n locale switch).
2. Angular receives `///evil.com` as the prefix.
3. It strips one slash, leaving `//evil.com`.
4. The resulting string is used in the `Location` header.
5. Modern browsers interpret `//` as a protocol-relative URL, redirecting the user from `https://your-app.com` to `https://evil.com`.


### Impact
This vulnerability allows attackers to conduct large-scale phishing and SEO hijacking:
- **Scale:** A single request can poison a high-traffic route, impacting all users until the cache expires.
- **SEO Poisoning:** Search engine crawlers may follow and index these malicious redirects, causing the legitimate site to be delisted or associated with malicious domains.
- **Trust:** Because the initial URL belongs to the trusted domain, users and security tools are less likely to flag the redirect as malicious.

### Attack Preconditions

- The application must use Angular SSR.
- The application must have routes that perform internal redirects.
- The infrastructure (Reverse Proxy/CDN) must pass the `X-Forwarded-Prefix` header to the SSR process without sanitization.
- The cache must not vary on the `X-Forwarded-Prefix` header.

### Patches
- 21.2.0-rc.1
- 21.1.5
- 20.3.17
- 19.2.21

### Workarounds
Until the patch is applied, developers should sanitize the `X-Forwarded-Prefix` header in their`server.ts` before the Angular engine processes the request:

```ts
app.use((req, res, next) => {
  const prefix = req.headers['x-forwarded-prefix']?.trim();
  if (prefix) {
    // Sanitize by removing all leading slashes
    req.headers['x-forwarded-prefix'] = prefix.replace(/^[/\\]+/, '/');
  }
  next();
});

```

### Resources
- [Report](https://github.com/angular/angular-cli/issues/32501)
- [Fix](https://github.com/angular/angular-cli/pull/32521)

## References
- https://github.com/angular/angular-cli/security/advisories/GHSA-xh43-g2fq-wjrj
- https://nvd.nist.gov/vuln/detail/CVE-2026-27738
- https://github.com/angular/angular-cli/issues/32501
- https://github.com/angular/angular-cli/pull/32521
- https://github.com/angular/angular-cli/commit/f086eccc36d10cf01c426e35864bc32e1e292323
- https://github.com/angular/angular-cli
