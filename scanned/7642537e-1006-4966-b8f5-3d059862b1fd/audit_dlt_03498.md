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

One possible error that can be returned in `CheckAndUpdateCctxGasPrice` is insufficient balance in the `GasStabilityPool`.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/abci.go#L107-L112
```go
	if err := k.fungibleKeeper.WithdrawFromGasStabilityPool(ctx, chainID, additionalFees.BigInt()); err != nil {
		return math.ZeroUint(), math.ZeroUint(), cosmoserrors.Wrap(
			types.ErrNotEnoughFunds,
			fmt.Sprintf("cannot withdraw %s from gas stability pool", additionalFees.String()),
		)
	}
```

The `GasStabilityPool` is only replenished when an outbound transaction is finalized.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L131-L136
```go
	// Fund the gas stability pool with the remaining funds
	if err := k.FundGasStabilityPoolFromRemainingFees(ctx, *cctx.GetCurrentOutTxParam(), msg.OutTxChain); err != nil {
		log.Error().Msgf(
			"VoteOnObservedOutboundTx: CCTX: %s Can't fund the gas stability pool with remaining fees %s", cctx.Index, err.Error(),
		)
	}
```

Therefore, during the execution of `IterateAndUpdateCctxGasPrice`, outbound `cctx` may not have been finalized yet, leading to a possible scenario of insufficient balance in the `GasStabilityPool`, which is an expected occurrence. However, in the current implementation, if the `GasStabilityPool` of one chain is insufficient, the function directly returns, and the remaining chains in the loop are not processed. For other chains, the `GasStabilityPool` might be sufficient, and they should not be neglected.

## Tools Used
vscode
## Recommended Mitigation Steps
If `CheckAndUpdateCctxGasPrice` returns an error, skip the loop for that `cctx` and continue with the outer loop for the chain.


## Assessed type

Loop
