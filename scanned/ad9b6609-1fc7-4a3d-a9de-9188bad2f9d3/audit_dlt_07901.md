# [?] eth/tracers: fix crasher in TraceCall with BlockOverrides (#3431)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2025-11-06
Source: https://github.com/bnb-chain/bsc/commit/8139edee158154e0158d09065adbdb4c469298d8
Type: security-commit

## Details
eth/tracers: fix crasher in TraceCall with BlockOverrides (#3431)

## Patch
### eth/tracers/api.go
```diff
@@ -1090,7 +1090,7 @@ func (api *API) TraceCall(ctx context.Context, args ethapi.TransactionArgs, bloc
 
 	// Apply the customization rules if required.
 	if config != nil {
-		if config.BlockOverrides != nil && config.BlockOverrides.Number.ToInt().Uint64() == h.Number.Uint64()+1 {
+		if config.BlockOverrides != nil && config.BlockOverrides.Number != nil && config.BlockOverrides.Number.ToInt().Uint64() == h.Number.Uint64()+1 {
 			// Overriding the block number to n+1 is a common way for wallets to
 			// simulate transactions, however without the following fix, a contract
 			// can assert it is being simulated by checking if blockhash(n) == 0x0 and
```

### eth/tracers/api_test.go
```diff
@@ -468,6 +468,20 @@ func TestTraceCall(t *testing.T) {
 		{"pc":0,"op":"NUMBER","gas":24946984,"gasCost":2,"depth":1,"stack":[]},
 		{"pc":1,"op":"STOP","gas":24946982,"gasCost":0,"depth":1,"stack":["0x1337"]}]}`,
 		},
+		// Tests issue #33014 where accessing nil block number override panics.
+		{
+			blockNumber: rpc.BlockNumber(0),
+			call: ethapi.TransactionArgs{
+				From:  &accounts[0].addr,
+				To:    &accounts[1].addr,
+				Value: (*hexutil.Big)(big.NewInt(1000)),
+			},
+			config: &TraceCallConfig{
+				BlockOverrides: &override.BlockOverrides{},
+			},
+			expectErr: nil,
+			expect:    `{"gas":21000,"failed":false,"returnValue":"0x","structLogs":[]}`,
+		},
 	}
 	for i, testspec := range testSuite {
 		result, err := api.TraceCall(context.Background(), testspec.call, rpc.BlockNumberOrHash{BlockNumber: &testspec.blockNumber}, testspec.config)
```
