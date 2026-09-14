No vulnerability found for this question.

The reported CVE affects `tungstenite`, a Rust crate not used anywhere in this codebase — the repository's WebSocket layer is built on `github.com/gorilla/websocket` (Go), a completely separate implementation. [1](#0-0) 

More importantly, the specific bug class from the advisory — unbounded/oversized HTTP header causing repeated expensive parsing during handshake — is already mitigated in the analogous chainlink code path. In `webSocketServer.handleRequest`, the auth header is length-checked against `HandshakeEncodedAuthHeaderMaxLen` (512 bytes) *before* any base64 decoding or parsing is attempted, and oversized headers are rejected immediately with `http.StatusBadRequest`: [2](#0-1) 

Additionally, the constants file caps all handshake field lengths (`HandshakeDonIDLen`, `HandshakeGatewayURLLen`, `HandshakeSignatureLen`, etc.) to fixed small sizes, and `UnpackSignedAuthHeader` rejects any payload that doesn't match the exact expected length rather than attempting variable-length parsing: [3](#0-2) [4](#0-3) 

The server also enforces `ReadHeaderTimeout`, `ReadTimeout`, and a configurable `HandshakeTimeoutMillis` on the underlying `http.Server` and `websocket.Upgrader`, further bounding the CPU/time a malicious client handshake can consume: [5](#0-4) 

This is a dependency-only bug in an unrelated Rust library, and the equivalent Go code path already has fixed-length/pre-decode bounds checks that prevent the excessive-parsing DoS pattern described in the advisory.

### Citations

**File:** core/services/gateway/network/wsserver.go (L1-13)
```go
package network

import (
	"context"
	"encoding/base64"
	"fmt"
	"net"
	"net/http"
	"time"

	"github.com/gorilla/websocket"

	"github.com/smartcontractkit/chainlink-common/pkg/logger"
```

**File:** core/services/gateway/network/wsserver.go (L66-97)
```go
func NewWebSocketServer(config *WebSocketServerConfig, acceptor ConnectionAcceptor, lggr logger.Logger, lf limits.Factory) (WebSocketServer, error) {
	config.applyDefaults()
	if config.Path == HealthCheckPath {
		return nil, fmt.Errorf("WebSocket request path %q conflicts with health check path", config.Path)
	}
	if err := config.ensureLimiters(lf); err != nil {
		return nil, err
	}
	baseCtx, cancelBaseCtx := context.WithCancel(context.Background())
	upgrader := &websocket.Upgrader{
		HandshakeTimeout: time.Duration(config.HandshakeTimeoutMillis) * time.Millisecond,
	}
	server := &webSocketServer{
		config:            config,
		acceptor:          acceptor,
		upgrader:          upgrader,
		doneCh:            make(chan struct{}),
		cancelBaseContext: cancelBaseCtx,
		lggr:              logger.Named(lggr, "WebSocketServer"),
	}
	mux := http.NewServeMux()
	mux.Handle(HealthCheckPath, http.HandlerFunc(server.handleHealthCheck))
	mux.Handle(config.Path, http.HandlerFunc(server.handleRequest))
	server.server = &http.Server{
		Addr:              fmt.Sprintf("%s:%d", config.Host, config.Port),
		Handler:           mux,
		BaseContext:       func(net.Listener) context.Context { return baseCtx },
		ReadTimeout:       time.Duration(config.ReadTimeoutMillis) * time.Millisecond,
		ReadHeaderTimeout: time.Duration(config.ReadTimeoutMillis) * time.Millisecond,
		WriteTimeout:      time.Duration(config.WriteTimeoutMillis) * time.Millisecond,
	}
	return server, nil
```

**File:** core/services/gateway/network/wsserver.go (L111-123)
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
```

**File:** core/services/gateway/network/constants.go (L1-16)
```go
package network

const (
	WsServerHandshakeAuthHeaderName      string = "Authorization"
	WsServerHandshakeChallengeHeaderName string = "Challenge"

	HandshakeTimestampLen            int = 4
	HandshakeDonIDLen                int = 64
	HandshakeGatewayURLLen           int = 128
	HandshakeSignatureLen            int = 65
	HandshakeAuthHeaderLen           int = HandshakeTimestampLen + HandshakeDonIDLen + HandshakeGatewayURLLen + HandshakeSignatureLen
	HandshakeEncodedAuthHeaderMaxLen int = 512
	HandshakeChallengeMinLen         int = HandshakeTimestampLen + HandshakeGatewayURLLen + 1
)


```

**File:** core/services/gateway/network/handshake.go (L75-90)
```go
func UnpackSignedAuthHeader(data []byte) (elems *AuthHeaderElems, signer []byte, err error) {
	if len(data) != HandshakeAuthHeaderLen {
		return nil, nil, fmt.Errorf("auth header length is invalid (expected: %d, got: %d)", HandshakeAuthHeaderLen, len(data))
	}
	elems = &AuthHeaderElems{}
	offset := 0
	elems.Timestamp = common.BytesToUint32(data[offset : offset+HandshakeTimestampLen])
	offset += HandshakeTimestampLen
	elems.DonID = common.AlignedBytesToString(data[offset : offset+HandshakeDonIDLen])
	offset += HandshakeDonIDLen
	elems.GatewayID = common.AlignedBytesToString(data[offset : offset+HandshakeGatewayURLLen])
	offset += HandshakeGatewayURLLen
	signature := data[offset:]
	signer, err = common.ExtractSigner(signature, data[:len(data)-HandshakeSignatureLen])
	return elems, signer, err
}
```
