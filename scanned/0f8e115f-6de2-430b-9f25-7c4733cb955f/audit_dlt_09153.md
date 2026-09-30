# [?] fix data race in syncer/launcher (#14050)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2024-08-06
Source: https://github.com/smartcontractkit/chainlink/commit/537d2ec1ad846898f820874442c3f69915096bad
Type: security-commit

## Details
fix data race in syncer/launcher (#14050)

## Patch
### .changeset/twelve-balloons-turn.md
```diff
@@ -0,0 +1,5 @@
+---
+"chainlink": patch
+---
+
+#internal fix data race in syncer launcher
```

### core/capabilities/registry.go
```diff
@@ -37,6 +37,8 @@ func (r *Registry) LocalNode(ctx context.Context) (capabilities.Node, error) {
 }
 
 func (r *Registry) ConfigForCapability(ctx context.Context, capabilityID string, donID uint32) (capabilities.CapabilityConfiguration, error) {
+	r.mu.RLock()
+	defer r.mu.RUnlock()
 	if r.metadataRegistry == nil {
 		return capabilities.CapabilityConfiguration{}, errors.New("metadataRegistry information not available")
 	}
```
