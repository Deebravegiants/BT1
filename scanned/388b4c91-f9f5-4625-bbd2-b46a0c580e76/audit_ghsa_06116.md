# [M] ip-address: a CIDR suffix on the parsed address suppresses special-use classification and can bypass SSRF and trust-boundary checks

## Summary
Severity: Medium
Advisory: GHSA-4xrf-jv44-h6hh
CVE: CVE-2026-69198
CWE: CWE-20, CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-4xrf-jv44-h6hh
Type: github-advisory

## Affected
- npm: `ip-address` — affected >=10.1.1 <10.2.2

## Details
### Summary

Every special-use classification method is built on `isInSubnet`, which short-circuits to `false` whenever the address's own subnet mask is *shorter* than the reference range's mask. That mask comes verbatim from the CIDR suffix on the parsed input, so appending a suffix such as `/0` suppresses classification entirely: `isLoopback()`, `isPrivate()`, `isLinkLocal()`, `isCGNAT()`, `isMulticast()`, `isUnspecified()`, `isBroadcast()`, `isULA()`, and `getType()` all report an internal address as unremarkable, while `correctForm()` and `address` still return the real internal target.

An application that builds a network trust-boundary decision on these checks (for example a filter intended to block Server-Side Request Forgery, or SSRF) may therefore treat an internal target as external and allow the request. SSRF is an attack in which a user-supplied address coaxes the server into making a request to an internal destination the user could not otherwise reach, such as a loopback service or a cloud metadata endpoint.

### Details

`isInSubnet` in `src/common.ts` opens with a guard that compares the two prefix lengths:

```js
export function isInSubnet(this, address) {
  if (this.subnetMask < address.subnetMask) {
    return false;                                  // <-- reached before any bit comparison
  }

  if (this.mask(address.subnetMask) === address.mask()) {
    return true;
  }

  return false;
}
```

That guard is correct for the question `isInSubnet` is named for — whether one *network* is contained in another, where a `/0` network genuinely is not inside a `/8`. It is wrong for classification, which asks a question about the address itself and must not depend on the prefix the caller happened to write. `/0` is shorter than every reference prefix in the special-use tables (loopback `/8`, link-local `/16`, CGNAT `/10`, ULA `/7`, multicast `/4`), so for a classification call the bit comparison is never reached and the method returns `false`.

The underlying bit comparison is correct, and `mask(n)` already returns the first `n` bits of the full parsed address independently of `subnetMask` — the defect is solely that the containment guard sits in the classification path. Host bits are retained through parsing, so `correctForm()` still yields the real target and the address remains fully usable for connecting.

`/0` is the universal case because it is shorter than every reference prefix, but any suffix shorter than the specific range being tested has the same effect: `10.0.0.5/7` defeats `isPrivate()` for `10.0.0.0/8`.

### Affected versions

`>= 10.1.1, <= 10.2.1`. The `is*` classification API was introduced for `Address4` in 10.1.1 and extended to `Address6` in 10.2.0; releases before 10.1.1 do not expose it and are not affected through this vector. The containment guard itself is much older, but `isInSubnet` alone is a subnet-containment predicate whose behavior here is correct.

This also defeats the fix released in 10.2.1 for GHSA-22jq-vg5j-6vgg: that release classifies IPv4-mapped and NAT64 addresses by their embedded IPv4 address, but the normalization is reached through `isInSubnet`, so `::ffff:127.0.0.1/0` reverts to being reported as non-internal.

### Impact

Every classifier is affected on both `Address4` and `Address6`. The sole exception is `Address6.isLinkLocal()` for *native* `fe80::/10` addresses, which compares raw bits directly; its IPv4-mapped path is still affected.

| Address | Reported as | Actually points at |
|---|---|---|
| `127.0.0.1/0` | not loopback | loopback (`127.0.0.0/8`) |
| `10.0.0.1/0`, `10.0.0.5/7` | not private | RFC 1918 `10/8` |
| `172.16.5.5/0` | not private | RFC 1918 `172.16/12` |
| `192.168.1.1/0` | not private | RFC 1918 `192.168/16` |
| `169.254.169.254/0` | not link-local | link-local / cloud metadata (IMDS) |
| `100.64.0.1/0` | not CGNAT | CGNAT `100.64/10` |
| `0.0.0.0/0`, `255.255.255.255/0` | not unspecified / not broadcast | unspecified / broadcast |
| `::1/0` | not loopback | IPv6 loopback |
| `fc00::1/0` | not ULA, not private | IPv6 ULA `fc00::/7` |
| `ff02::1/0` | not multicast | IPv6 multicast |
| `::ffff:127.0.0.1/0` | not loopback | loopback, via IPv4-mapped |
| `::ffff:169.254.169.254/0` | not link-local | IMDS, via IPv4-mapped |
| `64:ff9b::7f00:1/0` | not loopback | loopback, via NAT64 |

