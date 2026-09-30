# [?] Merge pull request #35 from libp2p/fix-serve-deadlock

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2021-07-25
Source: https://github.com/libp2p/go-libp2p/commit/bfd7dbdd6c9646ca3f64c65c57b0e669f63dd2ab
Type: security-commit

## Details
Merge pull request #35 from libp2p/fix-serve-deadlock

fix deadlock in the transport's serve function

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
@@ -241,13 +241,13 @@ func SubtestStress(t *testing.T, ta, tb transport.Transport, maddr ma.Multiaddr,
 			t.Error(err)
 			return
 		}
+		defer c.Close()
 
 		// serve the outgoing conn, because some muxers assume
 		// that we _always_ call serve. (this is an error?)
 		wg.Add(1)
 		go func() {
 			defer wg.Done()
-			defer c.Close()
 			debugLog(t, "serving connection")
 			echo(t, c)
 		}()
```
