The node's own HTTPS API server exhibits the same bug class as the Dex advisory: the `http.Server` used to serve the Operator UI/API over TLS is created without ever setting `TLSConfig.MinVersion`, so the Go stdlib defaults (which permit TLS 1.0) are used for any connection reaching the node's public HTTPS listener.

### Title
Chainlink node HTTPS API server allows downgrade to TLS 1.0/1.1 due to missing MinVersion/CipherSuites configuration - (File: core/cmd/shell.go)

### Summary
`ChainlinkRunner.Run` starts the node's HTTPS listener via `server.runTLS`, which calls `createServer` to build the `*http.Server` and then `ListenAndServeTLS(certFile, keyFile)`. [1](#0-0) 

`createServer` only sets `Addr`, `Handler`, `ReadTimeout`, `WriteTimeout`, `IdleTimeout`, and `MaxHeaderBytes` — it never assigns a `tls.Config` (no `MinVersion`, `CipherSuites`, or `CurvePreferences`).

### Finding Description
`ListenAndServeTLS` on a `*http.Server` with a nil `TLSConfig` falls back to Go's stdlib default `tls.Config` zero value, whose minimum supported version is TLS 1.0 unless the operator's Go toolchain/runtime explicitly restricts it. This is the exact same root cause as CVE-2024-23656 (Dex): a TLS-serving `http.Server`/listener path where the intended hardened `tls.Config` (min version, cipher suites) is never actually attached to the server object that performs the handshake, so weak protocol versions and cipher suites remain negotiable. In this codebase, `WebServer.TLS` config (`HTTPSPort`, `CertPath`, `KeyPath`, `ForceRedirect`, `ListenIP`) is exposed and documented as the way operators enable TLS for the node's HTTP API/Operator UI, but nothing in this path ever constructs or attaches a `tls.Config` with a minimum version floor. [2](#0-1) [3](#0-2) 

By contrast, other TLS-terminating pieces of the codebase (outbound mTLS clients, gateway HTTP server test doubles) are careful to set `MinVersion: tls.VersionTLS12` explicitly, showing the project is otherwise aware that this must be set — it's just missing on the node's own inbound HTTPS listener. [4](#0-3) 

### Impact Explanation
Any unprivileged network attacker able to intercept traffic to the node's HTTPS API port (`WebServer.TLS.HTTPSPort`, default 6689) can attempt a protocol downgrade to TLS 1.0/1.1 and negotiate weak, non-forward-secret cipher suites (e.g. static RSA key exchange, 3DES/CBC suites), enabling decryption or tampering of session cookies, API keys, and Operator UI credentials sent to the node — a confidentiality/impersonation risk consistent with the CVE-2024-23656 impact rating (High).

### Likelihood Explanation
This applies whenever an operator enables the node's built-in HTTPS listener (a documented, supported configuration path — `WebServer.TLS.HTTPSPort != 0`), with no additional misconfiguration required; the weakness is present by default in the server construction code itself, not a rare edge case.

### Recommendation
Explicitly set `TLSConfig` on the `*http.Server` returned by `createServer` (or on the server used in `runTLS`) with `MinVersion: tls.VersionTLS12` (or higher) and a restricted, forward-secret `CipherSuites` list, mirroring the pattern already used in `core/services/gateway/network/httpclient.go`.

### Proof of Concept
1. Configure `WebServer.TLS.HTTPSPort`, `CertPath`, `KeyPath` in the node's TOML config and start the node.
2. Run `sslyze <node-ip>:<HTTPSPort>` (or `openssl s_client -tls1 -connect <node-ip>:<HTTPSPort>`) from an unprivileged network position.
3. Observe the handshake succeeds under TLS 1.0/1.1 because `createServer` in `core/cmd/shell.go` never sets `TLSConfig.MinVersion`.

### Citations

**File:** core/cmd/shell.go (L463-473)
```go
	tls := config.WebServer().TLS()
	if tls.HTTPSPort() != 0 {
		runServer := server.runTLS(
			tls.ListenIP(),
			tls.HTTPSPort(),
			tls.CertFile(),
			tls.KeyFile(),
			config.WebServer().HTTPWriteTimeout(),
		)
		go tryRunServerUntilCancelled(gCtx, app.GetLogger(), serverStartTimeoutDuration, runServer)
	}
```

**File:** core/cmd/shell.go (L558-578)
```go
func (s *server) runTLS(ip net.IP, port uint16, certFile, keyFile string, requestTimeout time.Duration) func() error {
	addr := fmt.Sprintf("%s:%d", ip.String(), port)
	s.lggr.Infow("Listening and serving HTTPS on "+addr, "ip", ip, "port", port)
	s.tlsServer = createServer(s.handler, addr, requestTimeout)
	return func() error {
		err := s.tlsServer.ListenAndServeTLS(certFile, keyFile)
		return errors.Wrap(err, "failed to run TLS server (NOTE: you can disable TLS server completely and silence these errors by setting WebServer.TLS.HTTPSPort=0 in your config)")
	}
}

func createServer(handler *gin.Engine, addr string, requestTimeout time.Duration) *http.Server {
	s := &http.Server{
		Addr:           addr,
		Handler:        handler,
		ReadTimeout:    requestTimeout,
		WriteTimeout:   requestTimeout,
		IdleTimeout:    60 * time.Second,
		MaxHeaderBytes: 1 << 20,
	}
	return s
}
```

**File:** core/config/web_config.go (L13-21)
```go
type TLS interface {
	Dir() string
	Host() string
	ForceRedirect() bool
	CertFile() string
	KeyFile() string
	HTTPSPort() uint16
	ListenIP() net.IP
}
```

**File:** core/services/gateway/network/httpclient.go (L308-311)
```go
		defaultTransport.TLSClientConfig = &tls.Config{
			Certificates: []tls.Certificate{cert},
			MinVersion:   tls.VersionTLS12,
		}
```
