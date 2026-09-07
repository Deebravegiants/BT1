# [M] Protocol-Relative URL Injection via Single Backslash Bypass in Angular SSR

## Summary
Severity: Medium
Advisory: GHSA-vfx2-hv2g-xj5f
CVE: CVE-2026-33397
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-vfx2-hv2g-xj5f
Type: github-advisory

## Affected
- npm: `@angular/ssr` — affected >=22.0.0-next.0 <22.0.0-next.2
- npm: `@angular/ssr` — affected >=21.0.0-next.0 <21.2.3
- npm: `@angular/ssr` — affected >=20.0.0-next.0 <20.3.21

## Details
An Open Redirect vulnerability exists in `@angular/ssr` due to an incomplete fix for CVE-2026-27738. While the original fix successfully blocked multiple leading slashes (e.g., `///`), the internal validation logic fails to account for a single backslash (`\`) bypass.

When an Angular SSR application is deployed behind a proxy that passes the `X-Forwarded-Prefix` header:

- An attacker provides a value starting with a single backslash (e.g., `\evil.com`).
- The internal validation failed to flag the single backslash as invalid.
- The application prepends a leading forward slash, resulting in a `Location` header containing `/\evil.com`.
- Modern browsers interpret the `/\` sequence as `//`, treating it as a protocol-relative URL and redirecting the user to the attacker-controlled domain.

Furthermore, the response lacks the `Vary: X-Forwarded-Prefix` header, allowing the malicious redirect to be stored in intermediate caches (Web Cache Poisoning).

### Impact
This vulnerability allows attackers to conduct large-scale phishing and SEO hijacking:

- **Scale**: A single request can poison a high-traffic route, impacting all users until the cache expires.
- **SEO Poisoning**: Search engine crawlers may follow and index these malicious redirects, causing the legitimate site to be delisted or associated with malicious domains.
- **Trust**: Because the initial URL belongs to the trusted domain, users and security tools are less likely to flag the redirect as malicious.

### Patches

- 22.0.0-next.2
- 21.2.3
- 20.3.21

### Workarounds
Until the patch is applied, developers should sanitize the `X-Forwarded-Prefix` header in their `server.ts` before the Angular engine processes the request:

```ts
app.use((req, res, next) => {
  const prefix = req.headers['x-forwarded-prefix'];
  if (typeof prefix === 'string') {
    // Sanitize by removing all leading forward and backward slashes
    req.headers['x-forwarded-prefix'] = prefix.trim().replace(/^[/\\]+/, '/');
  }
  next();
});
```


### References

- Fix: https://github.com/angular/angular-cli/pull/32771
- Original CVE: CVE-2026-27738

## References
- https://github.com/angular/angular-cli/security/advisories/GHSA-vfx2-hv2g-xj5f
- https://nvd.nist.gov/vuln/detail/CVE-2026-33397
- https://github.com/angular/angular-cli/pull/32771
- https://github.com/advisories/GHSA-xh43-g2fq-wjrj
- https://github.com/angular/angular-cli