`getType()` returns `Global unicast` for all of the IPv6 cases above, and `getScope()` follows it.

### Reachability

A CIDR suffix is not legal in a URL host, so this is not reachable through the most common SSRF shape. `new URL('http://127.0.0.1/0')` parses `hostname` as `127.0.0.1` and `pathname` as `/0`, and a guard that classifies the extracted hostname is unaffected. Exploitation requires an application that accepts a bare address string that may carry a suffix and passes it to the constructor before classifying — for example an allow/deny field, a webhook target, or a proxy destination taken as a plain host rather than parsed out of a URL.

### Proof of concept

`npm i ip-address@10.2.1`, then:

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
    return a.isPrivate() || a.isLoopback() || a.isLinkLocal() || a.isULA()
        || a.isMulticast() || a.isUnspecified();
  } catch {}
  return false;
}

for (const h of ['127.0.0.1', '10.0.0.1', '::1',
                 '127.0.0.1/0', '10.0.0.5/7', '169.254.169.254/0',
                 '::1/0', '::ffff:127.0.0.1/0', '64:ff9b::7f00:1/0']) {
  console.log(isBlocked(h) ? 'BLOCK ' : 'ALLOW ', h, '->', new (h.includes(':') ? Address6 : Address4)(h).correctForm());
}
```

On affected versions every suffixed internal target is allowed, and `correctForm()` shows the request would reach the real internal address:

```
BLOCK  127.0.0.1 -> 127.0.0.1
BLOCK  10.0.0.1 -> 10.0.0.1
BLOCK  ::1 -> ::1
ALLOW  127.0.0.1/0 -> 127.0.0.1
ALLOW  10.0.0.5/7 -> 10.0.0.5
ALLOW  169.254.169.254/0 -> 169.254.169.254
ALLOW  ::1/0 -> ::1
ALLOW  ::ffff:127.0.0.1/0 -> ::ffff:7f00:1
ALLOW  64:ff9b::7f00:1/0 -> 64:ff9b::7f00:1
```

The first three lines are blocked as expected; the same destinations with a CIDR suffix are allowed through.

### Remediation

Upgrade to the patched release. In the fix, classification no longer consults the address's own prefix: a new `isHostInSubnet()` compares the address's host bits against the reference range only, and every classifier (`isLoopback`, `isPrivate`, `isLinkLocal`, `isCGNAT`, `isMulticast`, `isUnspecified`, `isBroadcast`, `isULA`, `isMapped4`, `isTeredo`, `is6to4`, `isDocumentation`, `getType`, and the IPv4-mapped/NAT64 normalization behind `embeddedIPv4`) uses it. `isInSubnet` keeps its subnet-containment semantics unchanged, including the guard that a wider network is not contained in a narrower one. After upgrading, `new Address4('127.0.0.1/0').isLoopback()` returns `true`.

If you cannot upgrade immediately, strip the suffix before classifying by re-parsing `addressMinusSuffix`:

```js
const parsed = new Address4(userInput);
const host = new Address4(parsed.addressMinusSuffix);   // classify this one
```

### A note on SSRF defense

These methods are address classifiers, not a complete SSRF defense. Regardless of this fix, a robust SSRF guard must resolve the hostname and validate the *resolved* IP against the socket it connects to, and account for DNS rebinding and redirects. Treat these checks as one layer, not the only one.

### Credit

Reported by @hi-im-glitchless.

## References
- https://github.com/beaugunderson/ip-address/security/advisories/GHSA-4xrf-jv44-h6hh
- https://github.com/beaugunderson/ip-address/commit/488fe9bc7c35363b4b090494fc38c266d217740d
- https://github.com/beaugunderson/ip-address
- https://github.com/beaugunderson/ip-address/releases/tag/v10.2.2
