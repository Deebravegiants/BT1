# [H] Traefik: Cross-user response poisoning via proxied CONNECT on Traefik's shared backend keep-alive pool

## Summary
Severity: High
Advisory: GHSA-3ccp-42pg-hgv6
CVE: CVE-2026-71324
CWE: CWE-444
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-3ccp-42pg-hgv6
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.53
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.24
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0 <3.7.9
- Go: `github.com/traefik/traefik` — affected >=0

## Details
## Summary

There is a critical vulnerability in Traefik's default HTTP reverse proxy that leads to unauthenticated cross-user response poisoning. When a client opens an HTTP/2 or HTTP/3 `CONNECT` request, Traefik forwards it — body included — to an HTTP/1.1 upstream over a shared `net/http.Transport`. If the upstream answers the CONNECT with a keep-alive non-2xx response without draining the body, the now-desynchronized backend socket is returned to Traefik's shared connection pool and reused for other clients, letting an attacker make a different client read a response the attacker smuggled — which may be another user's authenticated or private content. The entrypoint's `sanitizePath` option (default `true`) is not a reliable defense: backends that answer `CONNECT /` with a keep-alive non-2xx remain exploitable. The experimental FastProxy implementation was not affected. The issue is fixed by deferring the forwarded CONNECT payload until the backend accepts the tunnel, by not returning CONNECT connections to the shared idle pool, and by discarding the CONNECT body in the ForwardAuth path.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.53
- https://github.com/traefik/traefik/releases/tag/v3.6.24
- https://github.com/traefik/traefik/releases/tag/v3.7.9

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

## Summary

Traefik's default reverse proxy forwards a plain HTTP/2 or HTTP/3 `CONNECT` request and its body to
an HTTP/1.1 upstream through a shared `net/http.Transport`. When the upstream answers the CONNECT
with a keep-alive non-2xx response and does not drain the body, Traefik returns the now
desynchronized backend socket to its shared pool and reuses it for other clients. An
unauthenticated attacker uses this to make a different client read the attacker's smuggled response.

Traefik's default proxy is `net/http/httputil.ReverseProxy` over a shared `http.Transport`, so it
inherits the same root cause as the Caddy `reverse_proxy` CONNECT pool poisoning.

Traefik ships one partial mitigation Caddy does not. The entrypoint option `sanitizePath` (default
`true`) rewrites the forwarded CONNECT's empty path to `/`, so Traefik emits `CONNECT /` instead of
authority-form `CONNECT host:port`. This is not a reliable defense. It avoids the smuggle only
against backends that reject `CONNECT /` by closing the connection (Apache, nginx). Backends that
answer `CONNECT /` with a keep-alive non-2xx and leave the body undrained still cross. That set
includes any Go `net/http` server and gunicorn/Flask.

Confirmed on the official image `traefik:v3.6.23` (a currently supported release), default
configuration, against stock `go-httpbin` (Go) and `kennethreitz/httpbin` (Python gunicorn/Flask),
attacker and victim in separate containers, over both HTTP/2 and HTTP/3.

## Affected

- `traefik:v3.6.23` (official image) and current v3, default configuration, standard proxy to an
  HTTP/1.1 upstream. Backend keep-alive pooling is on by default (`MaxIdleConnsPerHost` 200).
- Attacker frontend is HTTP/2 or HTTP/3. An HTTP/1.1 frontend is not affected.
- The upstream keeps the connection alive after a non-2xx to the forwarded CONNECT and does not
  drain the body.
- The experimental FastProxy implementation is not affected (see Not affected).

## Details

Three behaviors compose.

1. Traefik forwards a plain CONNECT as an ordinary proxied request. The default proxy is
   `httputil.ReverseProxy` with a shared `http.Transport` (`pkg/proxy/httputil/proxy.go`). The
   director assigns the outbound `URL.Host` directly and does not reject CONNECT, leaving the
   request body a live stream. The client places a raw HTTP/1.1 request in that body (H2/H3 DATA
   frames), which is written onto the backend socket after the CONNECT header block.

2. `net/http` writes the CONNECT body unframed and pools the socket. For a CONNECT the transport
   writes the body with no `Content-Length` and no `Transfer-Encoding`. The upstream answers a
   keep-alive non-2xx and parses the trailing bytes as a pipelined request. Go reads the non-2xx
   response and returns the socket to the shared idle pool once the request body reaches EOF (the
   `wroteRequest` gate), while the smuggled request's response is still pending.

