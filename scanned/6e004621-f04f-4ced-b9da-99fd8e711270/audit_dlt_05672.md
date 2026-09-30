# [?] fix(eth/tracers): fix crash in TraceCall with BlockOverrides (#4657)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2026-01-13
Source: https://github.com/ava-labs/avalanchego/commit/ecdb451ed454099e78f950176dab30c19f192d19
Type: security-commit

## Details
fix(eth/tracers): fix crash in TraceCall with BlockOverrides (#4657)

Co-authored-by: hero5512 <lvshuaino@gmail.com>
Co-authored-by: lightclient <lightclient@protonmail.com>
Co-authored-by: yacovm <yacovm@users.noreply.github.com>

## Patch
### graft/coreth/eth/tracers/api_test.go
```diff
@@ -430,6 +430,20 @@ func testTraceCall(t *testing.T, scheme string) {
 		{"pc":0,"op":"NUMBER","gas":24946982,"gasCost":2,"depth":1,"stack":[]},
 		{"pc":1,"op":"STOP","gas":24946980,"gasCost":0,"depth":1,"stack":["0x1337"]}]}`,
 		},
+		// Tests issue #4657 where accessing nil block number override panics.
+		{
+			blockNumber: rpc.BlockNumber(0),
+			call: ethapi.TransactionArgs{
+				From:  &accounts[0].addr,
+				To:    &accounts[1].addr,
+				Value: (*hexutil.Big)(big.NewInt(1000)),
+			},
+			config: &TraceCallConfig{
+				BlockOverrides: &ethapi.BlockOverrides{},
+			},
+			expectErr: nil,
+			expect:    `{"gas":21000,"failed":false,"returnValue":"","structLogs":[]}`,
+		},
 	}
 	for i, testspec := range testSuite {
 		result, err := api.TraceCall(context.Background(), testspec.call, rpc.BlockNumberOrHash{BlockNumber: &testspec.blockNumber}, testspec.config)
```

### graft/subnet-evm/eth/tracers/api.go
```diff
@@ -965,7 +965,7 @@ func (api *API) TraceCall(ctx context.Context, args ethapi.TransactionArgs, bloc
 
 	// Apply the customization rules if required.
 	if config != nil {
-		if config.BlockOverrides != nil && config.BlockOverrides.Number.ToInt().Uint64() == h.Number.Uint64()+1 {
+		if config.BlockOverrides != nil && config.BlockOverrides.Number != nil && config.BlockOverrides.Number.ToInt().Uint64() == h.Number.Uint64()+1 {
 			// Overriding the block number to n+1 is a common way for wallets to
 			// simulate transactions, however without the following fix, a contract
 			// can assert it is being simulated by checking if blockhash(n) == 0x0 and
```
