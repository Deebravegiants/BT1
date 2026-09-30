# [H] klever-go: REST API slow-header connection exhaustion via Gin Engine.Run

## Summary
Severity: High
Advisory: GHSA-w4c6-7r69-w7j9
CVE: CVE-2026-52880
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-w4c6-7r69-w7j9
Type: github-advisory

## Affected
- Go: `github.com/klever-io/klever-go` — affected >=1.7.14 <1.7.18

## Details
### Summary

The Klever seednode REST API starts a Gin engine with `Engine.Run(restAPIInterface)`. In Gin v1.9.1, `Engine.Run` calls Go's default `http.ListenAndServe`, which constructs an HTTP server without application-level `ReadHeaderTimeout`, `ReadTimeout`, or `MaxHeaderBytes` limits.

An unauthenticated client that can reach a REST listener bound with Klever's documented `--rest-api-interface :8080` all-interface option can hold incomplete HTTP headers open indefinitely. In a local proof against the real `cmd/seednode/api.Start` path on `v1.7.17`, 120 slow-header connections caused 20/20 legitimate `/log` probes to fail with `accept: too many open files`. A fixed control using the same Gin router behind an explicit `http.Server` with `ReadHeaderTimeout`, `ReadTimeout`, and `MaxHeaderBytes` retained 0 slow connections and served 20/20 probes.

This report is distinct from the P2P advisories and from my direct-message goroutine report. This finding concerns Klever-owned HTTP REST startup code (`cmd/seednode/api` and `network/api`) using Gin `Engine.Run` without server-level header deadlines. It does not depend on `MultiDataInterceptor`, `Batch.Decompress`, libp2p, malformed P2P messages, or direct-message goroutine spawning.

### Details

Seednode REST API, latest release `v1.7.17`:

- `cmd/seednode/api/api.go:17` defines `Start(restAPIInterface, marshalizer)`.
- `cmd/seednode/api/api.go:18` creates `ws := gin.Default()`.
- `cmd/seednode/api/api.go:23` returns `ws.Run(restAPIInterface)`.
- `cmd/seednode/CLI.md:23` documents `--rest-api-interface`; it says `:8080` binds all interfaces and `off` disables the API.

Node REST API, latest release `v1.7.17`:

- `network/api/api.go:79` creates `ws = gin.Default()`.
- `network/api/api.go:98` returns `ws.Run(kleverFacade.RestAPIInterface())`.
- `cmd/node/main.go:147-150` documents the same `--rest-api-interface` flag and says `:8080` binds all interfaces.
- `docker/README.md:56-61` and `docker/README.md:67-70` publish host port `8080` for full-node and validator Docker examples.
- `README.md:264-268` documents that the node exposes a REST API for blockchain queries and operations.

The seednode REST API source is byte-identical across `v1.7.14` through `v1.7.17`; the captured runtime PoC was executed on `v1.7.17`.

Current `develop` commit `10bcfd50` remains affected:

- `network/api/api.go:98` still returns `ws.Run(kleverFacade.RestAPIInterface())`.
- `cmd/seednode/api/api.go:59` still returns `ws.Run(restAPIInterface)`.

Gin v1.9.1 implements `Engine.Run` as:

```go
func (engine *Engine) Run(addr ...string) (err error) {
    address := resolveAddress(addr)
    err = http.ListenAndServe(address, engine.Handler())
    return
}
```

In my source sweep, I did not find a production `http.Server{ReadHeaderTimeout: ...}` wrapper for either REST start path. The only `ReadHeaderTimeout` hit I found in the repository was a test helper under `network/api/websocket/routes_test.go`.

### PoC

GitHub Private Vulnerability Reporting does not appear to allow file attachments in this form, so I am including the reproduction command and captured output inline. I can paste the full 254-line Go test patch in a reply immediately if useful.

The test starts two local child servers:

1. Vulnerable: the real `cmd/seednode/api.Start` path.
2. Fixed control: the same Gin router served through `http.Server{ReadHeaderTimeout: 250ms, ReadTimeout: 250ms, MaxHeaderBytes: 4096}`.

Reproduction from a clean checkout:

```bash
git clone https://github.com/klever-io/klever-go
cd klever-go
git checkout v1.7.17

# Apply the PoC patch to cmd/seednode/api.
# I can provide the full patch in this advisory thread.

go test ./cmd/seednode/api -run TestPoC_SeednodeAPISlowlorisDifferential -count=1 -v -timeout 60s
```

Captured output on `v1.7.17`:

```text
POC_RESULT mode=vulnerable slow_connections_opened=120 slow_connections_still_open=111 legitimate_probe_ok=0 legitimate_probe_fail=20
POC_RESULT mode=fixed slow_connections_opened=120 slow_connections_still_open=0 legitimate_probe_ok=20 legitimate_probe_fail=0
```

The vulnerable server also logs repeated accept failures:

```text
http: Accept error: accept tcp 127.0.0.1:56415: accept: too many open files; retrying in 1s
```

### Impact

For an externally reachable Klever REST listener, a single unauthenticated client can retain many server-side connections by never completing HTTP headers. Because the Go server has no read-header deadline, those connections persist until the client closes them or an external proxy/firewall intervenes.

The direct result is REST API unavailability for legitimate clients. The local proof demonstrates this as 0/20 legitimate `/log` probes succeeding while the vulnerable server is saturated, versus 20/20 succeeding with the fixed server wrapper.

I am not claiming default public internet exposure. The default bind is `localhost:8080`. The affected condition is a REST API listener exposed through Klever's documented all-interface bind or Docker port-publish deployment shape.

This maps to the `SECURITY.md` High category: "Denial of Service affecting network availability." If Klever treats externally reachable REST API unavailability as non-critical because the default bind is localhost, the conservative classification is Medium under "Performance degradation attacks" / "Non-critical DoS vectors."

All testing was local loopback only. I did not contact Klever mainnet, public testnet, hosted RPCs, explorers, or third-party production infrastructure.

Suggested fix:

Start both REST APIs through explicit `http.Server` values instead of `Engine.Run`, for example:

```go
srv := &http.Server{
    Addr:              restAPIInterface,
    Handler:           ws.Handler(),
    ReadHeaderTimeout: 5 * time.Second,
    ReadTimeout:       10 * time.Second,
    WriteTimeout:      30 * time.Second,
    IdleTimeout:       120 * time.Second,
    MaxHeaderBytes:    32 << 10,
}
return srv.ListenAndServe()
```

Apply the same pattern to:

- `cmd/seednode/api.Start`
- `network/api.Start`

If Klever expects deployments to expose the REST API through a reverse proxy, I still recommend setting server-level limits in the application. That keeps the binary safe when operators use the documented direct bind or Docker port-publish path.

## References
- https://github.com/klever-io/klever-go/security/advisories/GHSA-w4c6-7r69-w7j9
- https://github.com/klever-io/klever-go
- https://github.com/klever-io/klever-go/releases/tag/v1.7.18
