## Finding

Chainlink's gateway subsystem has the same missing message-size-limit bug class described in the KubeEdge advisory, but on the *node-side WebSocket client* rather than the gateway server. The gateway server correctly enforces a read limit; the client-side connector does not.

### Title
Unbounded WebSocket read in gateway connector client allows memory-exhaustion DoS on the connecting node - (File: `core/services/gateway/network/wsclient.go`)

### Summary
The node's `webSocketClient.Connect` dials out to a Gateway and hands the resulting `*websocket.Conn` to `wsConnectionWrapper.Reset`, whose `readPump` then calls `conn.ReadMessage()` in an unbounded loop for the lifetime of the connection, with no `SetReadLimit` ever having been called on that connection object.

### Finding Description
On the gateway (server) side, `webSocketServer.handleRequest` explicitly bounds the handshake read via `conn.SetReadLimit(int64(maxRequestBytes))` before calling `conn.ReadMessage()`, and because gorilla/websocket's read limit is sticky on the `*websocket.Conn`, this limit continues to protect every subsequent read performed later by `wsConnectionWrapper.readPump` after `FinalizeHandshake` hands the same conn to `Reset`. [1](#0-0) 

On the node (client) side, however, `webSocketClient.Connect` dials the connection and performs the handshake write/reads, but at no point calls `conn.SetReadLimit`. [2](#0-1) 

That unbounded conn is then passed straight into `gatewayState.conn.Reset(conn)` in the connector's `reconnectLoop`, which starts `wsConnectionWrapper.readPump` on it. [3](#0-2) 

`readPump` runs `conn.ReadMessage()` in a loop indefinitely, buffering the entire message into memory with no size ceiling, exactly the same missing-limit pattern flagged in GHSA-wrcr-x4qj-j543 for KubeEdge's CloudStream/EdgeStream readers. [4](#0-3) 

### Impact Explanation
A Gateway a node is configured to connect to (or an entity able to respond on that TCP/TLS stream as that Gateway) can send an arbitrarily large WebSocket frame/message to the node. Because gorilla/websocket enforces no default read limit, `ReadMessage` will buffer the entire message in memory, allowing memory exhaustion and denial of service of the node process — the same "authenticated-endpoint, unbounded read" class as the original advisory (CWE-400/CWE-770).

### Likelihood Explanation
Exploitation requires being (or successfully impersonating/compromising) one of the node's configured Gateway endpoints and having the connection reach the post-handshake read loop — this mirrors the advisory's own precondition that "only an authenticated user/endpoint can cause this issue." Given nodes are typically configured to connect to multiple Gateways (including ones operated by parties outside the node operator's direct control), and the vulnerable code path applies to every established gateway connection for the lifetime of the process, likelihood is moderate whenever `GatewayConnector` is enabled.

### Recommendation
Call `conn.SetReadLimit(<bound>)` on the client-side connection in `webSocketClient.Connect` before performing the handshake read/writes, mirroring the bound already applied in `webSocketServer.handleRequest`, and expose it via `WebSocketClientConfig` (analogous to `HTTPServerConfig.MaxRequestBytesLimiter`) so operators can tune it consistently with the server-side limiter.

### Proof of Concept
1. Stand up a fake "Gateway" WebSocket endpoint that completes the challenge/response handshake exactly as `webSocketClient.Connect` expects.
2. After handshake, have the fake Gateway send a single very large (e.g. multi-GB) WebSocket binary/text frame to the connected node.
3. Observe that `wsConnectionWrapper.readPump`'s `conn.ReadMessage()` call attempts to buffer the entire frame in memory (no `SetReadLimit` was ever set on this conn), driving the node process's memory usage up and potentially triggering OOM/DoS, in contrast to the bounded behavior on the gateway server side which would reject an oversized handshake message.

### Citations

**File:** core/services/gateway/network/wsserver.go (L144-151)
```go
	maxRequestBytes, err := s.config.MaxRequestBytesLimiter.Limit(r.Context())
	if err != nil {
		s.lggr.Errorw("failed to get request size limit", "err", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	conn.SetReadLimit(int64(maxRequestBytes))
	msgType, response, err := conn.ReadMessage()
```

**File:** core/services/gateway/network/wsclient.go (L41-88)
```go
func (c *webSocketClient) Connect(ctx context.Context, url *url.URL) (*websocket.Conn, error) {
	authHeader, err := c.initiator.NewAuthHeader(ctx, url)
	if err != nil {
		return nil, err
	}
	authHeaderStr := base64.StdEncoding.EncodeToString(authHeader)

	hdr := make(http.Header)
	hdr.Add(WsServerHandshakeAuthHeaderName, authHeaderStr)

	conn, resp, err := c.dialer.DialContext(ctx, url.String(), hdr)
	if err != nil {
		if resp != nil {
			_ = resp.Body.Close()
		}
		c.lggr.Errorf("WebSocketClient: couldn't connect to %s: %v", url.String(), err)
		c.tryCloseConn(conn)
		return nil, err
	}
	defer resp.Body.Close()

	challengeStr := resp.Header.Get(WsServerHandshakeChallengeHeaderName)
	if challengeStr == "" {
		c.lggr.Error("WebSocketClient: empty challenge")
		c.tryCloseConn(conn)
		return nil, err
	}
	challenge, err := base64.StdEncoding.DecodeString(challengeStr)
	if err != nil {
		c.lggr.Errorf("WebSocketClient: couldn't decode challenge: %s: %v", challengeStr, err)
		c.tryCloseConn(conn)
		return nil, err
	}

	response, err := c.initiator.ChallengeResponse(ctx, url, challenge)
	if err != nil {
		c.lggr.Errorw("WebSocketClient: couldn't generate challenge response", "err", err)
		c.tryCloseConn(conn)
		return nil, err
	}

	if err = conn.WriteMessage(websocket.BinaryMessage, response); err != nil {
		c.lggr.Errorw("WebSocketClient: couldn't send challenge response", "err", err)
		c.tryCloseConn(conn)
		return nil, err
	}
	return conn, nil
}
```

**File:** core/services/gateway/connector/connector.go (L301-325)
```go
func (c *gatewayConnector) reconnectLoop(gatewayState *gatewayState) {
	defer c.closeWait.Done()
	redialBackoff := utils.NewRedialBackoff()
	ctx, cancel := c.shutdownCh.NewCtx()
	defer cancel()

	for {
		conn, err := gatewayState.wsClient.Connect(ctx, gatewayState.url)
		if err != nil {
			c.lggr.Errorw("connection error", "url", gatewayState.url, "err", err)
		} else {
			c.lggr.Infow("connected successfully", "url", gatewayState.url)
			closeCh := gatewayState.conn.Reset(conn)
			gatewayState.signal()
			if closeCh != nil { // nil means already closed
				<-closeCh
			}
			c.lggr.Infow("connection closed", "url", gatewayState.url)

			// reset backoff
			redialBackoff = utils.NewRedialBackoff()

			// reset signal channel
			gatewayState.signalCh = make(chan struct{})
		}
```

**File:** core/services/gateway/network/wsconnection.go (L197-213)
```go
func (c *wsConnectionWrapper) readPump(conn *websocket.Conn, closeCh chan<- error) {
	defer c.wg.Done()
	for {
		msgType, data, err := conn.ReadMessage()
		if err != nil {
			c.lggr.Errorw("failed to read message, closing connection", "error", err)
			var closeErr error
			if c.conn.CompareAndSwap(conn, nil) {
				closeErr = conn.Close()
				if closeErr != nil {
					c.lggr.Errorw("error closing connection", "error", closeErr)
				}
			}
			closeCh <- closeErr
			close(closeCh)
			return
		}
```
