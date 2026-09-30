# [?] fix(client): Panic due to possible nil params response (#277)

## Summary
Severity: Unknown
Chain: Babylon
Component: babylonlabs-io/babylon
Published: 2024-11-19
Source: https://github.com/babylonlabs-io/babylon/commit/48978b0cccbb5e765f6cec2c60ec0a8dc5a42a12
Type: security-commit

## Details
fix(client): Panic due to possible nil params response (#277)

Root cause of
https://github.com/babylonlabs-io/finality-provider/issues/121. If
response is nil due to error, will cause panic

## Patch
### CHANGELOG.md
```diff
@@ -42,6 +42,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
 
 - [#270](https://github.com/babylonlabs-io/babylon/pull/270) Validate there is only
 one finality provider key in the staking request
+- [#270](https://github.com/babylonlabs-io/babylon/pull/277) Panic due to possible
+nil params response
 
 ## v0.16.1
 
```

### client/query/finality.go
```diff
@@ -3,9 +3,10 @@ package query
 import (
 	"context"
 
-	finalitytypes "github.com/babylonlabs-io/babylon/x/finality/types"
 	"github.com/cosmos/cosmos-sdk/client"
 	sdkquerytypes "github.com/cosmos/cosmos-sdk/types/query"
+
+	finalitytypes "github.com/babylonlabs-io/babylon/x/finality/types"
 )
 
 // QueryFinality queries the Finality module of the Babylon node according to the given function
@@ -65,7 +66,7 @@ func (c *QueryClient) ActivatedHeight() (*finalitytypes.QueryActivatedHeightResp
 }
 
 // FinalityParams queries the finality module parameters
-func (c *QueryClient) FinalityParams() (*finalitytypes.Params, error) {
+func (c *QueryClient) FinalityParams() (*finalitytypes.QueryParamsResponse, error) {
 	var resp *finalitytypes.QueryParamsResponse
 	err := c.QueryFinality(func(ctx context.Context, queryClient finalitytypes.QueryClient) error {
 		var err error
@@ -74,7 +75,7 @@ func (c *QueryClient) FinalityParams() (*finalitytypes.Params, error) {
 		return err
 	})
 
-	return &resp.Params, err
+	return resp, err
 }
 
 // VotesAtHeight queries the Finality module to get signature set at a given babylon block height
```
