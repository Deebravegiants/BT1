# [?] Attempt to fix a panic error.

## Summary
Severity: Unknown
Chain: THORChain
Component: thorchain/thornode
Published: 2019-08-02
Source: https://github.com/thorchain/thornode/commit/6113e203aec3446208159e6eee88145c4d04ccd3
Type: security-commit

## Details
Attempt to fix a panic error.

## Patch
### x/silverback/server.go
```diff
@@ -51,12 +51,15 @@ func (s *Server) Start() {
 			svrChan <- client
 
 			for {
-					select {
-					case text, _ := <-client:
-						writer, _ := ws.NextWriter(websocket.TextMessage)
+				select {
+				case text, _ := <-client:
+					writer, err := ws.NextWriter(websocket.TextMessage)
+					// For some reason the client has gone away...
+					if err == nil {
 						writer.Write([]byte(text))
 						writer.Close()
 					}
+				}
 			}
 		})
 		http.ListenAndServe(":" + s.Port, nil)
```
