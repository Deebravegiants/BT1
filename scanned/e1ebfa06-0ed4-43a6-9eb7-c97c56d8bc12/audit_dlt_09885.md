# [?] [api] fix panic: concurrent write to websocket connection (#3908)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2023-08-01
Source: https://github.com/iotexproject/iotex-core/commit/789336a40ca397c6443dd79ce35f4128410f88c1
Type: security-commit

## Details
[api] fix panic: concurrent write to websocket connection (#3908)

* fix panic:concurrent write to websocket connection

Co-authored-by: dustinxie <dahuaxie@gmail.com>

## Patch
### api/websocket.go
```diff
@@ -3,6 +3,7 @@ package api
 import (
 	"context"
 	"net/http"
+	"sync"
 	"time"
 
 	"github.com/gorilla/websocket"
@@ -36,6 +37,40 @@ var upgrader = websocket.Upgrader{
 	WriteBufferSize: 1024,
 }
 
+// type safeWebsocketConn wraps websocket.Conn with a mutex
+// to avoid concurrent write to the connection
+// https://pkg.go.dev/github.com/gorilla/websocket#hdr-Concurrency
+type safeWebsocketConn struct {
+	ws *websocket.Conn
+	mu sync.Mutex
+}
+
+// WiteJSON writes a JSON message to the connection in a thread-safe way
+func (c *safeWebsocketConn) WriteJSON(message interface{}) error {
+	c.mu.Lock()
+	defer c.mu.Unlock()
+	return c.ws.WriteJSON(message)
+}
+
+// WriteMessage writes a message to the connection in a thread-safe way
+func (c *safeWebsocketConn) WriteMessage(messageType int, data []byte) error {
+	c.mu.Lock()
+	defer c.mu.Unlock()
+	return c.ws.WriteMessage(messageType, data)
+}
+
+// Close closes the underlying network connection without sending or waiting for a close frame
+func (c *safeWebsocketConn) Close() error {
+	return c.ws.Close()
+}
+
+// SetWriteDeadline sets the write deadline on the underlying network connection
+func (c *safeWebsocketConn) SetWriteDeadline(t time.Time) error {
+	c.mu.Lock()
+	defer c.mu.Unlock()
+	return c.ws.SetWriteDeadline(t)
+}
+
 // NewWebsocketHandler creates a new websocket handler
 func NewWebsocketHandler(web3Handler Web3Handler) *WebsocketHandler {
 	return &WebsocketHandler{
@@ -70,7 +105,8 @@ func (wsSvr *WebsocketHandler) handleConnection(ctx context.Context, ws *websock
 	})
 
 	ctx, cancel := context.WithCancel(ctx)
-	go ping(ctx, ws, cancel)
+	safeWs := &safeWebsocketConn{ws: ws}
+	go ping(ctx, safeWs, cancel)
 
 	for {
 		select {
@@ -87,10 +123,10 @@ func (wsSvr *WebsocketHandler) handleConnection(ctx context.Context, ws *websock
 			err = wsSvr.msgHandler.HandlePOSTReq(ctx, reader,
 				apitypes.NewResponseWriter(
 					func(resp interface{}) (int, error) {
-						if err = ws.SetWriteDeadline(time.Now().Add(writeWait)); err != nil {
+						if err = safeWs.SetWriteDeadline(time.Now().Add(writeWait)); err != nil {
 							log.Logger("api").Warn("failed to set write deadline timeout.", zap.Error(err))
 						}
-						return 0, ws.WriteJSON(resp)
+						return 0, safeWs.WriteJSON(resp)
 					}),
 			)
 			if err != nil {
@@ -102,7 +138,7 @@ func (wsSvr *WebsocketHandler) handleConnection(ctx context.Context, ws *websock
 	}
 }
 
-func ping(ctx context.Context, ws *websocket.Conn, cancel context.CancelFunc) {
+func ping(ctx context.Context, ws *safeWebsocketConn, cancel context.CancelFunc) {
 	pingTicker := time.NewTicker(pingPeriod)
 	defer func() {
 		pingTicker.Stop()
```
