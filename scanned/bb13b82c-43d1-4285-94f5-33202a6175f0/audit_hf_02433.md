# [H] Proper Reallocation Logic in _processWithdraw()

## Summary
Severity: High
Contest weight: 0.6362
Dataset id: 13053
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For gas efficiency, the Spool protocol has a guarded DoHardWork process to interact with external protocols. In particular, this process aggregates many actions together to act in an optimized manner with special considerations for flexible support of external protocols and reduced gas cost. While analyzing the reallocation-related logic, we notice the current implementation needs to be improved. To elaborate, we show below the related _processWithdraw() function. As the name indicates, this function is used to withdraw assets from the current set of strategies. After necessary optimization on the concurrent deposits and withdraws, this routine further redistributes the withdrawn assets to other strategies for immediate deposits. However, our analysis shows that it incorrectly provides the arguments for the redistribution. Specifically, it takes four arguments and the last one is withdrawData.reallocationProportions[withdrawData.stratIndexes[stratIndex]], which should be withdrawData.reallocationProportions[stratIndex]!
```solidity
function _processWithdraw(
    ReallocationWithdrawData memory withdrawData,
    address[] memory allStrategies,
    PriceData[] memory spotPrices
) private {
    ReallocationShares memory reallocation = _optimizeReallocation(withdrawData, spotPrices);
    // go over withdrawals
    for (uint256 i = 0; i < withdrawData.stratIndexes.length; i++) {
        uint256 stratIndex = withdrawData.stratIndexes[i];
        address stratAddress = allStrategies[stratIndex];
        Strategy storage strategy = strategies[stratAddress];
        require(!strategy.isInDepositPhase, "SWP");
        uint128 withdrawnReallocationRecieved;
        uint128 sharesToWithdraw = reallocation.totalSharesWithdrawn[stratIndex]
            - reallocation.optimizedShares[stratIndex];
        ProcessReallocationData memory processReallocationData =
            ProcessReallocationData(
                sharesToWithdraw,
                reallocation.optimizedShares[stratIndex],
                reallocation.optimizedWithdraws[stratIndex]
            );
        // withdraw / returns non-optimized withdrawn amount
        withdrawnReallocationRecieved = _doHardWorkReallocation(
            stratAddress,
            withdrawData.slippages[stratIndex],
            processReallocationData
        );
        // redistribute withdrawn to other strategies
        _depositRedistributedAmount(
            withdrawData.stratIndexes[stratIndex],
            reallocation.totalSharesWithdrawn[stratIndex],
            withdrawnReallocationRecieved,
            reallocation.optimizedWithdraws[stratIndex],
            allStrategies,
            withdrawData.reallocationProportions[withdrawData.stratIndexes[stratIndex]]
        );
        _updatePending(stratAddress);
        strategy.isInDepositPhase = true;
    }
}
```

## Recommendation
Correct the above routine for proper reallocation of withdrawn assets to current strategies.