3. Desynchronized reuse. The smuggled request targets a slow endpoint so its response arrives after
   the socket is pooled. A different client that reuses the socket reads the pending smuggled
   response as its own.

`sanitizePath` (default `true`, `pkg/server/server_entrypoint_tcp.go`) calls `req.URL.JoinPath()`,
which turns the CONNECT's empty path into `/`. Traefik emits `CONNECT /`. Whether that stops the
smuggle depends only on the backend: Apache and nginx answer `400 Bad Request` with
`Connection: close` (socket torn down, no cross); Go `net/http` and gunicorn/Flask answer a
keep-alive non-2xx and pipeline the trailing bytes (cross). With `sanitizePath` off, Traefik emits
authority-form `CONNECT host:port`, which Apache answers with a keep-alive `405`.

HTTP/2 and HTTP/3 only. Pooling requires the forwarded request body to reach EOF. An H2/H3 client
half-closes the CONNECT stream (END_STREAM), so the body reaches EOF while the connection stays open
and the socket is pooled. An H1 CONNECT body is the tunnel and cannot reach EOF without closing the
connection, so the socket is closed, not pooled. HTTP/3 routes to the same handler chain as HTTPS.

## Backend behavior

"Armed" means the backend answers with a keep-alive non-2xx and parses the trailing undrained bytes
as a pipelined request. Default Traefik emits `CONNECT /`; with `sanitizePath: false` it emits
authority-form `CONNECT host:port`.

| Backend (stock image)   | Server         | `CONNECT /` (default)      | authority-form CONNECT |
|-------------------------|----------------|----------------------------|------------------------|
| `mccutchen/go-httpbin`  | Go net/http    | armed (405 keep-alive)     | armed                  |
| `traefik/whoami`        | Go net/http    | armed (200 keep-alive)     | armed                  |
| `caddy:2`               | Go net/http    | armed (405 keep-alive)     | armed                  |
| `kennethreitz/httpbin`  | gunicorn/Flask | armed (405 keep-alive)     | armed                  |
| `httpd:2.4`             | Apache         | not armed (400 close)      | armed (405 keep-alive) |
| `nginx:alpine`          | nginx          | not armed (400 close)      | not armed (400 close)  |
| `tomcat:10`             | Tomcat         | not armed (501 close)      | -                      |
| node `http`             | Node.js        | not armed (closes)         | -                      |
| `python -m http.server` | Python stdlib  | not armed (501 close)      | -                      |

## Impact

Unauthenticated cross-user HTTP response poisoning. One client receives another client's response,
which can be authenticated or private content, or an attacker-chosen response.

Blast radius depends on the pool. With the default pool and a slow smuggled endpoint the crossing is
reliable for a converging victim. With a bounded pool one desync shifts the whole response queue:
measured with `MaxIdleConnsPerHost 1` and a slow victim endpoint, 8 of 8 sequential victims read a
response that was not their own (1 the attacker's, 7 another user's, 0 their own). Traefik does not
expose `MaxConnsPerHost`, so the parallel cascade is weaker than Caddy's.

## Proof of concept

`poc/run.sh` runs the official `traefik:v3.6.23` image fronting real off-the-shelf backends over
HTTP/1.1, with attacker and victim in separate containers. Requires docker and python3. It builds
the attack client, pulls the stock images, and runs the scenarios below.

The attacker opens an H2 or H3 `CONNECT` to Traefik and sends a raw HTTP/1.1
`GET /delay/2?tag=ATTACKERSMUGGLED` as the CONNECT body, then half-closes the stream. Traefik
forwards the CONNECT to the Go/Python backend, the backend answers a keep-alive non-2xx, keeps the
socket, and parses the trailing GET as a pipelined request, so a response to it is queued on that
socket. `net/http` returns the socket to Traefik's shared pool. The victim then sends
`GET /get?tag=VICTIMOWN` on its own connection, Traefik reuses the pooled backend socket, and the
victim reads the queued `/delay` response instead of its own. `CROSS` means the victim received a
response that was not its own.

## Expected output from poc

