# [?] Merge pull request #8519 from onflow/leo/access-fix-panics

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2026-04-08
Source: https://github.com/onflow/flow-go/commit/b91e22981f50d71c19f610b22a97c20cbe8b60b4
Type: security-commit

## Details
Merge pull request #8519 from onflow/leo/access-fix-panics

[Access] Remove panics from legacy handler

## Patch
### access/legacy/handler.go
```diff
@@ -35,7 +35,7 @@ func (h *Handler) GetNetworkParameters(
 	context.Context,
 	*accessproto.GetNetworkParametersRequest,
 ) (*accessproto.GetNetworkParametersResponse, error) {
-	panic("implement me")
+	return nil, status.Error(codes.Unimplemented, "not implemented")
 }
 
 // SendTransaction submits a transaction to the network.
@@ -252,7 +252,7 @@ func (h *Handler) GetAccountAtBlockHeight(
 	ctx context.Context,
 	request *accessproto.GetAccountAtBlockHeightRequest,
 ) (*accessproto.AccountResponse, error) {
-	panic("implement me")
+	return nil, status.Error(codes.Unimplemented, "not implemented")
 }
 
 // ExecuteScriptAtLatestBlock executes a script at a the latest block
```
