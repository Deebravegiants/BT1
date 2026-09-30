# [?] kaiax/reward: Fix deadlock in accumulateRewards

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2025-08-05
Source: https://github.com/kaiachain/kaia/commit/b62027634cfeff31db7a88539388fb64d0a36c62
Type: security-commit

## Details
kaiax/reward: Fix deadlock in accumulateRewards

## Patch
### kaiax/reward/impl/api.go
```diff
@@ -17,6 +17,7 @@
 package impl
 
 import (
+	"context"
 	"runtime"
 	"sync"
 
@@ -117,39 +118,58 @@ func (api *RewardGovAPI) accumulateRewards(lower, upper uint64) (*reward.RewardS
 		accSpec = reward.NewRewardSpec()
 		mu      sync.Mutex
 
-		numWorkers = runtime.NumCPU()
-		reqCh      = make(chan uint64, numWorkers)
-		errCh      = make(chan error, numWorkers)
-		wg         sync.WaitGroup
+		numWorkers  = runtime.NumCPU()
+		reqCh       = make(chan uint64, numWorkers)
+		errCh       = make(chan error, 1)
+		wg          sync.WaitGroup
+		ctx, cancel = context.WithCancel(context.Background())
 	)
+	defer cancel()
 
 	for i := 0; i < numWorkers; i++ {
 		wg.Add(1)
 		go func() {
 			defer wg.Done()
-			for num := range reqCh {
-				spec, err := api.r.GetBlockReward(num)
-				if err != nil {
-					errCh <- err
+			for {
+				select {
+				case <-ctx.Done():
 					return
+				case num, ok := <-reqCh:
+					if !ok {
+						return
+					}
+					spec, err := api.r.GetBlockReward(num)
+					if err != nil {
+						select {
+						case errCh <- err:
+						default:
+						}
+						cancel()
+						return
+					}
+					mu.Lock()
+					accSpec.Add(spec)
+					mu.Unlock()
 				}
-				mu.Lock()
-				accSpec.Add(spec)
-				mu.Unlock()
 			}
 		}()
 	}
 
 	for num := lower; num <= upper; num++ {
-		reqCh <- num
+		select {
+		case <-ctx.Done():
+			break
+		case reqCh <- num:
+		}
 	}
 	close(reqCh)
 
 	wg.Wait()
-	close(errCh)
 
-	if err := <-errCh; err != nil {
+	select {
+	case err := <-errCh:
 		return nil, err
+	default:
+		return accSpec, nil
 	}
-	return accSpec, nil
 }
```
