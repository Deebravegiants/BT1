# [?] Prevent panic on missing chains (#17820)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2025-05-21
Source: https://github.com/smartcontractkit/chainlink/commit/74d8d3e00b5f6fabdd1b41135ccd4ec2f39df8a1
Type: security-commit

## Details
Prevent panic on missing chains (#17820)

Prevents panic on missing chains

## Patch
### deployment/keystone/changeset/view.go
```diff
@@ -126,7 +126,8 @@ func getContractsPerChain(e deployment.Environment) (contractsPerChain, error) {
 	for _, contractAddress := range contractAddresses {
 		chain, ok := e.Chains[contractAddress.ChainSelector]
 		if !ok {
-			errs = errors.Join(errs, fmt.Errorf("chain with selector %d not found", contractAddress.ChainSelector))
+			// the chain might not be present in the environment if it was removed due to RPC instability
+			e.Logger.Warnf("chain with selector %d not found, skipping contract address %s", contractAddress.ChainSelector, contractAddress.Address)
 			continue
 		}
 
```
