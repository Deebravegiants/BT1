# [M] _executeSwaps of Executor.sol doesn’t have a whitelist

## Summary
Severity: Medium
Contest weight: 0.4378
Dataset id: 9628
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
The function _executeSwaps() of Executor.sol doesn’t have a whitelist, whereas _executeSwaps()
of SwapperV2.sol does have a whitelist. Calling arbitrary addresses is dangerous. For example, unlimited al-
lowances can be set to allow stealing of leftover tokens in the Executor contract. Luckily, there wouldn’t normally
be allowances set from users to the Executor.sol so the risk is limited.
Note: also see "Too generic calls in GenericBridgeFacet allow stealing of tokens"
contract Executor is IAxelarExecutable, Ownable, ReentrancyGuard, ILiFi {
function _executeSwaps(... ) ... {
for (uint256 i = 0; i < _swapData.length; i++) {
if (_swapData[i].callTo == address(erc20Proxy)) revert UnAuthorized(); // Prevent calling
ERC20 Proxy directly
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
```

## Recommendation
Reuse the code of SwapperV2.sol. Note: Having a whitelist also makes sure erc20Proxy
won’t be called.
