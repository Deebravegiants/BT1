# [M] 5.2.15 Processing of end balances

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** SwapperV2.sol#L22-L60, Executor.sol#L41-L57, Swapper.sol#L22-L38
**Description:** The contractSwapperV2has the following construction (twice) to prevent using any alreadystart
balance.

- it gets astart balance.
- does an action.
- if theend balance>start balance. then it uses the difference. else (which includesstart balance ==
    end balance) it uses theend balance.
So if the else clause it reached it uses theend balanceand ignores anystart balance. If the action hasn’t
changed the balances thenstart balance == end balanceand this amount is used. When the action has
lowered the balances thenend balanceis also used.
This defeats the code’s purpose.
Note: normally there shouldn’t be any tokens in the LiFi Diamond contract so the risk is limited.
NoteSwapper.solhas similar code.
contract SwapperV2 is ILiFi {
modifier noLeftovers(LibSwap.SwapData[] calldata _swapData, address payable _receiver) {
...
uint256[] memory initialBalances = _fetchBalances(_swapData);
...// all kinds of actions
newBalance = LibAsset.getOwnBalance(curAsset);
curBalance = newBalance > initialBalances[i]? newBalance - initialBalances[i] : newBalance;
...
}
function _executeAndCheckSwaps(...) ... {
...
uint256 swapBalance = LibAsset.getOwnBalance(finalTokenId);
...// all kinds of actions
uint256 newBalance = LibAsset.getOwnBalance(finalTokenId);
swapBalance = newBalance > swapBalance? newBalance - swapBalance : newBalance;
...
}

**Recommendation:** Consider whether any tokens left in the LiFi Diamond should be taken into account.

- If it is then changenewBalancein the else clauses to 0.
- If not then the initial balances are not relevant code can be simplified.
Note:Executor.solandSwapper.solhave comparable code which is different. Note: also see issue "Processing
of initial balances". Note: also see issue "Integrate all variants of_executeAndCheckSwaps()".
**LiFi:** Fixed with PR #94.
**Spearbit:** Verified. Note : It’s still not safe to keep tokens in the LibDiamond contract.
