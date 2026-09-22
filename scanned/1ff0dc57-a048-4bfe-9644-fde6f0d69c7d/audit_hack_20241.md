# [M] 5.2.14_executeSwapsofExecutor.soldoesn’t have a whitelist

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** Executor.sol#L323-L333, SwapperV2.sol#L67-L81
**Description:** The function_executeSwaps()ofExecutor.soldoesn’t have a whitelist, whereas_executeSwaps()
ofSwapperV2.soldoes have a whitelist. Calling arbitrary addresses is dangerous. For example, unlimited al-
lowances can be set to allow stealing of leftover tokens in theExecutorcontract. Luckily, there wouldn’t normally
be allowances set from users to theExecutor.solso the risk is limited.
Note: also see "Too generic calls inGenericBridgeFacetallow stealing of tokens"
contract Executor is IAxelarExecutable, Ownable, ReentrancyGuard, ILiFi {
function _executeSwaps(... ) ... {
for (uint256 i = 0; i < _swapData.length; i++) {
if (_swapData[i].callTo == address(erc20Proxy)) revert UnAuthorized();// Prevent calling
,! ERC20 Proxy directly
LibSwap.SwapData calldata currentSwapData = _swapData[i];
LibSwap.swap(_lifiData.transactionId, currentSwapData);
}
}
contract SwapperV2 is ILiFi {
function _executeSwaps(... ) ... {
for (uint256 i = 0; i < _swapData.length; i++) {
LibSwap.SwapData calldata currentSwapData = _swapData[i];
if (
!(appStorage.dexAllowlist[currentSwapData.approveTo] &&
appStorage.dexAllowlist[currentSwapData.callTo] &&
appStorage.dexFuncSignatureAllowList[bytes32(currentSwapData.callData[:8])])
) revert ContractCallNotAllowed();
LibSwap.swap(_lifiData.transactionId, currentSwapData);
}
}

Based on the comments of the LiFi project there is also the use case to call more generic contracts, which do not
return any token, e.g., NFT buy, carbon offset. It probably better to create new functionality to do this.
**Recommendation:** Reuse the code ofSwapperV2.sol. Note: Having a whitelist also makes sureerc20Proxy
won’t be called. Note: This also requires adding a management interface for the whitelist, likeDexManager-
Facet.sol. Note: Also see issue "Move whitelist toLibSwap.swap()"
Consider creating additional functionality for non-dex calls. Here whitelists also will be useful.
**LiFi:** LiFi Team claims that they acknowledge the risk but plan to keep this contract open as it is separate from the
main LIFI protocol contract and want to allow developers to call whatever they wish.
**Spearbit:** Acknowledged.
