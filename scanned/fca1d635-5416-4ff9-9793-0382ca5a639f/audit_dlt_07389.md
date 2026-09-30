# [?] fix deadlock in the transport's serve function

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2021-07-24
Source: https://github.com/libp2p/go-libp2p/commit/ea4a94069b0fb92eacbf43d62a5833fd6dbca1ec
Type: security-commit

## Details
fix deadlock in the transport's serve function

We don't close the connection before the echo hasn't returned, but echo won't
return before AcceptStream has returned an error, which only happens when the
connection is closed.

## Patch
### p2p/transport/testsuite/stream_suite.go
```diff
@@ -138,12 +138,12 @@ func serve(t *testing.T, l transport.Listener) {
 		if err != nil {
 			return
 		}
+		defer c.Close()
 
 		wg.Add(1)
 		debugLog(t, "accepted connection")
 		go func() {
 			defer wg.Done()
-			defer c.Close()
 			echo(t, c)
 		}()
 	}
```
