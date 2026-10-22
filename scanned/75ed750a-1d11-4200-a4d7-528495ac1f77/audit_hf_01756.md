# [M] Processing of initial balances

## Summary
Severity: Medium
Contest weight: 0.6017
Dataset id: 9638
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LiFi code bases contains two similar source files: Swapper.sol and SwapperV2.sol. One of the differences is the processing of msg.value for native tokens, see pieces of code below. The implementation of SwapperV2.sol sends previously available native token to the msg.sender. The following is exploit example. Assume that:
• the LiFi Diamond contract contains 0.1 ETH.
• a call is done with msg.value == 1 ETH.
• and _swapData[0].fromAmount == 0.5 ETH, which is the amount to be swapped. Option 1 Swapper.sol: initialBalances == 1.1 ETH - 1 ETH == 0.1 ETH. Option 2 SwapperV2.sol: initialBalances == 1.1 ETH. After the swap getOwnBalance() is 1.1 - 0.5 == 0.6 ETH. Option 1 Swapper.sol: returns 0.6 - 0.1 = 0.5 ETH. Option 2 SwapperV2.sol: returns 0.6 ETH (so includes the previously present ETH).
Note: the implementations of noLeftovers() are also different in Swapper.sol and SwapperV2.sol. Note: this is also related to the issue "Pulling tokens by LibSwap.swap() is counterintuitive", because the ERC20 are pulled in via LibSwap.swap(), whereas the msg.value is directly added to the balance.
As there normally shouldn’t be any token in the LiFi Diamond contract the risk is limited.
```solidity
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
```
```solidity
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
The following functions do a comparable processing of msg.value for the initial balance:
• swapAndCompleteBridgeTokensViaStargate() of Executor.sol
• swapAndCompleteBridgeTokens() of Executor.sol
• swapAndExecute() of Executor.sol
• swapAndCompleteBridgeTokens() of XChainExecFacet
```solidity
if (!LibAsset.isNativeAsset(transferredAssetId)) {
    ...
} else {
    startingBalance = LibAsset.getOwnBalance(transferredAssetId) - msg.value;
}
```
However in Executor.sol function swapAndCompleteBridgeTokensViaStargate() isn’t optimal for ERC20 tokens because ERC20 tokens are already deposited in the contract before calling this function.
```solidity
function swapAndCompleteBridgeTokensViaStargate(... ) ... {
    ...
    if (!LibAsset.isNativeAsset(transferredAssetId)) {
        startingBalance = LibAsset.getOwnBalance(transferredAssetId); // doesn't correct for initial balance
    } else {
        ...
    }
}
```
So assume:
• 0.1 ETH was in the contract.
• 1 ETH was added by the bridge.
• 0.5 ETH is swapped.
Then the StartingBalance is calculated to be 0.1 ETH + 1 ETH == 1.1 ETH. So no funds are returned to the receiver as the end balance is 1.1 ETH - 0.5 ETH == 0.6 ETH, is smaller than 1.1 ETH. Whereas this should have been (1.1 ETH - 0.5 ETH) - 0.1 ETH == 0.5 ETH.

## Recommendation
First implement the suggestions of "Pulling tokens by LibSwap.swap() is counterintuitive".
Also consider implementing the suggestions of "Consider using wrapped native token".
Also consider whether any tokens left in the LiFi Diamond and the Executor should be taken into account.
• If they are: use the correction with msg.value everywhere in function swapAndCompleteBridgeTokensViaStargate() of Executor.sol code, make a correction of the initial balance with the received tokens.
• If not: then the initial balances are not relevant and fetchBalances() and the comparable code in other functions can be removed.
Also see "Processing of end balances". Also see "Integrate all variants of _executeAndCheckSwaps()".
