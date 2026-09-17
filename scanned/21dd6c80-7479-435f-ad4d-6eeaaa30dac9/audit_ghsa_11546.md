# [H] express-rate-limit: IPv4-mapped IPv6 addresses bypass per-client rate limiting on servers with dual-stack network

## Summary
Severity: High
Advisory: GHSA-46wh-pxpv-q5gq
CVE: CVE-2026-30827
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-06
Source: https://github.com/advisories/GHSA-46wh-pxpv-q5gq
Type: github-advisory

## Affected
- npm: `express-rate-limit` — affected >=8.2.0 <8.2.2
- npm: `express-rate-limit` — affected >=8.1.0 <8.1.1
- npm: `express-rate-limit` — affected >=8.0.0 <8.0.2

## Details
## Summary

The default `keyGenerator` in express-rate-limit applies IPv6 subnet masking (`/56` by default) to all addresses that `net.isIPv6()` returns true for. This includes IPv4-mapped IPv6 addresses (`::ffff:x.x.x.x`), which Node.js returns as `request.ip` on dual-stack servers.

Because the first 80 bits of all IPv4-mapped addresses are zero, a `/56` (or any `/32` to `/80`) subnet mask produces the same network key (`::/56`) for **every** IPv4 client. This collapses all IPv4 traffic into a single rate-limit bucket: one client exhausting the limit causes HTTP 429 for all other IPv4 clients.

## Details

### Root Cause

In `source/ip-key-generator.ts`:

```typescript
export function ipKeyGenerator(ip: string, ipv6Subnet: number | false = 56) {
  if (ipv6Subnet && isIPv6(ip)) {
    return `${new Address6(`${ip}/${ipv6Subnet}`).startAddress().correctForm()}/${ipv6Subnet}`
  }
  return ip
}
```

`net.isIPv6('::ffff:192.168.1.1')` returns `true`, so IPv4-mapped addresses enter the subnet masking path. With a `/56` prefix, the start address for any `::ffff:x.x.x.x` is `::`, producing the key `::/56`.

### Proof of Concept

```javascript
const { isIPv6 } = require('net');
const { Address6 } = require('ip-address');

function ipKeyGenerator(ip, ipv6Subnet = 56) {
  if (ipv6Subnet && isIPv6(ip)) {
    return `${new Address6(`${ip}/${ipv6Subnet}`).startAddress().correctForm()}/${ipv6Subnet}`;
  }
  return ip;
}

console.log(ipKeyGenerator('::ffff:192.168.1.1', 56)); // ::/56
console.log(ipKeyGenerator('::ffff:10.0.0.1', 56));    // ::/56
console.log(ipKeyGenerator('::ffff:8.8.8.8', 56));     // ::/56
// ALL produce '::/56' — same bucket
```

### End-to-End Validation

On a dual-stack Express server (`app.listen(port, '::')`), tested with Express 5.2.1:
- `request.ip` for IPv4 clients is `::ffff:127.0.0.1`
- Rate limit key resolves to `::/56`
- After `limit` requests from any IPv4 client, all other IPv4 clients receive 429

### When This Occurs

- Node.js dual-stack servers (default on Linux when listening on `::`)
- Any environment where `request.ip` contains IPv4-mapped IPv6 addresses
- Only affects the default `keyGenerator` (custom key generators are not affected)

## Impact

- **Denial of Service**: A single client can block all IPv4 traffic by exhausting the shared rate limit
- **Affects default configuration**: No special options needed to trigger this

## Affected Versions

All versions of express-rate-limit between v8.0.0 and v8.2.1.

## Fix

This issue was fixed in commit 14e53888cdfd1b9798faf5b634c4206409e27fc4. This fix has been included in release v8.3.0, and backported to all affected minor versions in the form of releases v8.2.2, v8.1.1, and v8.0.2.

## References
- https://github.com/express-rate-limit/express-rate-limit/security/advisories/GHSA-46wh-pxpv-q5gq
- https://nvd.nist.gov/vuln/detail/CVE-2026-30827
- https://github.com/express-rate-limit/express-rate-limit/commit/14e53888cdfd1b9798faf5b634c4206409e27fc4
- https://github.com/express-rate-limit/express-rate-limit
