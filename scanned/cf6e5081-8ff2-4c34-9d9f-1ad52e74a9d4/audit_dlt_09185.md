# [?] swarm: fix race condition in TestFailFirst (#1490)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2022-05-16
Source: https://github.com/libp2p/go-libp2p/commit/c51c1b642cf8a05f496525b0a9156afaf6de07e0
Type: security-commit

## Details
swarm: fix race condition in TestFailFirst (#1490)

## Patch
### p2p/net/swarm/dial_sync_test.go
```diff
@@ -9,6 +9,8 @@ import (
 	"time"
 
 	"github.com/libp2p/go-libp2p-core/peer"
+
+	"github.com/stretchr/testify/require"
 )
 
 func getMockDialFunc() (dialWorkerFunc, func(), context.Context, <-chan struct{}) {
@@ -161,6 +163,7 @@ func TestDialSyncAllCancel(t *testing.T) {
 
 func TestFailFirst(t *testing.T) {
 	var count int32
+	dialErr := fmt.Errorf("gophers ate the modem")
 	f := func(p peer.ID, reqch <-chan dialRequest) {
 		go func() {
 			for {
@@ -169,12 +172,11 @@ func TestFailFirst(t *testing.T) {
 					return
 				}
 
-				if atomic.LoadInt32(&count) > 0 {
-					req.resch <- dialResponse{conn: new(Conn)}
+				if atomic.CompareAndSwapInt32(&count, 0, 1) {
+					req.resch <- dialResponse{err: dialErr}
 				} else {
-					req.resch <- dialResponse{err: fmt.Errorf("gophers ate the modem")}
+					req.resch <- dialResponse{conn: new(Conn)}
 				}
-				atomic.AddInt32(&count, 1)
 			}
 		}()
 	}
@@ -185,17 +187,12 @@ func TestFailFirst(t *testing.T) {
 	ctx, cancel := context.WithTimeout(context.Background(), time.Second*5)
 	defer cancel()
 
-	if _, err := ds.Dial(ctx, p); err == nil {
-		t.Fatal("expected gophers to have eaten the modem")
-	}
+	_, err := ds.Dial(ctx, p)
+	require.ErrorIs(t, err, dialErr, "expected gophers to have eaten the modem")
 
 	c, err := ds.Dial(ctx, p)
-	if err != nil {
-		t.Fatal(err)
-	}
-	if c == nil {
-		t.Fatal("should have gotten a 'real' conn back")
-	}
+	require.NoError(t, err)
+	require.NotNil(t, c, "should have gotten a 'real' conn back")
 }
 
 func TestStressActiveDial(t *testing.T) {
```
