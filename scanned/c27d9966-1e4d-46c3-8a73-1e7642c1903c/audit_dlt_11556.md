# [?] Fix panic on missing base gas fee. (#214)

## Summary
Severity: Unknown
Chain: MEV
Component: flashbots/suave-geth
Published: 2024-02-28
Source: https://github.com/flashbots/suave-geth/commit/b694404a3fdb0b4da53bd6239c9dcc4003dc5208
Type: security-commit

## Details
Fix panic on missing base gas fee. (#214)

## Patch
### core/vm/contracts_suave_eth.go
```diff
@@ -222,6 +222,8 @@ func (b *suaveRuntime) buildEthBlock(blockArgs types.BuildBlockArgs, dataID type
 
 	payload, err := executableDataToDenebExecutionPayload(envelope.ExecutionPayload)
 	if err != nil {
+		log.Warn("failed to generate execution payload from executable data",
+			"reason", err)
 		return nil, nil, fmt.Errorf("could not format execution payload as deneb payload: %w", err)
 	}
 
@@ -337,7 +339,9 @@ func executableDataToDenebExecutionPayload(data *dencun.ExecutableData) (*specDe
 	}
 
 	baseFeePerGas := new(uint256.Int)
-	if baseFeePerGas.SetFromBig(data.BaseFeePerGas) {
+	if data.BaseFeePerGas == nil {
+		return nil, errors.New("base fee per gas: not provided")
+	} else if baseFeePerGas.SetFromBig(data.BaseFeePerGas) {
 		return nil, errors.New("base fee per gas: overflow")
 	}
 
```
