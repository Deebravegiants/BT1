# [?] fix: Fix data race test coverage. (#20156)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2024-04-23
Source: https://github.com/cosmos/cosmos-sdk/commit/8a98c7c36b801cad6829673e563137f3e38612c3
Type: security-commit

## Details
fix: Fix data race test coverage. (#20156)

## Patch
### testutil/network/network.go
```diff
@@ -12,6 +12,7 @@ import (
 	"path/filepath"
 	"strings"
 	"sync"
+	"sync/atomic"
 	"syscall"
 	"testing"
 	"time"
@@ -647,29 +648,29 @@ func (n *Network) LatestHeight() (int64, error) {
 	timeout := time.NewTimer(time.Second * 5)
 	defer timeout.Stop()
 
-	var latestHeight int64
+	var latestHeight atomic.Int64
 	val := n.Validators[0]
 	queryClient := cmtservice.NewServiceClient(val.clientCtx)
 
 	for {
 		select {
 		case <-timeout.C:
-			return latestHeight, errors.New("timeout exceeded waiting for block")
+			return latestHeight.Load(), errors.New("timeout exceeded waiting for block")
 		case <-ticker.C:
 			done := make(chan struct{})
 			go func() {
 				res, err := queryClient.GetLatestBlock(context.Background(), &cmtservice.GetLatestBlockRequest{})
 				if err == nil && res != nil {
-					latestHeight = res.SdkBlock.Header.Height
+					latestHeight.Store(res.SdkBlock.Header.Height)
 				}
 				done <- struct{}{}
 			}()
 			select {
 			case <-timeout.C:
-				return latestHeight, errors.New("timeout exceeded waiting for block")
+				return latestHeight.Load(), errors.New("timeout exceeded waiting for block")
 			case <-done:
-				if latestHeight != 0 {
-					return latestHeight, nil
+				if latestHeight.Load() != 0 {
+					return latestHeight.Load(), nil
 				}
 			}
 		}
```
