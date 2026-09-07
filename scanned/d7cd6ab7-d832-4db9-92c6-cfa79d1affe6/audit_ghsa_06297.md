# [M] ip-address: misclassification of IPv4-mapped/NAT64 IPv6 addresses can bypass SSRF and trust-boundary checks

## Summary
Severity: Medium
Advisory: GHSA-22jq-vg5j-6vgg
CVE: CVE-2026-54272
CWE: CWE-20, CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-22jq-vg5j-6vgg
Type: github-advisory

## Affected
- npm: `ip-address` — affected >=10.1.1 <10.2.1

## Details
### Summary

`Address6`'s special-property checks misclassify IPv4-mapped (`::ffff:0:0/96`) and NAT64 well-known (`64:ff9b::/96`) IPv6 addresses. These checks classify an address by its IPv6 wrapper rather than by the IPv4 address it embeds, so `isLoopback()`, `isLinkLocal()`, `isMulticast()`, and `isUnspecified()` all return `false` for literals such as `::ffff:127.0.0.1` or `::ffff:169.254.169.254` that actually route to loopback, RFC 1918, or link-local (cloud-metadata) destinations. `Address6` also had no `isPrivate()` method, so a mapped RFC 1918 address could not be detected at all.

An application that builds a network trust-boundary decision on these checks (for example, a filter intended to block Server-Side Request Forgery, or SSRF) may therefore treat an internal target as external and allow the request. SSRF is an attack in which a user-supplied address coaxes the server into making a request to an internal destination the user could not otherwise reach, such as a loopback service or a cloud metadata endpoint.

### Details

`Address6.getType()` classifies an address by matching it against a table of known IPv6 special-use prefixes, returning `Global unicast` when nothing matches. That table had no entry for the IPv4-mapped range (`::ffff:0:0/96`), so every mapped address fell through to `Global unicast`; NAT64 addresses matched their own `NAT64 …` labels. The boolean checks `isLoopback`, `isUnspecified`, and `isMulticast` compared `getType()` against a fixed label and so returned `false`, while `isLinkLocal` and `isULA` checked only the native IPv6 ranges.

The library already exposed `isMapped4()` and `to4()`, but did not apply them inside these checks, so a mapped or NAT64 address was never normalized to its embedded IPv4 address before classification. The underlying CIDR matching is correct; the defect is that the special-use table omitted the IPv4-mapped range and the checks performed no embedded-IPv4 normalization.

### Affected versions

`>= 10.1.1, <= 10.2.0`. The `is*` classification API was introduced for `Address4` in 10.1.1 and extended to `Address6` in 10.2.0. Releases before 10.1.1 do not expose this API and are not affected through this vector.

### Impact

The misclassification covers the entire `::ffff:0:0/96` range, in both dotted and hex notation and case-insensitively, plus the `64:ff9b::/96` NAT64 well-known prefix:

| Address | Reported as | Actually points at |
|---|---|---|
| `::ffff:127.0.0.1` / `::ffff:7f00:1` | Global unicast | loopback (`127.0.0.0/8`) |
| `::ffff:10.0.0.1` | Global unicast | RFC 1918 `10/8` |
| `::ffff:172.16.5.5` | Global unicast | RFC 1918 `172.16/12` |
| `::ffff:192.168.1.1` | Global unicast | RFC 1918 `192.168/16` |
| `::ffff:169.254.169.254` / `::ffff:a9fe:a9fe` | Global unicast | link-local / cloud metadata (IMDS) |
| `::ffff:100.64.0.1` | Global unicast | CGNAT `100.64/10` |
| `::ffff:0.0.0.0` / `::ffff:255.255.255.255` | Global unicast | unspecified / broadcast |
| `64:ff9b::7f00:1` / `64:ff9b::a9fe:a9fe` | NAT64 (well-known) | loopback / IMDS via NAT64 |

For IPv4-mapped addresses the host OS routes to the IPv4 stack, so the misclassification is reachable on any dual-stack host. For NAT64, the classification bypass is unconditional but end-to-end reachability additionally requires a NAT64/DNS64 gateway in the deployment network.

### Proof of concept

A guard assembled from these checks lets internal hosts through:

```js
const { Address4, Address6 } = require('ip-address');

// true => block as internal, false => allow outbound
function isBlocked(host) {
  try {
    const a = new Address4(host);
    return a.isPrivate() || a.isLoopback() || a.isLinkLocal() || a.isCGNAT()
        || a.isMulticast() || a.isUnspecified() || a.isBroadcast();
  } catch {}
  try {
    const a = new Address6(host);
    return a.isLoopback() || a.isLinkLocal() || a.isULA()
        || a.isMulticast() || a.isUnspecified();
  } catch {}
  return false;
}

for (const h of ['127.0.0.1', '::1', '10.0.0.1', '8.8.8.8',
                 '::ffff:127.0.0.1', '::ffff:10.0.0.1',
                 '::ffff:169.254.169.254', '64:ff9b::7f00:1']) {
  console.log(isBlocked(h) ? 'BLOCK ' : 'ALLOW ', h);
}
```

On affected versions this prints (note that every `::ffff:…` and `64:ff9b::…` internal target is allowed):

```
BLOCK  127.0.0.1
BLOCK  ::1
BLOCK  10.0.0.1
ALLOW  8.8.8.8
ALLOW  ::ffff:127.0.0.1
ALLOW  ::ffff:10.0.0.1
ALLOW  ::ffff:169.254.169.254
ALLOW  64:ff9b::7f00:1
```

The first three lines (native loopback, native IPv6 loopback, and a literal RFC 1918 address) are blocked as expected; the IPv4-mapped and NAT64 forms of the same internal destinations are allowed through.

### Remediation

Upgrade to the patched release. In the fix, `Address6` normalizes IPv4-mapped and NAT64 well-known addresses to their embedded IPv4 address before classifying, via a new `embeddedIPv4()` helper that `isLoopback`, `isLinkLocal`, `isMulticast`, and `isUnspecified` consult first. `Address6` also gains `isPrivate()`, `isCGNAT()`, and `isBroadcast()` for parity with `Address4`, and `getType()` now labels the `::ffff:0:0/96` range as `IPv4-mapped`. After upgrading, `new Address6('::ffff:127.0.0.1').isLoopback()` returns `true` and `new Address6('::ffff:10.0.0.1').isPrivate()` returns `true`.

If you cannot upgrade immediately, normalize embedded IPv4 addresses yourself before classifying: call `to4()` on any address where `isMapped4()` (or membership in `64:ff9b::/96`) is true, and run your IPv4 checks against the result.

### A note on SSRF defense

These methods are address classifiers, not a complete SSRF defense. Regardless of this fix, a robust SSRF guard must resolve the hostname and validate the *resolved* IP against the socket it connects to, and account for DNS rebinding and redirects. Treat these checks as one layer, not the only one.

### Credit

Reported by @OV-0-VO.

## References
- https://github.com/beaugunderson/ip-address/security/advisories/GHSA-22jq-vg5j-6vgg
- https://nvd.nist.gov/vuln/detail/CVE-2026-54272
- https://github.com/beaugunderson/ip-address/commit/4a1f613f4c1bec915677dea923c10aaa09361ef9
- https://github.com/beaugunderson/ip-address
- https://github.com/beaugunderson/ip-address/releases/tag/v10.2.1
