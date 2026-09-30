# [?] fix race condition in TestFailFirst

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2021-08-22
Source: https://github.com/libp2p/go-libp2p/commit/258e1e698b5b7b4effb15ba8a6ac98cf26a948a6
Type: security-commit

## Details
fix race condition in TestFailFirst

## Patch
### p2p/net/swarm/dial_sync_test.go
```diff
@@ -4,6 +4,7 @@ import (
 	"context"
 	"fmt"
 	"sync"
+	"sync/atomic"
 	"testing"
 	"time"
 
@@ -186,7 +187,7 @@ func TestDialSyncAllCancel(t *testing.T) {
 }
 
 func TestFailFirst(t *testing.T) {
-	var count int
+	var count int32
 	f := func(ctx context.Context, p peer.ID, reqch <-chan dialRequest) error {
 		go func() {
 			for {
@@ -196,12 +197,12 @@ func TestFailFirst(t *testing.T) {
 						return
 					}
 
-					if count > 0 {
+					if atomic.LoadInt32(&count) > 0 {
 						req.resch <- dialResponse{conn: new(Conn)}
 					} else {
 						req.resch <- dialResponse{err: fmt.Errorf("gophers ate the modem")}
 					}
-					count++
+					atomic.AddInt32(&count, 1)
 
 				case <-ctx.Done():
 					return
```
