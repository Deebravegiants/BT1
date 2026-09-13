# [M] Hono has an Arbitrary Key Read in Serve static Middleware (Cloudflare Workers Adapter)

## Summary
Severity: Medium
Advisory: GHSA-w332-q679-j88p
CVE: CVE-2026-24473
CWE: CWE-200, CWE-284, CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-w332-q679-j88p
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.11.7

## Details
## Summary

Serve static Middleware for the Cloudflare Workers adapter contains an information disclosure vulnerability that may allow attackers to read arbitrary keys from the Workers environment. Improper validation of user-controlled paths can result in unintended access to internal asset keys.

## Details

The vulnerability exists in the serve-static middleware used with the Cloudflare Workers adapter. When serving static assets, the middleware does not sufficiently validate or restrict user-supplied paths before resolving them against the Workers asset storage.

As a result, an attacker may craft requests that access arbitrary keys beyond the intended static asset scope. This issue only affects applications running on Cloudflare Workers that use Serve static Middleware with user-controllable request paths.

## Impact

This vulnerability may lead to information disclosure by allowing unauthorized access to internal assets or data stored in the Workers environment. The exposed data is limited to readable asset keys and does not allow modification of stored data or execution of arbitrary code.

The impact is limited to applications that use Serve static Middleware in the Cloudflare Workers adapter and rely on it to safely handle untrusted request paths.

## Affected Components

* Serve static Middleware (Cloudflare Workers adapter)

## References
- https://github.com/honojs/hono/security/advisories/GHSA-w332-q679-j88p
- https://nvd.nist.gov/vuln/detail/CVE-2026-24473
- https://github.com/honojs/hono/commit/cf9a78db4d0a19b117aee399cbe9d3a6d9bfd817
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.11.7
