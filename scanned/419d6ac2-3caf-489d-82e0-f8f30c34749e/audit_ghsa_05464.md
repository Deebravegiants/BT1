# [M] Traefik's ACME TLS-ALPN fast path lacks timeouts and close on handshake stall

## Summary
Severity: Medium
Advisory: GHSA-cwjm-3f7h-9hwq
CVE: CVE-2026-22045
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-cwjm-3f7h-9hwq
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.7
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.35

## Details
## Impact

There is a potential vulnerability in Traefik ACME TLS certificates' automatic generation: the ACME TLS-ALPN fast path can allow unauthenticated clients to tie up goroutines and file descriptors indefinitely when the ACME TLS challenge is enabled.

A malicious client can open many connections, send a minimal ClientHello with `acme-tls/1`, then stop responding, leading to denial of service of the entrypoint.  

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.35
- https://github.com/traefik/traefik/releases/tag/v3.6.7

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

# \[Security\] ACME TLS-ALPN fast path lacks timeouts and close on handshake stall

Dear Traefik security team,

We believe we have identified a resource-exhaustion issue in the ACME TLS-ALPN fast path that can allow unauthenticated clients to tie up goroutines and file descriptors indefinitely when the ACME TLS challenge is enabled.

## Summary

- Affected code: `pkg/server/router/tcp/router.go` (ACME TLS-ALPN handling).  
- When a ClientHello advertises `acme-tls/1`, Traefik intercepts it and calls `tls.Server(...).Handshake()` without any read/write deadlines and without closing the connection afterward.  
- Immediately before this branch, existing deadlines set by the entrypoint are cleared.  
- A client that sends the ALPN marker and then stops responding can keep the goroutine and socket open indefinitely, potentially exhausting the entrypoint under load.  
- Exposure is limited to entrypoints where the ACME TLS-ALPN challenge is enabled and ACME bypass is not allowed.

## Relevant snippets
```143:171:pkg/server/router/tcp/router.go
// Deadlines are cleared before protocol dispatch
if err := conn.SetDeadline(time.Time{}); err != nil {
    log.Error().Err(err).Msg("Error while setting deadline")
}

// ACME TLS-ALPN fast path
if !r.acmeTLSPassthrough && slices.Contains(hello.protos, tlsalpn01.ACMETLS1Protocol) {
    r.acmeTLSALPNHandler().ServeTCP(r.GetConn(conn, hello.peeked))
    return
}
```

```224:226:pkg/server/router/tcp/router.go
// Handler invoked by the branch above
return tcp.HandlerFunc(func(conn tcp.WriteCloser) {
    _ = tls.Server(conn, r.httpsTLSConfig).Handshake()
})
```

## Impact

- Each stalled handshake consumes a goroutine and FD with no timeout and no server-side close.  
- A malicious client can open many connections, send a minimal ClientHello with `acme-tls/1`, then stop responding, leading to denial of service of the entrypoint.  
- Normal HTTPS handling uses `http.Server` timeouts; this bespoke path bypasses them.

## Conditions for exploitation

- ACME TLS-ALPN challenge enabled (default when configured).  
- `allowACMEByPass` disabled for the entrypoint (the default when ACME TLS challenge is handled by Traefik).

## CWE

- CWE-400: Uncontrolled Resource Consumption.

## Proposed fix (illustrative)

```
@@ func (r *Router) acmeTLSALPNHandler() tcp.Handler {
-    return tcp.HandlerFunc(func(conn tcp.WriteCloser) {
-        _ = tls.Server(conn, r.httpsTLSConfig).Handshake()
-    })
+    return tcp.HandlerFunc(func(conn tcp.WriteCloser) {
+        // Ensure the handshake cannot block indefinitely and always closes the socket.
+        _ = conn.SetReadDeadline(time.Now().Add(10 * time.Second))
+        _ = conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
+
+        tlsConn := tls.Server(conn, r.httpsTLSConfig)
+        _ = tlsConn.Handshake()
+        _ = tlsConn.Close() // close regardless of handshake outcome
+    })
 }
```

Alternatively, route ACME TLS-ALPN through the existing `tcp.TLSHandler`/HTTP server path so the configured timeouts and lifecycle management apply automatically.

## CVSS v3.1 (estimate)

- Vector: AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H  
- Base score: 7.5 (High)  
- Rationale: Network-only, no auth/user interaction required; impact is service availability via resource exhaustion; no confidentiality or integrity impact.

Please let us know if you would like a PoC or further details. We have not made any code changes in this report.

Let us know if you have any questions or need clarification\!

Best wishes,  
Pavel Kohout  
 Aisle Research  
</details>

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-cwjm-3f7h-9hwq
- https://nvd.nist.gov/vuln/detail/CVE-2026-22045
- https://github.com/traefik/traefik/commit/e9f3089e9045812bcf1b410a9d40568917b26c3d
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.35
- https://github.com/traefik/traefik/releases/tag/v3.6.7