```
== core: DEFAULT config, cross-user poisoning vs real off-the-shelf backends ==
  [core-go-h2] h2->h2 CROSS
  [core-go-h3] h3->h3 CROSS
  [core-go-x] h2->h3 CROSS
  [core-py-h2] h2->h2 CROSS
  [core-py-h3] h3->h3 CROSS
== mechanism: sanitizePath off -> stock Apache 405 (the direct Caddy analogue) ==
  [mech-ap-h2] h2->h2 CROSS
  [mech-ap-h3] h3->h3 CROSS
== controls: must NOT cross ==
  [ctl-apache] h2->h2 NO_CROSS
  [ctl-pooloff] h2->h2 NO_CROSS
  [ctl-kaoff] h2->h2 NO_CROSS
== safe variant: experimental FastProxy chunk-frames the CONNECT body ==
  [safe-fast] h2->h2 NO_CROSS
== cascade: bounded pool, one desync poisons a queue of victims ==
  smuggled=1 other_user=7 own=0 of 8 (cross-user poisoned=8)
RESULT: PASS
```

- Core rows. DEFAULT Traefik config against a Go backend (`go-httpbin`) and a Python gunicorn/Flask
  backend (`kennethreitz/httpbin`), for H2->H2, H3->H3, and H2->H3. The victim reads the attacker's
  smuggled response.
- Mechanism rows. `sanitizePath` off and stock Apache. Traefik emits authority-form
  `CONNECT apache-backend:80`, Apache answers a keep-alive `405`, and it crosses. This is the direct
  Caddy analogue and proves the full mechanism including Apache.
- Control rows. `ctl-apache` runs the default config against Apache, which closes `CONNECT /`;
  `ctl-pooloff` disables Traefik backend reuse (`maxIdleConnsPerHost: -1`); `ctl-kaoff` runs Apache
  with `KeepAlive Off`. All three print `NO_CROSS`, so the crossing depends on backend socket reuse,
  not pipelining or a shared client.
- Safe variant. Experimental FastProxy against the Go backend prints `NO_CROSS` because it
  chunk-frames the CONNECT body.
- Cascade. `MaxIdleConnsPerHost 1` and a slow victim endpoint. One CONNECT desync shifts the queue:
  of 8 sequential victims, 1 reads the attacker's smuggled response, 7 read another user's response,
  0 read their own.

The captured crossing (`poc/evidence/RELEASE_v3.6.23_victim.json`): the victim sent
`GET /get?tag=VICTIM_OWN` and received a 200 whose body is the response to
`GET /delay/2?tag=ATTACKER_SMUGGLED` with the echoed header `X-Smuggled: released-v3.6.23`, none of
which the victim sent.

## Not affected

- HTTP/1.1 frontend. An H1 CONNECT body cannot reach EOF without closing the connection, so the
  backend socket is not pooled.
- Experimental FastProxy (`experimental.fastProxy`). It chunk-frames the forwarded CONNECT body
  (`Transfer-Encoding: chunked`, captured in `poc/evidence/wire_fastproxy_chunked.txt`), so the
  trailing bytes are read as the CONNECT body, not a pipelined request. `safe-fast` is `NO_CROSS`.

## ForwardAuth

The ForwardAuth middleware with `forwardBody: true` and `preserveRequestMethod: true` re-issues the
request to the auth server as a CONNECT with the buffered body re-attached and `ContentLength` never
set (`pkg/middlewares/auth/forward.go`). The auth client writes that body unframed to the auth
server (captured on the wire), so a keep-alive non-2xx from the auth server poisons the shared
auth-client pool the same way.

## Root cause

`net/http` pools a connection after a keep-alive non-2xx response to a CONNECT whose body it wrote
unframed. Traefik's default proxy forwards client CONNECT through a shared `net/http.Transport` and
applies no CONNECT rejection. `sanitizePath` changes the emitted request target but does not remove
the defect. Traefik's own FastProxy implementation frames the CONNECT body and does not cross, which
shows this is a property of the httputil/`net/http` path, not fixed by path normalization.

## POC

[poc.zip](https://github.com/user-attachments/files/29963125/poc.zip)

</details>

---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-3ccp-42pg-hgv6
- https://github.com/traefik/traefik/pull/13542
- https://github.com/traefik/traefik/pull/13543
- https://github.com/traefik/traefik/pull/13556
- https://github.com/traefik/traefik/commit/04d36f28e4eae7535e96a6351dd9f7bfb48a30e7
- https://github.com/traefik/traefik/commit/0807b6d5dd1da8b2f7f4076ea2392b5437bf2ab0
- https://github.com/traefik/traefik/commit/94a7508817d180f0ab2f1eae93df48d4ab19ecce
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.53
- https://github.com/traefik/traefik/releases/tag/v3.6.24
- https://github.com/traefik/traefik/releases/tag/v3.7.9
