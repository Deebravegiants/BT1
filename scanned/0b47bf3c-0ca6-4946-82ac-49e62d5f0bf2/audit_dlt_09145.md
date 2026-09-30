# [?] fix for race condition in registry (#17098)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2025-04-03
Source: https://github.com/smartcontractkit/chainlink/commit/97b9a827e032ab6dad0799653758552c8c5a473c
Type: security-commit

## Details
fix for race condition in registry (#17098)

## Patch
### core/capabilities/registry.go
```diff
@@ -31,6 +31,8 @@ type Registry struct {
 }
 
 func (r *Registry) LocalNode(ctx context.Context) (capabilities.Node, error) {
+	r.mu.Lock()
+	defer r.mu.Unlock()
 	if r.metadataRegistry == nil {
 		return capabilities.Node{}, errors.New("metadataRegistry information not available")
 	}
```
