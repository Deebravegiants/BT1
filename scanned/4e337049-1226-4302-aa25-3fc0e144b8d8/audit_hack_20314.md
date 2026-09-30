# [H] 5.1.1 Receiverdoesn't always reset allowance

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** Receiver.sol#L224-L
**Description:** The function_swapAndCompleteBridgeTokens()ofReceiverreset the approval to the executor at
the end of an ERC20 transfer. However it there is insufficient gas then the approval is not reset.
This allows the executor to access any tokens (of the same type) left in theReceiver.

```
function _swapAndCompleteBridgeTokens(...) ... {
...
if (LibAsset.isNativeAsset(assetId)) {
...
} else {// case 2: ERC20 asset
...
token.safeIncreaseAllowance(address(executor), amount);
if (reserveRecoverGas && gasleft() < _recoverGas) {
token.safeTransfer(receiver, amount);
...
return;// no safeApprove 0
}
try executor.swapAndCompleteBridgeTokens{...} ...
token.safeApprove(address(executor), 0);
}
}
```
**Recommendation:** Only increase the allowance if sufficient gas is available, for example in the following way
function _swapAndCompleteBridgeTokens(...) ... {
...
if (LibAsset.isNativeAsset(assetId)) {
...
} else { // case 2: ERC20 asset
...

- token.safeIncreaseAllowance(address(executor), amount);
    if (reserveRecoverGas && gasleft() < _recoverGas) {
       token.safeTransfer(receiver, amount);
       ...
       return;
    }
+ token.safeIncreaseAllowance(address(executor), amount);
    try executor.swapAndCompleteBridgeTokens{...} ...
    token.safeApprove(address(executor), 0);
}
}

**LiFi:** Fixed in PR 247.
**Spearbit:** Verified.
