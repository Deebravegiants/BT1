# [?] Avoid deadlock in GetRewardsAccumulated

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2024-07-17
Source: https://github.com/kaiachain/kaia/commit/10d71723a9c9b6d648d89a9ae28b4188456f5b80
Type: security-commit

## Details
Avoid deadlock in GetRewardsAccumulated

## Patch
### governance/api.go
```diff
@@ -174,29 +174,27 @@ func (api *GovernanceAPI) GetRewardsAccumulated(first rpc.BlockNumber, last rpc.
 	mu := sync.Mutex{} // protect blockRewards
 
 	numWorkers := runtime.NumCPU()
-	// TODO-api: Fix hanging issue when requested range is over numWorkers considering goroutine scheduling
-	reqCh := make(chan uint64, blockCount)
-	errCh := make(chan error, blockCount+1)
+	reqCh := make(chan uint64, numWorkers)
+	errCh := make(chan error, 1)
 	wg := sync.WaitGroup{}
 
 	// introduce the worker pattern to prevent resource exhaustion
 	for i := 0; i < numWorkers; i++ {
+		wg.Add(1)
 		go func() {
+			defer wg.Done()
 			// the minimum digit of request is period to avoid current access to an accArray item
 			for num := range reqCh {
 				bn := rpc.BlockNumber(num)
 				blockReward, err := govKaiaAPI.GetRewards(&bn)
 				if err != nil {
 					errCh <- err
-					wg.Done()
 					return
 				}
 
 				mu.Lock()
 				blockRewards.Add(blockReward)
 				mu.Unlock()
-
-				wg.Done()
 			}
 		}()
 	}
@@ -217,15 +215,17 @@ func (api *GovernanceAPI) GetRewardsAccumulated(first rpc.BlockNumber, last rpc.
 	accumRewards.LastBlock = header.Number
 	accumRewards.LastBlockTime = time.Unix(header.Time.Int64(), 0).String()
 
-	for num := firstBlock; num <= lastBlock; num++ {
-		wg.Add(1)
-		reqCh <- num
-	}
+	go func() {
+		defer close(reqCh)
+		for num := firstBlock; num <= lastBlock; num++ {
+			reqCh <- num
+		}
+	}()
 
 	// generate a goroutine to return error early
 	go func() {
 		wg.Wait()
-		errCh <- nil
+		close(errCh)
 	}()
 
 	if err := <-errCh; err != nil {
```
