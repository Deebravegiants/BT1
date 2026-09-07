# [H] Better Auth: Rate limiter keys IPv6 addresses individually and is bypassable via prefix rotation

## Summary
Severity: High
Advisory: GHSA-p6v2-xcpg-h6xw
CVE: CVE-2026-45364
CWE: CWE-307
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-p6v2-xcpg-h6xw
Type: github-advisory

## Affected
- npm: `better-auth` — affected >=0 <1.4.17
- npm: `better-auth` — affected >=1.5.0-beta.1 <1.5.0-beta.9

## Details
### Am I affected?

Users are affected if all of the following are true:

- Their app uses `better-auth` at a version `< 1.4.17`, or at a v1.5 prerelease tagged `<= 1.5.0-beta.8`.
- The apps authentication endpoints serve clients reachable over IPv6. Most managed hosts including Cloudflare, Vercel, Fly.io, AWS Application Load Balancer, and Google Cloud Load Balancing advertise IPv6 by default.
- The app's rate-limit configuration is enabled (the production default) and relies on the leftmost `x-forwarded-for` value (the stock setup) or any other configured IP-bearing header.

If users are on `1.4.16` specifically, the `normalizeIP` helper exists in your version but the IPv6 prefix length defaults to `/128`. Stock config still permits prefix rotation because no prefix mask is applied. Either upgrade to `1.4.17` or set `advanced.ipAddress.ipv6Subnet: 64` in the config.

If applications do not use the rate limiter, or if the deployment serves only IPv4 clients, the prefix-rotation vector does not apply. The representation-aliasing vector still applies to IPv6 addresses delivered over IPv4 transport in some edge cases (an upstream proxy carrying an IPv4-mapped IPv6 source), but it is rare in practice.

Fix:

1. Upgrade to `better-auth@1.4.17` or later. The current stable line `1.6.x` and the pre-release line `1.7.0-beta` both carry the fix.
2. If applications cannot upgrade, see workarounds below.

### Summary

Better Auth's HTTP rate limiter keyed each request by the exact textual IP address it received in `x-forwarded-for` (or the configured IP-bearing header). IPv6 clients controlling a typical `/64` allocation could rotate through 2^64 distinct source addresses without exhausting the per-address counter, defeating rate limiting on `/sign-in/email`, `/sign-up/email`, `/forget-password`, and every other path the limiter protects. The same bug allowed a single client to vary the textual encoding of one IPv6 address (uppercase, compression, IPv4-mapped, hex-encoded IPv4-in-IPv6) and produce multiple distinct keys.

### Details

The pre-fix `getIp` function returned the leftmost `x-forwarded-for` value verbatim after a single validity check, and `onRequestRateLimit` constructed the rate-limit key by string concatenation of that value with the request path. Two facts of IPv6 made the key space larger than the population of clients:

- ISPs and cloud providers assign prefixes, not addresses. RFC 6177 recommends `/56` for residential users; cloud providers commonly assign `/29` to `/48`. An attacker controlling a single `/64` therefore controls 2^64 source addresses without doing anything unusual.
- IPv6 has multiple textual representations for the same address. RFC 5952 specifies a canonical form, but RFC 4291 §2.2 permits the older mixed forms, and `::ffff:0:0/96` IPv4-mapped addresses can be written as either dotted-decimal or hex-encoded.

The fix in `better-auth@1.4.17` introduces `normalizeIP` and applies it to every `getIp` result. Normalization expands compressed IPv6 forms, lowercases hex digits, collapses IPv4-mapped IPv6 to plain IPv4, and applies a default `/64` prefix mask. The rate-limit key construction now uses an explicit `|` separator to prevent key-construction collisions across address-and-path joins.

The `/64` default matches the smallest commonly-allocated IPv6 unit, so a single client cannot use prefix rotation to defeat rate limiting on stock config. Operators who serve clients on coarser allocations (`/56` for residential ISPs, larger for cloud) can configure `advanced.ipAddress.ipv6Subnet` accordingly.

### Patches

Fixed in `better-auth@1.4.17` on the v1.4.x maintenance line and in `better-auth@1.5.0-beta.9` on the v1.5.x line. PR #7470 introduced the normalization primitive (`packages/core/src/utils/ip.ts`) and applied it to `getIp` and the rate-limit key. PR #7509 changed the IPv6 prefix-length default from `/128` to `/64` so that stock config closes the prefix-rotation vector without requiring users to opt in.

After the patch, the rate limiter treats all IPv6 addresses within a `/64` allocation as a single client, all textual encodings of one IPv6 address as the same address, and all IPv4-mapped IPv6 addresses as their underlying IPv4 form.

### Workarounds

If users cannot upgrade past `1.4.17`:

- **On `>= 1.4.16`**: set `advanced.ipAddress.ipv6Subnet: 64` in the auth configuration. The `normalizeIP` helper is present at `1.4.16`; only the default is wrong. This restores the post-`1.4.17` behavior on stock config.
- **On `< 1.4.16`**: shift the bypass mitigation upstream. Set the IPv6 prefix length on the app's CDN, WAF, or load balancer rate-limit policy to `/64` (or coarser per RFC 6177 if the app serves residential traffic). Cloudflare, Vercel Firewall, AWS WAF, and Google Cloud Armor all support per-prefix rate limiting.
- **As a partial mitigation on any version**: tighten the `customRules` window for sign-in, sign-up, and password-reset endpoints. This narrows the abuse window but does not close it.

### Impact

The bypass enables unbounded authentication attempts from a single IPv6-capable client. Direct consequences:

- Credential-stuffing and brute-force on `/sign-in/email` are no longer rate-limited per client.
- Account enumeration via response-shape differences becomes faster.
- Password-reset and email-verification email fan-out can be amplified.

The bypass does not directly compromise any account. Successful exploitation still requires the attacker to guess a credential the password store accepts. The rating reflects the loss of one defense-in-depth layer rather than a direct compromise.

### Credit

Reported by `@nexryai` on GitHub.

### Resources

- [CWE-307: Improper Restriction of Excessive Authentication Attempts](https://cwe.mitre.org/data/definitions/307.html)
- [RFC 4291: IP Version 6 Addressing Architecture](https://datatracker.ietf.org/doc/html/rfc4291)
- [RFC 5952: A Recommendation for IPv6 Address Text Representation](https://datatracker.ietf.org/doc/html/rfc5952)
- [RFC 6177: IPv6 Address Assignment to End Sites](https://datatracker.ietf.org/doc/html/rfc6177)

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-p6v2-xcpg-h6xw
- https://nvd.nist.gov/vuln/detail/CVE-2026-45364
- https://github.com/better-auth/better-auth/pull/7470
- https://github.com/better-auth/better-auth/pull/7509
- https://github.com/better-auth/better-auth/commit/43e719bcc0c223c7079fa0c611a9cf7ea1188254
- https://github.com/better-auth/better-auth/commit/57af0f7b910dcf7b1a5c0615d10b9bd56bb69bef
- https://github.com/better-auth/better-auth
