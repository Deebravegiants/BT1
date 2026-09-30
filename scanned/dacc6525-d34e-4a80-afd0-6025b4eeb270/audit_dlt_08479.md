# [?] fix getlogs deadlock (#2127)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2025-04-11
Source: https://github.com/sei-protocol/sei-chain/commit/54bf1476cd188ff2679e2f6979a40ae4b8a838e2
Type: security-commit

## Details
fix getlogs deadlock (#2127)

* bump sei-cosmos to v0.3.57

* Fix getLogs deadlock

## Patch
### evmrpc/filter.go
```diff
@@ -305,8 +305,10 @@ func (f *LogFetcher) GetLogsByFilters(ctx context.Context, crit filters.FilterCr
 		}
 	}
 	close(runner.Queue)
-	runner.Done.Wait()
-	close(resultsChan)
+	go func() {
+		runner.Done.Wait()
+		close(resultsChan)
+	}()
 
 	// Aggregate results into the final slice
 	for result := range resultsChan {
```
