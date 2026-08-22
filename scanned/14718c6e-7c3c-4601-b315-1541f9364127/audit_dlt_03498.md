# [M] When updating gas, if one chain fails, the others should continue to be updated instead of being skipped.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-05
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/178
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/abci.go#L34-L53
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/abci.go#L107-L112


# Vulnerability details

## Impact
Due to an expected error occurring in one chain, the gas for the other chains cannot be updated.

## Proof of Concept
`IterateAndUpdateCctxGasPrice` is used to periodically update the `gas price` of `cctx`. It iterates through all `cctx` in all chains to update their `gas price`.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/abci.go#L34-L53
```go
	// iterate all chains' pending cctx
	chains := common.DefaultChainsList()
	for _, chain := range chains {
		res, err := k.CctxAllPending(sdk.UnwrapSDKContext(ctx), &types.QueryAllCctxPendingRequest{
			ChainId: chain.ChainId,
		})
		if err != nil {
			return err
		}

		// iterate through all pending cctx
		for _, pendingCctx := range res.CrossChainTx {
			if pendingCctx != nil {
				_, _, err := k.CheckAndUpdateCctxGasPrice(ctx, *pendingCctx, gasPriceIncreaseFlags)
				if err != nil {
					return err
				}
			}
		}
	}
```


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/178_
