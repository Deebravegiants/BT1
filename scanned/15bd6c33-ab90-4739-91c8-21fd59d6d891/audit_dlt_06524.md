# [H] Rebalancing : `updateWeights` could revert to due to strict check for swap. This would impact the timely rebalancing.

## Summary
Severity: High
Chain: Smart contract
Component: Velvet-Capital
Published: 2024-06-23
Source: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/61
Type: hats-finding

## Details
**Github username:** @aktech297
**Twitter username:** kaka
**Submission hash (on-chain):** 0xd114959c5e80ef86a2e0524d93f295ab15058232187ff60e4e9e1d37e37c0daf
**Severity:** high

**Description:**
**Description**\

The function [updateWeights](https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/blob/aa47c9ff85bcc2bede62978c3895668b549da125/contracts/rebalance/Rebalancing.sol#L63-L81) in the Rebalancing contract is called by the assetmanager to update the weights.

During the process,

1. Funds pulled form the vault to the swap handler for sell token .
2.  doing swap using the [EnsoHandler](https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/blob/aa47c9ff85bcc2bede62978c3895668b549da125/contracts/handler/ExternalSwapHandler/EnsoHandler.sol#L33) contract.
3. checking whether any leftover token in the hanlder contract. if so revert the update weight call.
4. verify the token balance in the vault.

In the above process, the step 4 is too strict. Practically it is not possible to swap all the token amounts. some dust will be left over.

There are array of tokens involved for swap and update.

It is possible that for anyone token, all the amount may not be used for swap. so the swap handler would left our with dust amount. So, the check done in step 3 would cause the revert of the operation.

**The other case which might be concerning is,**

The swap hanlder already funded a small amount by somebody else just before calling the `updateWeights`

if we look at the calldata for swap, it would contain the input and output token address, input and output token amount and slippage parameters.

As said above, if the hanlder is funded with dust amount already, then it will have more than the input amount wihch is encoded in the calldata.

So, swap halder certainly will left out with some funds after swap.

This will cause continous DOS when updating the weights.

**Impact**\

Hardly few times, the token swap done fully. most of the time some dust will remain in handler. this will cause unexpected revert during the update weights process.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/61_
