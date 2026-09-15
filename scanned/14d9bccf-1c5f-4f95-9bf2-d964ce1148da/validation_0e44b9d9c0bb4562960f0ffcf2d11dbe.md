### Title
Silent authentication-handshake failure returns `(nil, nil)` on empty challenge - ([File: core/services/gateway/network/wsclient.go])

### Summary
`webSocketClient.Connect` (the client side of the Gateway node authentication handshake) fails to correctly propagate an error when the Gateway's handshake response is malformed, mirroring the CVE-2016-0772 StartTLS pattern of silently continuing after an unacknowledged negotiation step.

### Finding Description
`webSocketClient.Connect` in `core/services/gateway/network/wsclient.go` implements the client (`ConnectionInitiator`) side of the node↔Gateway handshake described in `core/services/gateway/network/handshake.go`. After dialing, it reads the `WsServerHandshakeChallengeHeaderName` header from the response: [1](#0-0) 

```go
conn, resp, err := c.dialer.DialContext(ctx, url.String(), hdr)
if err != nil {
    ...
    return nil, err
}
defer resp.Body.Close()

challengeStr := resp.Header.Get(WsServerHandshakeChallengeHeaderName)
if challengeStr == "" {
    c.lggr.Error("WebSocketClient: empty challenge")
    c.tryCloseConn(conn)
    return nil, err
}
```

At the point where `challengeStr == ""` is checked, `err` was already verified to be `nil` on the line above (`if err != nil { return nil, err }`). Therefore, when the Gateway (or a man-in-the-middle) omits/strips the challenge header, the function logs an error, closes the connection, but returns `nil, nil` — a `(conn, err)` pair that looks like a *successful* call with no connection, rather than propagating a concrete error. This is structurally identical to the reported `net/imap#starttls` bug: a security-relevant negotiation step (STARTTLS response / challenge header) is not acknowledged by the remote end, and the client code does not raise an exception/error for the caller to act on — it silently proceeds as if nothing failed.

### Impact Explanation
Any caller relying on the `error` return value of `Connect` to gate its authenticated-connection state machine (e.g., retry/backoff loops, readiness signaling, or state transitions keyed off `err == nil`) will not be able to distinguish "connected successfully" from "handshake stripped/failed", because both cases return a `nil` error. This creates the possibility of a MITM or misbehaving Gateway silently stripping the authentication challenge stage of the handshake without the node observing an error, undermining the integrity guarantees of the node↔Gateway mutual-authentication handshake (`StartHandshake`/`ChallengeResponse`/`FinalizeHandshake` in `handshake.go`).

### Likelihood Explanation
This requires the attacker to be positioned as, or impersonate, the Gateway endpoint (network position) — the same class of actor described in the CVE-2016-0772 report (MITM stripping a negotiation response). Within the stated scope, this falls in the "session/token/external-initiator handling" category of the node's Gateway connector rather than a purely malicious-peer/network-layer bug, since the defect is in the node's own error-handling logic, not merely in the wire protocol.

### Recommendation
Change the `nil` error return in the empty-challenge branch to a concrete, non-nil error (e.g., a sentinel `ErrEmptyChallenge`) so callers can never conflate a handshake failure with success:
```go
if challengeStr == "" {
    c.lggr.Error("WebSocketClient: empty challenge")
    c.tryCloseConn(conn)
    return nil, errors.New("empty challenge header in handshake response")
}
```
Additionally, audit all call sites of `webSocketClient.Connect` to ensure they treat `(nil conn, nil err)` defensively even if not fixed at the source.

### Proof of Concept
1. Stand up a WebSocket server that accepts the `WsServerHandshakeAuthHeaderName` request but responds to the upgrade without setting `WsServerHandshakeChallengeHeaderName` (simulating a MITM stripping the header, analogous to `striptls.py` in the original report).
2. Call `network.NewWebSocketClient(...).Connect(ctx, url)` against this server.
3. Observe that `Connect` returns `(nil, nil)` instead of a non-nil error, even though the handshake did not complete and the connection was closed — the caller cannot detect the failure via the standard `if err != nil` check.

**Note on completeness:** I was unable to fully trace, within the remaining tool budget, how every caller of `webSocketClient.Connect` (e.g., the connector's reconnect loop) handles a `(nil, nil)` return, so the exact operational consequence (e.g., whether it causes a crash, an infinite silent-retry loop, or is otherwise masked downstream) is not fully confirmed. The root-cause defect in `wsclient.go` is verified directly from source.

### Citations

**File:** core/services/gateway/network/wsclient.go (L51-67)
```go
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
```
