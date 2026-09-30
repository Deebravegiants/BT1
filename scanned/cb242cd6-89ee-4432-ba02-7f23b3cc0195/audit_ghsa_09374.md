# [H] Gotenberg has an SSRF deny-list bypass in IsPublicIP via IPv6 6to4 / NAT64 / site-local prefixes

## Summary
Severity: High
Advisory: GHSA-86m8-88fq-xfxp
CVE: CVE-2026-45741
CWE: CWE-184, CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-86m8-88fq-xfxp
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0

## Details
### Summary

`IsPublicIP` in `pkg/gotenberg/outbound.go` incorrectly classifies IPv6 6to4 / NAT64 / deprecated site-local addresses as public IPs, allowing an unauthenticated attacker to reach internal destinations (e.g., cloud metadata services at `169.254.169.254`) via a single crafted DNS AAAA record. This is a variant of CVE-2026-44430 (modelcontextprotocol/registry).

### Details

`IsPublicIP` uses Go stdlib helpers (`IsLoopback`, `IsPrivate`, `IsLinkLocalUnicast`, etc.) to block internal IPs. However, these helpers do not recognize IPv6 prefixes that embed IPv4 addresses:

| Prefix | RFC | Tunnels to |
|--------|-----|-----------|
| `2002::/16` | RFC 3056 (6to4) | IPv4 in bits 16-47 |
| `64:ff9b::/96` | RFC 6052 (NAT64 well-known) | IPv4 in low 32 bits |
| `64:ff9b:1::/48` | RFC 8215 (NAT64 local-use) | IPv4 in low 32 bits |
| `fec0::/10` | RFC 3879 (deprecated site-local) | internal routing |

`addr.Unmap()` only handles `::ffff:0:0/96` (IPv4-mapped) and has no effect on these prefixes. On dual-stack or NAT64-enabled cloud hosts, the OS kernel transparently routes these addresses to their embedded internal IPv4 destinations.

Vulnerable code (`pkg/gotenberg/outbound.go` L53-69, commit `93d0103`):

```go
func IsPublicIP(addr netip.Addr) bool {
    addr = addr.Unmap() // only handles ::ffff:x.x.x.x
    switch {
    case addr.IsLoopback(), addr.IsPrivate(),
         addr.IsLinkLocalUnicast(), ...:
        return false
    }
    return true // 6to4/NAT64/site-local incorrectly reaches here
}
```

### PoC
```
cd poc/
./build.sh   # docker build (~30s)
./run.sh     # docker run — exits with code 1 (bug detected)
```

Expected output: `IsPublicIP(2002:a9fe:a9fe::) = true` — the function returns true for 3 addresses that wrap 169.254.169.254 (AWS IMDS). Full test file available via GHSA private comment on request.

### Impact

An unauthenticated attacker controlling a DNS AAAA record can tunnel gotenberg's outbound HTTP client to AWS/GCP/Azure IMDS (169.254.169.254), leaking IAM credentials. The Chromium URL convert route returns the full response as a PDF (full-read SSRF). Affects all deployments with `WithDenyPrivateIPs(true)` on dual-stack or NAT64-enabled hosts.

### Suggested Fix

Add explicit prefix checks after `addr.Unmap()`:
```
var blockedIPv6Prefixes = []netip.Prefix{
    netip.MustParsePrefix("2002::/16"),
    netip.MustParsePrefix("64:ff9b::/96"),
    netip.MustParsePrefix("64:ff9b:1::/48"),
    netip.MustParsePrefix("fec0::/10"),
}
for _, p := range blockedIPv6Prefixes {
    if p.Contains(addr) { return false }
}
```

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-86m8-88fq-xfxp
- https://github.com/gotenberg/gotenberg
