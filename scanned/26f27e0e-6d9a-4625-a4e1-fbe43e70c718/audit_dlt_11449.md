# [?] Attempt to fix streams lookup race condition (#11284)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2023-11-14
Source: https://github.com/smartcontractkit/ccip/commit/9471f2eb833225310e90da93148e89650f15edfd
Type: security-commit

## Details
Attempt to fix streams lookup race condition (#11284)

## Patch
### core/services/ocr2/plugins/ocr2keeper/evm21/streams_lookup.go
```diff
@@ -151,11 +151,13 @@ func (r *EvmRegistry) streamsLookup(ctx context.Context, checkResults []ocr2keep
 	var wg sync.WaitGroup
 
 	for i, lookup := range lookups {
-		i := i
 		wg.Add(1)
-		r.threadCtrl.Go(func(ctx context.Context) {
-			r.doLookup(ctx, &wg, lookup, i, checkResults, lggr)
-		})
+		func(i int, lookup *StreamsLookup) {
+			r.threadCtrl.Go(func(ctx context.Context) {
+				r.doLookup(ctx, &wg, lookup, i, checkResults, lggr)
+			})
+		}(i, lookup)
+
 	}
 
 	wg.Wait()
```
