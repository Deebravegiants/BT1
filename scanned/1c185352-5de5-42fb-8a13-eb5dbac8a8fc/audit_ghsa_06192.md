# [M] Hono: Algorithmic Complexity DoS in Language Middleware

## Summary
Severity: Medium
Advisory: GHSA-54fx-42gc-7vw4
CVE: CVE-2026-71848
CWE: CWE-407
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-54fx-42gc-7vw4
Type: github-advisory

## Affected
- npm: `hono` — affected >=4.12.0 <4.12.34

## Details
### Summary

The `languageDetector` middleware is vulnerable to algorithmic complexity denial of service when processing a crafted language tag containing a large number of hyphen-separated subtags.

### Details

To implement progressive language-tag truncation, `normalizeLanguage()` repeatedly calls `parts.slice(0, i).join('-')` for every possible prefix. The total amount of string processing grows quadratically with the number of subtags.

Language values may come from a query parameter, cookie, `Accept-Language` header, or URL path, depending on the detector configuration. The default detector order enables query-string, cookie, and header detection, so applications using `languageDetector()` may expose this processing to unauthenticated requests.

Request-size limits reduce the maximum cost of a single request but do not eliminate the issue. Inputs accepted by common JavaScript runtimes can still cause noticeable synchronous event-loop blocking.

### Impact

An attacker may repeatedly send requests containing long, hyphen-separated language tags, causing excessive CPU consumption and preventing unrelated requests from being processed.

The practical impact depends on the runtime's request-size limits, reverse-proxy configuration, and the detectors enabled by the application.

### Resolution

The progressive lookup should avoid reconstructing every shorter prefix. The implementation can instead inspect the configured supported languages and select the longest value that matches the input at a hyphen boundary.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-54fx-42gc-7vw4
- https://github.com/honojs/hono/commit/f70e2c31684387b3231cc38512a31df6ca76a1c7
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.12.34
