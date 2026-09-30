# [?] op-e2e: Avoid panics on conductor startup failure (#10247)

## Summary
Severity: Unknown
Chain: Boba
Component: bobanetwork/boba
Published: 2024-04-23
Source: https://github.com/bobanetwork/boba/commit/da002ffb3e7809edb4c55c46489663fe642d7d98
Type: security-commit

## Details
op-e2e: Avoid panics on conductor startup failure (#10247)

## Patch
### op-e2e/sequencer_failover_setup.go
```diff
@@ -147,7 +147,9 @@ func setupHAInfra(t *testing.T, ctx context.Context) (*System, map[string]*condu
 			}
 
 			for _, c := range conductors {
-				if serr := c.service.Stop(ctx); serr != nil {
+				if c == nil || c.service == nil {
+					// pass. Sometimes we can get nil in this map
+				} else if serr := c.service.Stop(ctx); serr != nil {
 					t.Log("Failed to stop conductor", "error", serr)
 				}
 			}
```
