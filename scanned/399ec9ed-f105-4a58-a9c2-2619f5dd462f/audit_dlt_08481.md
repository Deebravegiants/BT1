# [?] Avoid panics in getLogs (#1993)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2024-12-21
Source: https://github.com/sei-protocol/sei-chain/commit/ee91380299980d5164bca2a2d57451863db36093
Type: security-commit

## Details
Avoid panics in getLogs (#1993)

* Avoid panics in getLogs

* Fix

* Address comments for best effort

## Patch
### evmrpc/filter.go
```diff
@@ -321,6 +321,7 @@ func (f *LogFetcher) GetLogsByFilters(ctx context.Context, crit filters.FilterCr
 	}
 
 	// Parallelize execution
+	var mu = sync.Mutex{}
 	numWorkers := int(math.Min(MaxNumOfWorkers, float64(end-begin+1)))
 	var wg sync.WaitGroup
 	tasksChan := make(chan int64, end-begin+1)
@@ -343,8 +344,14 @@ func (f *LogFetcher) GetLogsByFilters(ctx context.Context, crit filters.FilterCr
 	}()
 
 	// Worker function
+	var errorsList []error
 	worker := func() {
 		defer wg.Done()
+		defer func() {
+			if r := recover(); r != nil {
+				err = fmt.Errorf("unexpected panic caught in GetLogsByFilters worker: %v", r)
+			}
+		}()
 		for height := range tasksChan {
 			if len(crit.Addresses) != 0 || len(crit.Topics) != 0 {
 				providerCtx := f.ctxProvider(height)
@@ -356,11 +363,14 @@ func (f *LogFetcher) GetLogsByFilters(ctx context.Context, crit filters.FilterCr
 			h := height
 			block, berr := blockByNumberWithRetry(ctx, f.tmClient, &h, 1)
 			if berr != nil {
-				panic(berr)
-			}
-			matchedLogs := f.GetLogsForBlock(block, crit, bloomIndexes)
-			for _, log := range matchedLogs {
-				resultsChan <- log
+				mu.Lock()
+				errorsList = append(errorsList, berr)
+				mu.Unlock()
+			} else {
+				matchedLogs := f.GetLogsForBlock(block, crit, bloomIndexes)
+				for _, log := range matchedLogs {
+					resultsChan <- log
+				}
 			}
 		}
 	}
@@ -377,6 +387,11 @@ func (f *LogFetcher) GetLogsByFilters(ctx context.Context, crit filters.FilterCr
 		close(resultsChan) // Close the results channel after workers finish
 	}()
 
+	// Check err after all work is done
+	if len(errorsList) > 0 {
+		err = errors.Join(errorsList...)
+	}
+
 	// Aggregate results into the final slice
 	for result := range resultsChan {
 		res = append(res, result)
@@ -392,7 +407,7 @@ func (f *LogFetcher) GetLogsByFilters(ctx context.Context, crit filters.FilterCr
 		res = res[:int(f.filterConfig.maxLog)]
 	}
 
-	return res, end, nil
+	return res, end, err
 }
 
 func (f *LogFetcher) GetLogsForBlock(block *coretypes.ResultBlock, crit filters.FilterCriteria, filters [][]bloomIndexes) []*ethtypes.Log {
```
