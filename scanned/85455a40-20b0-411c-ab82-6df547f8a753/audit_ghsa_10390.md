# [C] Dgraph: Unauthenticated Admin Token Disclosure Leading to Authentication Bypass via /debug/vars

## Summary
Severity: Critical
Advisory: GHSA-vvf7-6rmr-m29q
CVE: CVE-2026-41492
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-vvf7-6rmr-m29q
Type: github-advisory

## Affected
- Go: `github.com/dgraph-io/dgraph/v25` — affected >=0 <25.3.3
- Go: `github.com/dgraph-io/dgraph/v24` — affected >=0
- Go: `github.com/dgraph-io/dgraph` — affected >=0

## Details
### Summary
Dgraph `v25.3.2` still exposes the process command line through the unauthenticated `/debug/vars` endpoint on Alpha. Because the admin token is commonly supplied via the `--security "token=..."` startup flag, an unauthenticated attacker can retrieve that token and replay it in the `X-Dgraph-AuthToken` header to access admin-only endpoints.

This is a variant of the previously fixed `/debug/pprof/cmdline` issue, but the current fix is incomplete because it blocks only `/debug/pprof/cmdline` and still serves `http.DefaultServeMux`, which includes `expvar`'s `/debug/vars` handler.

### Details
Alpha still exposes Go's default HTTP mux:

- `x/metrics.go`
  - imports `expvar`
  - initializes `Conf = expvar.NewMap("dgraph_config")`
- Go's `expvar` package automatically registers `/debug/vars`
- `expvar` publishes:
  - `cmdline = os.Args`
  - `memstats = runtime.Memstats`

Alpha's HTTP handler explicitly blocks only the old CVE path:

- `dgraph/cmd/alpha/run.go`
  - checks `if r.URL.Path == "/debug/pprof/cmdline"` and returns `404`
  - otherwise falls through to `http.DefaultServeMux.ServeHTTP(w, r)`

Admin endpoints still trust the leaked token:

- `dgraph/cmd/alpha/admin.go`
  - reads `X-Dgraph-AuthToken`
  - compares it to `worker.Config.AuthToken`
### PoC
1. Send an unauthenticated request to Alpha:

```http
GET /debug/vars HTTP/1.1
Host: target:8080
```

2. Parse the JSON response and read the `cmdline` field.

3. Extract the admin token from the startup arguments, for example:

```text
--security token=debug-vars-secret;
```

4. Replay the token to an admin-only endpoint:

```http
GET /admin/config/cache_mb HTTP/1.1
Host: target:8080
X-Dgraph-AuthToken: debug-vars-secret
```

5. The request is accepted as an authorized admin request.

This was reproduced against `dgraph/dgraph:v25.3.2` in Docker.

Observed behavior:

- unauthenticated `/debug/vars` leaked the configured token
- replaying the leaked token in `X-Dgraph-AuthToken` successfully accessed `/admin/config/cache_mb`
- response body was:

```text
4096
```

It was verified that the old CVE path appears specifically patched in the same version:

- `/debug/pprof/cmdline` returned `404 Not Found`
- `/debug/pprof/` remained reachable

### Impact
Unauthenticated attackers can obtain the Alpha admin token and gain unauthorized administrative access.

This enables privileged admin operations such as:

- reading privileged admin configuration
- mutating admin configuration
- performing operational control actions gated by `X-Dgraph-AuthToken`

In deployments where the Alpha HTTP port is reachable by untrusted parties, this is a practical authentication bypass to admin functionality.

## References
- https://github.com/dgraph-io/dgraph/security/advisories/GHSA-vvf7-6rmr-m29q
- https://nvd.nist.gov/vuln/detail/CVE-2026-41492
- https://github.com/dgraph-io/dgraph
- https://github.com/dgraph-io/dgraph/releases/tag/v25.3.3
