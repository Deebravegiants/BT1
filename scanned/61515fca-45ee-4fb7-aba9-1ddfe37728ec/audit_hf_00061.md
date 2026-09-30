# [H] H-02 | Liquidation Rewards Sent To The Rebalancer Will Be Lost

## Summary
Severity: High
Contest weight: 0.1968
Dataset id: 137
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Rebalancer contract implements the function initiateClosePosition which is responsible for closing a portion of the current Rebalancer position within the UsdnProtocol, based on a user's deposit. This function makes an external call to _usdnProtocol.initiateClosePosition. During this external call, where the Rebalancer contract acts as the caller, one or more liquidity ticks may be liquidated. If liquidation occurs, the Rebalancer contract will receive wstETH tokens as a reward. However, these wstETH tokens are not forwarded to the original caller of rebalancer.initiateClosePosition and instead remain trapped within the Rebalancer contract, where they will be permanently inaccessible.

## Recommendation
Consider tracking the wstETH balance of the Rebalancer contract before and after the _usdnProtocol.initiateClosePosition call. If the wstETH balance was increased after the call, send the difference of wstETH tokens to the rebalancer.initiateClosePosition caller.
