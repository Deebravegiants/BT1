### Title
Unbounded blocking read after WebSocket upgrade allows connection-slot and goroutine exhaustion in Gateway handshake - (File: `core/services/gateway/network/wsserver.go`)

### Summary
The CVE describes QEMU's `io/channel-websock.c` leaking memory when a remote attacker triggers slow data-channel reads that are never completed. The Chainlink Gateway websocket server has an analogous pattern in `webSocketServer.handleRequest`: once the HTTP-to-WebSocket upgrade succeeds, the code calls `conn.ReadMessage()` to read the second handshake message with **no read deadline set on the raw connection**, allowing an unprivileged, unauthenticated-yet-upgraded client to stall this read indefinitely.

### Finding Description
In `core/services/gateway/network/wsserver.go`:
- `handleRequest` first validates the auth header and calls `s.acceptor.StartHandshake(authBytes)`, which allocates a `connAttempt` entry in `connectionManager.connAttempts` (`core/services/gateway/connectionmanager.go:47-49,82-87`).
- It then upgrades the HTTP connection to a WebSocket (`s.upgrader.Upgrade`, `wsserver.go:134`). The `websocket.Upgrader.HandshakeTimeout` only bounds the upgrade handshake itself; once `Upgrade` returns, the connection is hijacked out of `net/http`'s control, so the `http.Server`'s `ReadTimeout`/`ReadHeaderTimeout` (set at `wsserver.go:93-94`) no longer apply to this connection.
- The code then calls `conn.SetReadLimit(...)` (byte-size cap) but **never calls `conn.SetReadDeadline(...)`** before `msgType, response, err := conn.ReadMessage()` at `wsserver.go:150-151`.
- If a client completes the upgrade (sending a valid, base64-decodable auth header that also passes `StartHandshake`) but never sends the second binary handshake message, `conn.ReadMessage()` blocks forever. The goroutine handling this HTTP request (one per accepted TCP connection in Go's `net/http`) is never released, and the corresponding `connAttempt` entry created by `StartHandshake` is never cleared by `AbortHandshake`, since that only runs on the error paths that this stalled read never reaches.
- Repeating this from many connections leaks goroutines and grows `connAttempts` unboundedly (no map eviction/timeout mechanism was found for stale attempts), mirroring the "slow data-channel read causing memory leak" bug class of CVE-2017-15268.

### Impact Explanation
An unprivileged client (any actor able to reach the Gateway's public WebSocket endpoint and produce a syntactically valid auth header, without needing valid node credentials, since `StartHandshake` failing only rejects malformed/unauthorized headers *before* the leak point — the leak occurs after `StartHandshake` succeeds but before `FinalizeHandshake`) can hold a TCP connection open indefinitely post-upgrade. This consumes one goroutine and one `connAttempts` map entry per stalled connection, and by opening many such connections, could exhaust file descriptors, goroutines, and memory on the Gateway node, resulting in denial of service for legitimate node connections — a direct availability impact analogous to the QEMU CVE.

### Likelihood Explanation
Likelihood is moderate-to-high for actors that can pass `StartHandshake` (which only validates header format/timestamp/DON id per `handshake.go`, not full challenge-response authentication — the actual identity proof happens in the *second* message that this bug lets an attacker never send). No rate limiting or per-IP connection cap is visible in the reviewed `wsserver.go`/`connectionmanager.go` code guarding this specific post-upgrade read path, and repeating the upgrade from many source connections is straightforward for a network-reachable client.

### Recommendation
Set an explicit read deadline on the connection immediately after upgrade and before calling `conn.ReadMessage()` for the handshake-response message, e.g. `conn.SetReadDeadline(time.Now().Add(time.Duration(s.config.HandshakeTimeoutMillis) * time.Millisecond))`, and ensure `s.acceptor.AbortHandshake(attemptID)` is invoked (via `defer`/timeout) so a stalled client cannot hold a `connAttempts` entry or goroutine indefinitely. Additionally, add TTL-based eviction for `connAttempts` as defense-in-depth.

### Proof of Concept
1. Client sends an HTTP GET to the Gateway WS path with a well-formed (but otherwise attacker-controlled) `WsServerHandshakeAuthHeaderName` header that satisfies `StartHandshake`'s decoding/validation in `handshake.go` (e.g. correctly formatted timestamp/DonID/GatewayID + valid-looking signature bytes, or by targeting a codepath where `StartHandshake` succeeds).
2. Complete the WebSocket upgrade handshake normally (`wsserver.go:134`).
3. After upgrade, do not send any further WebSocket message (or send it extremely slowly, e.g. a few bytes then stall) — never provide the binary handshake response.
4. Observe that `conn.ReadMessage()` at `wsserver.go:151` blocks indefinitely (no deadline enforced), the request-handling goroutine never returns, and `s.acceptor.AbortHandshake` is never called, leaving the `connAttempt` entry live in `connectionManager.connAttempts` for the lifetime of the idle connection.
5. Repeat across many connections to observe cumulative goroutine and map growth on the Gateway process. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** core/services/gateway/network/wsserver.go (L89-96)
```go
	server.server = &http.Server{
		Addr:              fmt.Sprintf("%s:%d", config.Host, config.Port),
		Handler:           mux,
		BaseContext:       func(net.Listener) context.Context { return baseCtx },
		ReadTimeout:       time.Duration(config.ReadTimeoutMillis) * time.Millisecond,
		ReadHeaderTimeout: time.Duration(config.ReadTimeoutMillis) * time.Millisecond,
		WriteTimeout:      time.Duration(config.WriteTimeoutMillis) * time.Millisecond,
	}
```

**File:** core/services/gateway/network/wsserver.go (L111-165)
```go
func (s *webSocketServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	authHeader := r.Header.Get(WsServerHandshakeAuthHeaderName)
	if len(authHeader) > HandshakeEncodedAuthHeaderMaxLen {
		s.lggr.Debugw("received auth header is too large", "len", len(authHeader))
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	authBytes, err := base64.StdEncoding.DecodeString(authHeader)
	if err != nil {
		s.lggr.Debugw("received auth header can't be base64-decoded", "err", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	attemptID, challenge, err := s.acceptor.StartHandshake(authBytes)
	if err != nil {
		s.lggr.Debugw("received invalid auth header", "err", err)
		w.WriteHeader(http.StatusUnauthorized)
		return
	}

	challengeStr := base64.StdEncoding.EncodeToString(challenge)
	hdr := make(http.Header)
	hdr.Add(WsServerHandshakeChallengeHeaderName, challengeStr)
	conn, err := s.upgrader.Upgrade(w, r, hdr)
	if err != nil {
		s.lggr.Errorw("failed websocket upgrade", "err", err)
		if conn != nil {
			conn.Close()
		}
		s.acceptor.AbortHandshake(attemptID)
		return
	}

	maxRequestBytes, err := s.config.MaxRequestBytesLimiter.Limit(r.Context())
	if err != nil {
		s.lggr.Errorw("failed to get request size limit", "err", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	conn.SetReadLimit(int64(maxRequestBytes))
	msgType, response, err := conn.ReadMessage()
	if err != nil || msgType != websocket.BinaryMessage {
		s.lggr.Errorw("invalid handshake message", "msgType", msgType, "err", err, "remoteAddr", conn.RemoteAddr())
		conn.Close()
		s.acceptor.AbortHandshake(attemptID)
		return
	}

	if err = s.acceptor.FinalizeHandshake(attemptID, response, conn); err != nil {
		s.lggr.Errorw("unable to finalize handshake", "err", err)
		conn.Close()
		s.acceptor.AbortHandshake(attemptID)
		return
	}
}
```

**File:** core/services/gateway/connectionmanager.go (L40-52)
```go
type connectionManager struct {
	services.StateMachine

	config             *config.ConnectionManagerConfig
	dons               map[string]*donConnectionManager
	wsServer           network.WebSocketServer
	clock              clockwork.Clock
	connAttempts       map[string]*connAttempt
	connAttemptCounter uint64
	connAttemptsMu     sync.Mutex
	gMetrics           *monitoring.GatewayMetrics
	lggr               logger.Logger
}
```

**File:** core/services/gateway/connectionmanager.go (L81-87)
```go
// immutable
type connAttempt struct {
	nodeState   *nodeState
	nodeAddress string
	challenge   network.ChallengeElems
	timestamp   uint32
}
```

**File:** core/services/gateway/network/handshake.go (L33-42)
```go
type ConnectionAcceptor interface {
	// Verify auth header, save state of the attempt and generate a challenge for the node.
	StartHandshake(authHeader []byte) (attemptID string, challenge []byte, err error)

	// Verify signed challenge and update connection, if successful.
	FinalizeHandshake(attemptID string, response []byte, conn *websocket.Conn) error

	// Clear attempt's state.
	AbortHandshake(attemptID string)
}
```
