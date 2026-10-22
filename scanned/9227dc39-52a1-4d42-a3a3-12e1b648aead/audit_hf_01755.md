# [M] Processing of end balances

## Summary
Severity: Medium
Contest weight: 0.4310
Dataset id: 9629
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
The contract SwapperV2 has the following construction (twice) to prevent using any already start
balance.
• it gets a start balance.
• does an action.
• if the end balance > start balance. then it uses the difference. else (which includes start balance ==
end balance) it uses the end balance.
So if the else clause it reached it uses the end balance and ignores any start balance. If the action hasn’t
changed the balances then start balance == end balance and this amount is used.
When the action has
lowered the balances then end balance is also used.
This defeats the code’s purpose.
Note: normally there shouldn’t be any tokens in the LiFi Diamond contract so the risk is limited.
Note Swapper.sol has similar code.
contract SwapperV2 is ILiFi {
modifier noLeftovers(LibSwap.SwapData[] calldata _swapData, address payable _receiver) {
...
uint256[] memory initialBalances = _fetchBalances(_swapData);
... // all kinds of actions
newBalance = LibAsset.getOwnBalance(curAsset);
curBalance = newBalance > initialBalances[i] ? newBalance - initialBalances[i] : newBalance;
...
}
function _executeAndCheckSwaps(...) ... {
...
uint256 swapBalance = LibAsset.getOwnBalance(finalTokenId);
... // all kinds of actions
uint256 newBalance = LibAsset.getOwnBalance(finalTokenId);
swapBalance = newBalance > swapBalance ? newBalance - swapBalance : newBalance;
...
}
```

## Recommendation
Consider whether any tokens left in the LiFi Diamond should be taken into account.
• If it is then change newBalance in the else clauses to 0.
• If not then the initial balances are not relevant code can be simplified.
