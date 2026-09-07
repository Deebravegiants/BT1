# [M] Nezha Monitoring: Unbounded WebSocket Streams — Resource Exhaustion DoS

## Summary
Severity: Medium
Advisory: GHSA-jg62-j5h6-8mpq
CVE: CVE-2026-53522
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-jg62-j5h6-8mpq
Type: github-advisory

## Affected
- Go: `github.com/nezhahq/nezha` — affected >=1.0.0 <2.2.0

## Details
## 1. Description

The Nezha dashboard exposes two endpoints that create long-lived WebSocket streams to monitored agents:

- `POST /api/v1/terminal` → `createTerminal()` (terminal.go:27-67)
- `POST /api/v1/file` → `createFM()` (fm.go:28-67)

Both call `rpc.NezhaHandlerSingleton.CreateStream(streamId, ...)` which inserts a new `ioStreamContext` into an **unbounded** `map[string]*ioStreamContext` (`s.ioStreams` in `io_stream.go:59-67`). There is **no per-user rate limit, no global semaphore, and no per-server connection cap**. Each stream allocates:

1. A `ioStreamContext` struct with several channels and sync primitives
2. Two goroutines via `StartStream()` (io_stream.go:358-369) — bidirectional `io.CopyBuffer`
3. A gRPC IOStream between the dashboard and the agent
4. An agent-side PTY/shell process

**Vulnerable code:**

`terminal.go:27-67` — `createTerminal`:
```go
func createTerminal(c *gin.Context) (*model.CreateTerminalResponse, error) {
    // ... validation ...
    rpc.NezhaHandlerSingleton.CreateStream(streamId, getUid(c), server.ID)
    // ... sends TaskTypeTerminalGRPC to agent ...
    return &model.CreateTerminalResponse{...}, nil
}
```

`fm.go:28-67` — `createFM`:
```go
func createFM(c *gin.Context) (*model.CreateFMResponse, error) {
    // ... validation ...
    rpc.NezhaHandlerSingleton.CreateStream(streamId, getUid(c), server.ID)
    // ... sends TaskTypeFM to agent ...
    return &model.CreateFMResponse{...}, nil
}
```

`io_stream.go:55-67` — `CreateStreamWithPurpose` (inserts into unbounded map):
```go
func (s *NezhaHandler) CreateStreamWithPurpose(...) {
    s.ioStreamMutex.Lock()
    defer s.ioStreamMutex.Unlock()
    s.ioStreams[streamId] = &ioStreamContext{
        creatorUserID:  creatorUserID,
        targetServerID: targetServerID,
        purpose:        purpose,
        userIoConnectCh:  make(chan struct{}),
        agentIoConnectCh: make(chan struct{}),
        revokedCh:        make(chan struct{}),
    }
}
```

`io_stream.go:319-372` — `StartStream` spawns two goroutines per stream:
```go
func (s *NezhaHandler) StartStream(streamId string, timeout time.Duration) error {
    // ...
    go func() {
        _, innerErr := io.CopyBuffer(userIo, agentIo, bp.buf)
        errCh <- innerErr
    }()
    go func() {
        _, innerErr := io.CopyBuffer(agentIo, userIo, bp.buf)
        errCh <- innerErr
    }()
    return <-errCh
}
```

The `NezhaHandler.ioStreams` map is initialized as a plain `make(map[string]*ioStreamContext)` in `nezha.go:36` — no capacity limit, no eviction policy beyond explicit `CloseStream` / `RevokeStreamsForServer`.

The `HasPermission` check at terminal.go:41-43 and fm.go:43-45 controls **access scope** but does **not** limit creation volume. A user with `ScopeServerExec` (terminal) or `ScopeServerRead+Write+Delete` (file manager) can open unlimited streams.

## 2. PoC

A conceptual attack (no Docker needed):

```
# As an authenticated user with a valid JWT or PAT:
for i in {1..1000}; do
  curl -X POST "https://dashboard.example.com/api/v1/terminal" \
    -H "Authorization: Bearer $JWT" \
    -H "Content-Type: application/json" \
    -d '{"server_id": 1}' &
done
wait
```

Each request:
- Creates a new stream entry in `ioStreams`
- Sends a `TaskTypeTerminalGRPC` task to the agent
- When the WebSocket attachment occurs (`GET /ws/terminal/{id}`), spawns 2 goroutines for I/O relay and allocates a 1 MB buffer per goroutine

The attack targets three resource domains:
1. **Dashboard memory/goroutines** — each stream adds goroutines, channels, and buffers
2. **Agent resources** — each stream spawns a PTY/shell process on the monitored server
3. **gRPC connection pool** — concurrent IOStreams consume gRPC multiplexing capacity

The `POST /file (createFM)` endpoint provides an alternative path with the same unbounded behavior, using `ScopeServerRead+Write+Delete` instead of `ScopeServerExec`.

## 3. Impact

- **Denial of Service against the dashboard**: memory exhaustion, goroutine starvation, or gRPC stream table overflow from rapid stream creation
- **Denial of Service against monitored agents**: each terminal session spawns a PTY process on the agent — an attacker can crash or degrade all agents behind the dashboard
- **Operational cascade**: if the dashboard OOMs, all agent monitoring and alerting is lost
- **PAT connection-registry bypass**: rapid create-connect-disconnect cycles may evade cleanup tracking

The attack requires only authenticated access with standard scopes — no special privileges. Any team member with terminal access to a server can DoS the entire infrastructure.

## 4. Remediation

Implement layered rate limiting and concurrency control:

1. **Per-user stream cap** in `CreateStream` — reject if the user already has N active streams (e.g., 10 per user):
   ```go
   func (s *NezhaHandler) CreateStreamWithPurpose(...) {
       s.ioStreamMutex.Lock()
       defer s.ioStreamMutex.Unlock()
       count := 0
       for _, ctx := range s.ioStreams {
           if ctx.creatorUserID == creatorUserID { count++ }
       }
       if count >= maxStreamsPerUser { return error }
       // ... existing code ...
   }
   ```

2. **Per-server semaphore** — limit concurrent streams to any single server (e.g., 20 per server)

3. **Rate limiter on `createTerminal` and `createFM`** — mirror the existing MCP rate limiter (`mcp_ratelimit.go`) for legacy WebSocket endpoints

4. **Add a configurable `MaxStreamsPerUser` / `MaxStreamsPerServer` setting** so operators can tune limits without code changes

## References
- https://github.com/nezhahq/nezha/security/advisories/GHSA-jg62-j5h6-8mpq
- https://nvd.nist.gov/vuln/detail/CVE-2026-53522
- https://github.com/nezhahq/nezha
