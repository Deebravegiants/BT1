# [M] 5.2.10 Remaining tokens can be sweeped from the LiFi Diamond or theExecutor

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** Executor.sol#L143-L149, Executor.sol#L191-L199, Executor.sol#L242-L249, Executor.sol#L338-L345
**Description:** The initial balance of (native) tokens in both theLifi Diamondand theExecutorcontract can be
sweeped by all the swap functions in all the bridges, which use the following functions:

- swapAndCompleteBridgeTokensViaStargate()ofExecutor.sol
- swapAndCompleteBridgeTokens()ofExecutor.sol
- swapAndExecute()ofExecutor.sol
- _executeAndCheckSwaps()ofSwapperV2.sol
- _executeAndCheckSwaps()ofSwapper.sol
- swapAndCompleteBridgeTokens()ofXChainExecFacet
Although these functions ...
- swapAndCompleteBridgeTokensViaStargate()ofExecutor.sol
- swapAndCompleteBridgeTokens()ofExecutor.sol
- swapAndExecute()ofExecutor.sol
- swapAndCompleteBridgeTokens()ofXChainExecFacet
have the following code:

```
if (!LibAsset.isNativeAsset(transferredAssetId)) {
startingBalance = LibAsset.getOwnBalance(transferredAssetId);
// sometimes transfer tokens in
} else {
startingBalance = LibAsset.getOwnBalance(transferredAssetId) - msg.value;
}
// do swaps
uint256 postSwapBalance = LibAsset.getOwnBalance(transferredAssetId);
if (postSwapBalance > startingBalance) {
LibAsset.transferAsset(transferredAssetId, receiver, postSwapBalance - startingBalance);
}
```
This doesn’t protect the initial balance of the first tokens, because it can just be part of a swap to another token.
The initial balances of intermediate tokens are not checked or protected.
As there normally shouldn’t be (native) tokens in the LiFi Diamond or theExecutorthe risk is limited. Note: set
the risk to medium as there are other issues in this report that leave tokens in the contracts
Although in practice there is some dust in the LiFi Diamond and theExecutor:

- 0x362fa9d0bca5d19f743db50738345ce2b40ec99f
- 0x46405a9f361c1b9fc09f2c83714f806ff249dae7
**Recommendation:** Consider whether any tokens left in the LiFi Diamond and theExecutorshould be taken into
account.
- If so: for every (intermediate) swap determine initial amount of (native) token and make sure this isn’t
swapped.
- If not: remove the code with thestartingBalance. also analyse all occurances of tokens in the LiFi Diamond
and theExecutorto determine its source.
**LiFi:** Fixed with PR #94.
**Spearbit:** Verified.
