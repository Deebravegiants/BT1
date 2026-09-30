# [?] Fix Builder Service Panic (#10937)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2022-06-27
Source: https://github.com/OffchainLabs/prysm/commit/7c489199bfb9aea4c6ecda749d67a3bc83c22ec8
Type: security-commit

## Details
Fix Builder Service Panic (#10937)

## Patch
### beacon-chain/builder/service.go
```diff
@@ -105,6 +105,11 @@ func (s *Service) Status() error {
 		getStatusLatency.Observe(float64(time.Since(start).Milliseconds()))
 	}()
 
+	// Return early if builder isn't initialized in service.
+	if s.c == nil {
+		return nil
+	}
+
 	return s.c.Status(ctx)
 }
 
```
