# [?] readiness: fix data race

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2021-07-21
Source: https://github.com/wormhole-foundation/wormhole/commit/07106497f101ef85d20e6de8e309825b28465e75
Type: security-commit

## Details
readiness: fix data race

Change-Id: If548f2b28d4ebaaa7d5a2127f684371fad6c2451

## Patch
### bridge/pkg/readiness/health.go
```diff
@@ -49,6 +49,7 @@ func Handler(w http.ResponseWriter, r *http.Request) {
 		panic(err)
 	}
 
+	mu.Lock()
 	for k, v := range registry {
 		_, err = fmt.Fprintln(resp, fmt.Sprintf("%s\t%v", k, v))
 		if err != nil {
@@ -59,6 +60,7 @@ func Handler(w http.ResponseWriter, r *http.Request) {
 			ready = false
 		}
 	}
+	mu.Unlock()
 
 	if !ready {
 		w.WriteHeader(http.StatusPreconditionFailed)
```
