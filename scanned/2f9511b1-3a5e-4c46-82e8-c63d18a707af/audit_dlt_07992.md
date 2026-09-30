# [?] Fix panic in eth_getLogs

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/bor
Published: 2024-10-04
Source: https://github.com/0xPolygon/bor/commit/827811a8d22a965dce977dfb728ec0c9bb5ef631
Type: security-commit

## Details
Fix panic in eth_getLogs

## Patch
### eth/filters/api.go
```diff
@@ -352,7 +352,7 @@ func (api *FilterAPI) GetLogs(ctx context.Context, crit FilterCriteria) ([]*type
 		return nil, errExceedMaxTopics
 	}
 
-	borConfig := api.chainConfig.Bor
+	borConfig := api.sys.backend.ChainConfig().Bor
 
 	var filter *Filter
 
@@ -435,7 +435,7 @@ func (api *FilterAPI) GetFilterLogs(ctx context.Context, id rpc.ID) ([]*types.Lo
 		return nil, errFilterNotFound
 	}
 
-	borConfig := api.chainConfig.Bor
+	borConfig := api.sys.backend.ChainConfig().Bor
 
 	var filter *Filter
 
```
