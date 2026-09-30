# [?] Fix for nil feedID causing panics in the UI (#9835)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2023-07-18
Source: https://github.com/smartcontractkit/ccip/commit/c56e37d2c1b08051530f2f5293656258ee4d3430
Type: security-commit

## Details
Fix for nil feedID causing panics in the UI (#9835)

Fix for the job UI that got broken by https://github.com/smartcontractkit/chainlink/pull/9814

## Patch
### core/web/resolver/spec.go
```diff
@@ -614,8 +614,12 @@ func (r *OCR2SpecResolver) TransmitterID() *string {
 }
 
 // FeedID resolves the spec's feed ID
-func (r *OCR2SpecResolver) FeedID() string {
-	return r.spec.FeedID.String()
+func (r *OCR2SpecResolver) FeedID() *string {
+	if r.spec.FeedID == nil {
+		return nil
+	}
+	feedID := r.spec.FeedID.String()
+	return &feedID
 }
 
 type VRFSpecResolver struct {
```

### core/web/schema/type/spec.graphql
```diff
@@ -91,7 +91,7 @@ type OCR2Spec {
     transmitterID: String
     pluginType: String!
     pluginConfig: Map!
-    feedID: String!
+    feedID: String
 }
 
 type VRFSpec {
```
