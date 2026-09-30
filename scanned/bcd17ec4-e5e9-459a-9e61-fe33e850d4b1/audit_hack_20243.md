# [M] 5.2.16 Processing of initial balances

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** Swapper.sol#L22-L38, Swapper.sol#L83-L96, SwapperV2.sol#L22-L39, SwapperV2.sol#L86-L93,
Executor.sol#L143-L149, Executor.sol#L191-L199, Executor.sol#L242-L249, Executor.sol#L338-L345,
XChainExecFacet.sol#L30-L38
**Description:** The LiFi code bases contains two similar source files:Swapper.solandSwapperV2.sol. One of
the differences is the processing ofmsg.valuefor native tokens, see pieces of code below. The implementation of
SwapperV2.solsends previously available native token to themsg.sender.
The following is exploit example. Assume that:

- the LiFi Diamond contract contains 0.1 ETH.
- a call is done withmsg.value == 1 ETH.
- and _swapData[0].fromAmount == 0.5 ETH, which is the amount to be swapped. Option
    1 Swapper.sol:initialBalances == 1.1 ETH - 1 ETH == 0.1 ETH. Option 2SwapperV2.sol: initialBalances
    == 1.1 ETH. After the swapgetOwnBalance()is1.1 - 0.5 == 0.6 ETH. Option 1 Swapper.sol:
    returns0.6 - 0.1 = 0.5 ETH. Option 2SwapperV2.sol: returns 0.6 ETH‘ (so includes the previously
    present ETH).
Note: the implementations ofnoLeftovers()are also different inSwapper.solandSwapperV2.sol. Note: this is
also related to the issue "Pulling tokens byLibSwap.swap()is counterintuitive", because the ERC20 are pulled in
viaLibSwap.swap(), whereas themsg.valueis directly added to the balance.
As there normally shouldn’t be any token in the LiFi Diamond contract the risk is limited.

```
contract Swapper is ILiFi {
function _fetchBalances(...) ... {
...
for (uint256 i = 0; i < length; i++) {
address asset = _swapData[i].receivingAssetId;
uint256 balance = LibAsset.getOwnBalance(asset);
if (LibAsset.isNativeAsset(asset)) {
balances[i] = balance - msg.value;
} else {
balances[i] = balance;
}
}
return balances;
}
}
contract SwapperV2 is ILiFi {
function _fetchBalances(...) ... {
...
for (uint256 i = 0; i < length; i++) {
balances[i] = LibAsset.getOwnBalance(_swapData[i].receivingAssetId);
}
...
}
}
```
The following functions do a comparable processing ofmsg.valuefor the initial balance:

- swapAndCompleteBridgeTokensViaStargate()ofExecutor.sol
- swapAndCompleteBridgeTokens()ofExecutor.sol
- swapAndExecute()ofExecutor.sol
- swapAndCompleteBridgeTokens()ofXChainExecFacet


```
if (!LibAsset.isNativeAsset(transferredAssetId)) {
} else {
startingBalance = LibAsset.getOwnBalance(transferredAssetId) - msg.value;
}
```
However inExecutor.solfunctionswapAndCompleteBridgeTokensViaStargate()isn’t optimal forERC20tokens
becauseERC20tokens are already deposited in the contract before calling this function.
function swapAndCompleteBridgeTokensViaStargate(... ) ... {
if (!LibAsset.isNativeAsset(transferredAssetId)) {
startingBalance = LibAsset.getOwnBalance(transferredAssetId);// doesn't correct for initial
,! balance
} else {
}
}

So assume:

- 0.1 ETH was in the contract.
- 1 ETH was added by the bridge.
- 0.5 ETH is swapped.
Then theStartingBalanceis calculated to be0.1 ETH + 1 ETH == 1.1 ETH. So no funds are returned to the
receiveras the end balance is1.1 ETH - 0.5 ETH == 0.6 ETH, is smaller than1.1 ETH. Whereas this should
have been(1.1 ETH - 0.5 ETH) - 0.1 ETH == 0.5 ETH.
**Recommendation:** First implement the suggestions of "Pulling tokens byLibSwap.swap()is counterintuitive".
Also consider implementing the suggestions of "Consider using wrapped native token".
Also consider whether any tokens left in the LiFi Diamond and the Executor should be taken into account.
- If they are: use the correction with msg.value everywhere in functionswapAndCompleteBridgeTokensViaS-
targate()ofExecutor.solcode, make a correction of the initial balance with the received tokens.
- If not: then the initial balances are not relevant andfetchBalances()and the comparable code in other
functions can be removed.
Also see "Processing of end balances". Also see "Integrate all variants of_executeAndCheckSwaps()".
**LiFi:** Fixed with PR #94.
**Spearbit:** Verified.
