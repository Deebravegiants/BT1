# [?] node: fix data race on httpConfig.prefix (#32047)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-06-16
Source: https://github.com/ethereum/go-ethereum/commit/9402187733c5b085a299c84a5aaf9e1fbd01e117
Type: security-commit

## Details
node: fix data race on httpConfig.prefix (#32047)

This fixes a data race when accessing the `httpConfig.prefix` field.
This field can be modified while the server is running through
`enableRPC`. The fix is storing the prefix in the handler, which is
accessed through the atomic pointer.

alternative to #32035
fixes https://github.com/ethereum/go-ethereum/issues/32019

## Patch
### node/rpcstack.go
```diff
@@ -62,6 +62,7 @@ type rpcEndpointConfig struct {
 
 type rpcHandler struct {
 	http.Handler
+	prefix string
 	server *rpc.Server
 }
 
@@ -77,11 +78,11 @@ type httpServer struct {
 	// HTTP RPC handler things.
 
 	httpConfig  httpConfig
-	httpHandler atomic.Value // *rpcHandler
+	httpHandler atomic.Pointer[rpcHandler]
 
 	// WebSocket handler things.
 	wsConfig  wsConfig
-	wsHandler atomic.Value // *rpcHandler
+	wsHandler atomic.Pointer[rpcHandler]
 
 	// These are set by setListenAddr.
 	endpoint string
@@ -97,9 +98,6 @@ const (
 
 func newHTTPServer(log log.Logger, timeouts rpc.HTTPTimeouts) *httpServer {
 	h := &httpServer{log: log, timeouts: timeouts, handlerNames: make(map[string]string)}
-
-	h.httpHandler.Store((*rpcHandler)(nil))
-	h.wsHandler.Store((*rpcHandler)(nil))
 	return h
 }
 
@@ -198,16 +196,16 @@ func (h *httpServer) start() error {
 
 func (h *httpServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
 	// check if ws request and serve if ws enabled
-	ws := h.wsHandler.Load().(*rpcHandler)
+	ws := h.wsHandler.Load()
 	if ws != nil && isWebsocket(r) {
-		if checkPath(r, h.wsConfig.prefix) {
+		if checkPath(r, ws.prefix) {
 			ws.ServeHTTP(w, r)
 		}
 		return
 	}
 
 	// if http-rpc is enabled, try to serve request
-	rpc := h.httpHandler.Load().(*rpcHandler)
+	rpc := h.httpHandler.Load()
 	if rpc != nil {
 		// First try to route in the mux.
 		// Requests to a path below root are handled by the mux,
@@ -219,7 +217,7 @@ func (h *httpServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
 			return
 		}
 
-		if checkPath(r, h.httpConfig.prefix) {
+		if checkPath(r, rpc.prefix) {
 			rpc.ServeHTTP(w, r)
 			return
 		}
@@ -267,14 +265,14 @@ func (h *httpServer) doStop() {
 	}
 
 	// Shut down the server.
-	httpHandler := h.httpHandler.Load().(*rpcHandler)
-	wsHandler := h.wsHandler.Load().(*rpcHandler)
+	httpHandler := h.httpHandler.Load()
+	wsHandler := h.wsHandler.Load()
 	if httpHandler != nil {
-		h.httpHandler.Store((*rpcHandler)(nil))
+		h.httpHandler.Store(nil)
 		httpHandler.server.Stop()
 	}
 	if wsHandler != nil {
-		h.wsHandler.Store((*rpcHandler)(nil))
+		h.wsHandler.Store(nil)
 		wsHandler.server.Stop()
 	}
 
@@ -315,16 +313,17 @@ func (h *httpServer) enableRPC(apis []rpc.API, config httpConfig) error {
 	h.httpConfig = config
 	h.httpHandler.Store(&rpcHandler{
 		Handler: NewHTTPHandlerStack(srv, config.CorsAllowedOrigins, config.Vhosts, config.jwtSecret),
+		prefix:  config.prefix,
 		server:  srv,
 	})
 	return nil
 }
 
 // disableRPC stops the HTTP RPC handler. This is internal, the caller must hold h.mu.
 func (h *httpServer) disableRPC() bool {
-	handler := h.httpHandler.Load().(*rpcHandler)
+	handler := h.httpHandler.Load()
 	if handler != nil {
-		h.httpHandler.Store((*rpcHandler)(nil))
+		h.httpHandler.Store(nil)
 		handler.server.Stop()
 	}
 	return handler != nil
@@ -350,6 +349,7 @@ func (h *httpServer) enableWS(apis []rpc.API, config wsConfig) error {
 	h.wsConfig = config
 	h.wsHandler.Store(&rpcHandler{
 		Handler: NewWSHandlerStack(srv.WebsocketHandler(config.Origins), config.jwtSecret),
+		prefix:  config.prefix,
 		server:  srv,
 	})
 	return nil
@@ -369,22 +369,22 @@ func (h *httpServer) stopWS() {
 
 // disableWS disables the WebSocket handler. This is internal, the caller must hold h.mu.
 func (h *httpServer) disableWS() bool {
-	ws := h.wsHandler.Load().(*rpcHandler)
+	ws := h.wsHandler.Load()
 	if ws != nil {
-		h.wsHandler.Store((*rpcHandler)(nil))
+		h.wsHandler.Store(nil)
 		ws.server.Stop()
 	}
 	return ws != nil
 }
 
 // rpcAllowed returns true when JSON-RPC over HTTP is enabled.
 func (h *httpServer) rpcAllowed() bool {
-	return h.httpHandler.Load().(*rpcHandler) != nil
+	return h.httpHandler.Load() != nil
 }
 
 // wsAllowed returns true when JSON-RPC over WebSocket is enabled.
 func (h *httpServer) wsAllowed() bool {
-	return h.wsHandler.Load().(*rpcHandler) != nil
+	return h.wsHandler.Load() != nil
 }
 
 // isWebsocket checks the header of an http request for a websocket upgrade request.
```
