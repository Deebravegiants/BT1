# [M] http4k: BasicCookieStorage` (renamed `InsecureCookieStorage`) did not enforce RFC 6265 cookie scoping; new `DefaultCookieStorage` is now the default

## Summary
Severity: Medium
Advisory: GHSA-pr33-38xx-6r26
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-pr33-38xx-6r26
Type: github-advisory

## Affected
- Maven: `org.http4k:http4k-core` — affected >=6.0.0.0 <6.48.0.0
- Maven: `org.http4k:http4k-core` — affected >=5.0.0.0 <5.42.0.0
- Maven: `org.http4k:http4k-core` — affected >=0 <4.51.0.0

## Details
### Impact

The previous `BasicCookieStorage` did not enforce RFC 6265 scoping rules around cookie domain, path, and `Secure` attribute. A client using a single storage instance to talk to multiple origins could have cookies leak across domains, or have `Secure` cookies sent over plain HTTP — the deprecation message states it bluntly: *"BasicCookieStorage has no domain/path/scheme scoping and leaks cookies across origins. Use DefaultCookieStorage instead."*

**Who is affected:** any client using `BasicCookieStorage` directly with cookies for more than one origin or scheme. Single-origin uses are unaffected.

### Patches

| Line | Fixed in | Edition |
|------|----------|---------|
| v6.x (Community) | **6.48.0.0** | Community |
| v5.x (LTS) | **5.42.0.0** | Enterprise — contact [enterprise@http4k.org](mailto:enterprise@http4k.org) |
| v4.x (LTS) | **4.51.0.0** | Enterprise — contact [enterprise@http4k.org](mailto:enterprise@http4k.org) |

The fix introduces `DefaultCookieStorage` (RFC 6265 compliant) as the drop-in default; `BasicCookieStorage` is renamed `InsecureCookieStorage` and remains available for callers with a deliberate need for the old behaviour.

### Workarounds

For deployments that cannot upgrade immediately:
- Use a dedicated `BasicCookieStorage` instance per origin / scheme, or
- Switch to a separate RFC 6265-compliant cookie store implementation.

### References

- Fix release: [v6.48.0.0](https://github.com/http4k/http4k/releases/tag/6.48.0.0)
- Cookie storage rewrite: [`6a9b44d743`](https://github.com/http4k/http4k/commit/6a9b44d743)
- Background: [RFC 6265 — HTTP State Management Mechanism](https://datatracker.ietf.org/doc/html/rfc6265)

## References
- https://github.com/http4k/http4k/security/advisories/GHSA-pr33-38xx-6r26
- https://github.com/http4k/http4k/commit/6a9b44d743
- https://datatracker.ietf.org/doc/html/rfc6265
- https://github.com/http4k/http4k
- https://github.com/http4k/http4k/releases/tag/6.48.0.0
