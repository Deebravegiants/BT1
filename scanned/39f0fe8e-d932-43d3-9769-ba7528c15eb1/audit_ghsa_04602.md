# [M] Mailpit: Incomplete SSRF protection in Link Check API via IPv6 transition mechanisms

## Summary
Severity: Medium
Advisory: GHSA-w4mc-hhc6-xp28
CVE: CVE-2026-55187
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-w4mc-hhc6-xp28
Type: github-advisory

## Affected
- Go: `github.com/axllent/mailpit` — affected >=0 <1.30.2

## Details
## Summary

The remediation shipped in mailpit v1.29.2 for [GHSA-mpf7-p9x7-96r3](https://github.com/axllent/mailpit/security/advisories/GHSA-mpf7-p9x7-96r3) (CVE-2026-27808) is incomplete. The `tools.IsInternalIP` deny-list relies on Go's stdlib classification helpers (`IsLoopback`, `IsPrivate`, `IsLinkLocalUnicast`, `IsLinkLocalMulticast`, `IsUnspecified`, `IsMulticast`) plus an inline CGNAT range, but those helpers do **not** match two classes of IPv6 address that should be blocked for SSRF purposes:

1. **IPv6 forms that embed an IPv4 destination via documented translation mechanisms** — 6to4, NAT64, IPv4-compatible IPv6, ISATAP, or (in older Go versions) IPv4-mapped IPv6. These let an attacker reach internal IPv4 destinations by supplying an IPv6 literal that encodes the desired IPv4.

2. **IPv6 prefixes that fall outside the narrow private/loopback/link-local ranges Go's stdlib classifies** — specifically the deprecated site-local prefix `fec0::/10` (RFC 3879/4291) and the documentation prefix `2001:db8::/32` (RFC 3849). The first is still routable on dual-stack hosts and is cited as a bypass form in [CVE-2026-44430](https://advisories.gitlab.com/golang/github.com/modelcontextprotocol/registry/CVE-2026-44430/); the second should never appear in real network traffic and is safe to block as fail-safe behavior.

Together these gaps let the Link Check API be coerced into dialing internal destinations that the v1.29.2 fix was intended to block.

This is the same bug class as [GHSA-56c3-vfp2-5qqj / CVE-2026-44430 (MCP Registry)](https://advisories.gitlab.com/golang/github.com/modelcontextprotocol/registry/CVE-2026-44430/) and [GHSA-86m8-88fq-xfxp / CVE-2026-45741 (Gotenberg)](https://advisories.gitlab.com/golang/github.com/gotenberg/gotenberg/v8/CVE-2026-45741/) — projects that, like mailpit, built their SSRF deny-list around Go's stdlib `Is*` family and discovered the resulting bypass post-disclosure.

The underlying ecosystem-wide issue is tracked upstream at [**golang/go#79925**](https://github.com/golang/go/issues/79925), which proposes extending `net.IP.IsPrivate` to handle these IPv6 transition forms. Until that lands, every Go project that wants comprehensive SSRF protection has to implement the decoding itself — which is exactly the gap that produced this advisory and the three CVEs in adjacent projects cited above.

## Affected versions

- mailpit `v1.29.2` and later HEAD — the GHSA-mpf7-p9x7-96r3 fix is in place but [`tools.IsInternalIP`](https://github.com/axllent/mailpit/blob/a68499fa4e8874d414921fbd520e181dc92a39d7/internal/tools/net.go#L25-L34) does not cover the IPv6 forms enumerated below.
- Pre-`v1.29.2` versions remain vulnerable to the original advisory.

## Vulnerable code

[`internal/tools/net.go` L25-L34](https://github.com/axllent/mailpit/blob/a68499fa4e8874d414921fbd520e181dc92a39d7/internal/tools/net.go#L25-L34) — `IsInternalIP`:

```go
func IsInternalIP(ip net.IP) bool {
    return ip.IsLoopback() ||
        ip.IsPrivate() ||
        ip.IsLinkLocalUnicast() ||
        ip.IsLinkLocalMulticast() ||
        ip.IsUnspecified() ||
        ip.IsMulticast() ||
        cgnatRange.Contains(ip)
}
```

[`internal/linkcheck/status.go` L140-L163](https://github.com/axllent/mailpit/blob/a68499fa4e8874d414921fbd520e181dc92a39d7/internal/linkcheck/status.go#L140-L163) — `safeDialContext` calls `IsInternalIP` on resolved IPs before dialing, but only blocks when one of the seven predicates above fires.

For each of the following bypass forms, `net.IP.IsLoopback`, `IsPrivate`, `IsLinkLocalUnicast`, `IsLinkLocalMulticast`, `IsUnspecified`, `IsMulticast`, and the CGNAT range check all return `false` — so the dial proceeds:

**IPv4-embedded-in-IPv6 forms** (each carries an IPv4 destination via a documented translation prefix):

| Bypass IPv6 literal | Decoded IPv4 destination | RFC |
|---|---|---|
| `64:ff9b::a9fe:a9fe` | `169.254.169.254` (AWS / GCP / Azure metadata) | RFC 6052 — NAT64 well-known prefix |
| `64:ff9b:1::a9fe:a9fe` | `169.254.169.254` | RFC 8215 — NAT64 local-use |
| `2002:a9fe:a9fe::` | `169.254.169.254` | RFC 3056 — 6to4 |
| `::a9fe:a9fe` | `169.254.169.254` | RFC 4291 §2.5.5.1 — IPv4-compatible IPv6 |
| `64:ff9b::7f00:1` | `127.0.0.1` | RFC 6052 (loopback via NAT64) |
| `2002:0a00:0001::` | `10.0.0.1` | RFC 3056 (RFC 1918 via 6to4) |
| `<any-prefix>:5efe:<ipv4>` | `<ipv4>` (e.g. `2001:db8::5efe:7f00:1` → `127.0.0.1`) | RFC 5214 — ISATAP |

**Direct IPv6 prefixes not classified by the stdlib `Is*` family:**

| Bypass IPv6 literal | What it is | RFC |
|---|---|---|
| `fec0::1` (any address in `fec0::/10`) | Deprecated site-local — still routable on dual-stack hosts | RFC 3879 (deprecation) / RFC 4291 §2.5.7 |
| `2001:db8::1` (any address in `2001:db8::/32`) | Documentation prefix — should never appear on the wire | RFC 3849 |

`IsInternalIP` returns `false` for every entry in both tables.

The original advisory's stated mitigations *do* hold against the embedded-IPv4 forms in the narrow case where the IPv6 literal is `::ffff:<ipv4>` (IPv4-mapped), because Go's `net.IP.To4()` normalizes that form and the stdlib `Is*` methods then check the embedded IPv4. This was the partial fix shipped in [Go 1.22.4 / CVE-2024-24790](https://pkg.go.dev/vuln/GO-2024-2887). But it does not extend to 6to4, NAT64, IPv4-compatible, or ISATAP forms — those require explicit decoding that neither Go's stdlib nor `IsInternalIP` performs. The direct prefixes (`fec0::/10`, `2001:db8::/32`) likewise are simply outside the scope of any Go stdlib `Is*` method.

## Proof of Concept

The repro depends on environment-specific routing for the embedded IPv4 destination. The forms below all *pass* the `safeDialContext` check on a stock mailpit v1.29.2 — they will not be blocked by the SSRF deny-list. Whether they connect successfully depends on whether the host's network has NAT64 / 6to4 routing to reach the embedded IPv4.

### Unit-test repro (no network dependency)

The most defensible PoC is a unit test against `IsInternalIP` itself — it demonstrates the deny-list gap directly without depending on the test environment routing the bypass IPs:

```go
// internal/tools/net_ssrf_test.go
package tools

import (
    "net"
    "testing"
)

func TestIsInternalIP_UncoveredIPv6Forms(t *testing.T) {
    cases := map[string]net.IP{
        // IPv4-embedded-in-IPv6 forms.
        "NAT64 well-known wrapping AWS IMDS (RFC 6052)":     net.ParseIP("64:ff9b::a9fe:a9fe"),
        "NAT64 local-use wrapping AWS IMDS (RFC 8215)":      net.ParseIP("64:ff9b:1::a9fe:a9fe"),
        "6to4 wrapping AWS IMDS (RFC 3056)":                 net.ParseIP("2002:a9fe:a9fe::"),
        "IPv4-compatible IPv6 wrapping AWS IMDS (RFC 4291)": net.ParseIP("::a9fe:a9fe"),
        "NAT64 wrapping loopback (RFC 6052)":                net.ParseIP("64:ff9b::7f00:1"),
        "6to4 wrapping RFC 1918 (RFC 3056)":                 net.ParseIP("2002:0a00:0001::"),
        "ISATAP wrapping AWS IMDS (RFC 5214)":               net.ParseIP("2001:db8::5efe:a9fe:a9fe"),

        // Direct IPv6 prefixes outside the stdlib Is* family.
        "Deprecated site-local fec0::/10 (RFC 3879/4291)":   net.ParseIP("fec0::1"),
        "Documentation prefix 2001:db8::/32 (RFC 3849)":     net.ParseIP("2001:db8::1"),
    }

    for name, ip := range cases {
        t.Run(name, func(t *testing.T) {
            if !IsInternalIP(ip) {
                t.Errorf("IsInternalIP(%s) = false — SSRF deny-list bypass", ip)
            }
        })
    }
}
```

Run with:
```
go test ./internal/tools/ -run TestIsInternalIP_UncoveredIPv6Forms
```

On v1.29.2 every subtest fails. Each failure is a documented bypass.

### End-to-end repro

In an environment where the embedded IPv4 destination is reachable (e.g. a host whose network provides NAT64 to RFC 1918 / link-local):

1. Send a crafted email to mailpit's SMTP listener containing an `<a href>` with a bypass URL:
   ```html
   <a href="http://[64:ff9b::a9fe:a9fe]/latest/meta-data/iam/security-credentials/">link</a>
   ```
2. `POST /api/v1/message/{ID}/link-check`.
3. Observe the `doHead` HTTP HEAD response status — non-zero status (success or specific error) confirms the dial reached the destination rather than being blocked by `IsInternalIP`.

In environments without NAT64 / 6to4 routing the connection will time out, but the absence of a `private/reserved address` blocked response confirms the deny-list bypass logically; the unit test above is the canonical PoC.

## Impact

Identical scope and severity model to the original GHSA-mpf7-p9x7-96r3:

- The link-check API is reachable in mailpit's default deploy without authentication (no `--ui-auth`, no `--smtp-auth` required).
- An attacker who can deliver email to the mailpit SMTP listener (often unauthenticated in default config) and invoke the link-check API can probe internal services using any of the uncovered IPv6 forms above — either via the embedded-IPv4 mechanisms to reach IPv4 destinations like cloud metadata endpoints (`169.254.169.254`, `168.63.129.16`), or by addressing a routable IPv6 service via `fec0::/10` directly.
- The status-code-and-error feedback exposed by the link-check API leaks reachability information per probe.
- Damage ceiling is bounded by the mailpit response shape (status code, status text, `451 Blocked private/reserved address` sentinel) — no response body is exposed — but reachability + status-code mapping is sufficient for service discovery and for confirming cloud-metadata service identity.
- **Scope note:** `tools.IsInternalIP` is also used by the screenshot-proxy and HTML-Check-API endpoints (per maintainer disclosure). The same deny-list bypass applies to dialer decisions in those paths, but they include additional checks that mute the impact. The Link Check API remains the most revealing because its response includes the HTTP status code from the dialed destination; the other two are less directly leaky.

**Severity:** Moderate, mirroring the original advisory (CVSS 5.8).

## Suggested remediation

The fix has two parts:

1. **For the IPv4-embedded-in-IPv6 forms:** decode the embedded IPv4 and re-check it. This is the same pattern [Python's `ipaddress.is_private` implemented in 3.13](https://docs.python.org/3/library/ipaddress.html), what [`code.dny.dev/ssrf`](https://pkg.go.dev/code.dny.dev/ssrf) (IANA Special Purpose Registry-driven, auto-synced) implements out-of-the-box, and the behavior change being proposed for Go's stdlib at [golang/go#79925](https://github.com/golang/go/issues/79925).

2. **For the direct IPv6 prefixes:** add them to the first range check alongside `cgnatRange.Contains`.

Reference implementation (extends the existing helper, keeps the call-site contract identical):

```go
// internal/tools/net.go
package tools

import (
    "encoding/binary"
    "net"
)

var (
    cgnatRange          = mustCIDR("100.64.0.0/10")    // RFC 6598
    deprecatedSiteLocal = mustCIDR("fec0::/10")         // RFC 3879 / 4291
    documentationPrefix = mustCIDR("2001:db8::/32")     // RFC 3849
    nat64WellKnown      = mustCIDR("64:ff9b::/96")      // RFC 6052
    nat64LocalUse       = mustCIDR("64:ff9b:1::/48")    // RFC 8215
    sixToFour           = mustCIDR("2002::/16")         // RFC 3056
    teredo              = mustCIDR("2001::/32")         // RFC 4380
    ipv4Compatible      = mustCIDR("::/96")             // RFC 4291 §2.5.5.1
    ipv4Mapped          = mustCIDR("::ffff:0:0/96")     // RFC 4291 §2.5.5.2
)

func mustCIDR(s string) *net.IPNet {
    _, n, err := net.ParseCIDR(s)
    if err != nil {
        panic(err)
    }
    return n
}

// IsInternalIP reports whether ip should be blocked as a connection target.
// Covers the stdlib Is* checks plus CGNAT, plus IPv6 forms outside the
// stdlib's scope (deprecated site-local, documentation prefix, and the
// IPv6 transition mechanisms whose embedded IPv4 is itself internal).
func IsInternalIP(ip net.IP) bool {
    if ip.IsLoopback() ||
        ip.IsPrivate() ||
        ip.IsLinkLocalUnicast() ||
        ip.IsLinkLocalMulticast() ||
        ip.IsUnspecified() ||
        ip.IsMulticast() ||
        cgnatRange.Contains(ip) ||
        deprecatedSiteLocal.Contains(ip) ||
        documentationPrefix.Contains(ip) {
        return true
    }
    if embedded, ok := embeddedIPv4(ip); ok {
        return IsInternalIP(embedded)
    }
    return false
}

// embeddedIPv4 returns the IPv4 destination encoded in ip, if ip is an
// IPv6 form documented to carry an embedded IPv4 destination.
func embeddedIPv4(ip net.IP) (net.IP, bool) {
    // Skip IPv4 / IPv4-mapped IPv6 — covered by the stdlib Is* checks via To4.
    if ip.To4() != nil {
        return nil, false
    }
    ip16 := ip.To16()
    if ip16 == nil || len(ip16) != net.IPv6len {
        return nil, false
    }
    switch {
    case nat64WellKnown.Contains(ip16), nat64LocalUse.Contains(ip16),
        ipv4Compatible.Contains(ip16):
        // Last 32 bits are the embedded IPv4.
        return net.IPv4(ip16[12], ip16[13], ip16[14], ip16[15]).To4(), true
    case sixToFour.Contains(ip16):
        // Bits 16..47 are the embedded IPv4.
        return net.IPv4(ip16[2], ip16[3], ip16[4], ip16[5]).To4(), true
    case teredo.Contains(ip16):
        // Bits 96..127 are the embedded IPv4 XOR'd with 0xFFFFFFFF.
        x := binary.BigEndian.Uint32(ip16[12:16]) ^ 0xFFFFFFFF
        b := make([]byte, 4)
        binary.BigEndian.PutUint32(b, x)
        return net.IPv4(b[0], b[1], b[2], b[3]).To4(), true
    case ip16[10] == 0x5e && ip16[11] == 0xfe:
        // ISATAP (RFC 5214) — interface identifier ends with :5efe:<ipv4>.
        // Match structurally on bytes 10-11; the /64 prefix is not fixed.
        // Must run after the fixed-prefix cases above (Teredo can legitimately
        // have 5efe in bytes 10-11; its embedding takes precedence).
        return net.IPv4(ip16[12], ip16[13], ip16[14], ip16[15]).To4(), true
    }
    return nil, false
}
```

This covers every bypass in the two tables above. The direct-prefix additions (`deprecatedSiteLocal`, `documentationPrefix`) are two lines in the first if-block; the embedded-IPv4 decoder is the substantive new function.

**Alternative — adopt a comprehensive library:** Replace the hand-rolled deny-list with [`code.dny.dev/ssrf`](https://pkg.go.dev/code.dny.dev/ssrf), which generates its IPv4 and IPv6 prefix lists from the IANA Special Purpose Registries via a bi-monthly auto-sync. This protects against future RFCs adding new transition forms without requiring further mailpit maintenance.

## References

- Original advisory: [GHSA-mpf7-p9x7-96r3 / CVE-2026-27808](https://github.com/axllent/mailpit/security/advisories/GHSA-mpf7-p9x7-96r3)
- Vulnerable function: [`internal/tools/net.go#L25-L34` — `IsInternalIP`](https://github.com/axllent/mailpit/blob/a68499fa4e8874d414921fbd520e181dc92a39d7/internal/tools/net.go#L25-L34)
- Caller: [`internal/linkcheck/status.go#L140-L163` — `safeDialContext`](https://github.com/axllent/mailpit/blob/a68499fa4e8874d414921fbd520e181dc92a39d7/internal/linkcheck/status.go#L140-L163)
- Upstream Go-stdlib issue tracking the root cause: [**golang/go#79925**](https://github.com/golang/go/issues/79925) — proposal to extend `net.IP.IsPrivate` semantics and improve documentation
- Related: same bypass class in other Go projects — [GHSA-56c3-vfp2-5qqj / CVE-2026-44430](https://advisories.gitlab.com/golang/github.com/modelcontextprotocol/registry/CVE-2026-44430/), [GHSA-86m8-88fq-xfxp / CVE-2026-45741](https://advisories.gitlab.com/golang/github.com/gotenberg/gotenberg/v8/CVE-2026-45741/)
- Go stdlib design context: [Damien Neil's comment](https://github.com/golang/go/issues/76067#issuecomment-3506705688) ("`IsPrivate` was a mistake. Just about every use of it that I've seen seems to misuse it.")
- Python stdlib reference: [`ipaddress.is_private` 3.13 docs](https://docs.python.org/3/library/ipaddress.html) — covers 6to4, NAT64 explicitly
- Comprehensive Go library: [`code.dny.dev/ssrf`](https://pkg.go.dev/code.dny.dev/ssrf) — IANA-registry-driven
- RFCs: 3056 (6to4), 4380 (Teredo), 6052 (NAT64), 8215 (NAT64 local-use), 4291 (IPv6 addressing including IPv4-mapped/compatible), 5214 (ISATAP), 3879 (site-local deprecation), 3849 (documentation prefix)

## References
- https://github.com/axllent/mailpit/security/advisories/GHSA-w4mc-hhc6-xp28
- https://github.com/axllent/mailpit
