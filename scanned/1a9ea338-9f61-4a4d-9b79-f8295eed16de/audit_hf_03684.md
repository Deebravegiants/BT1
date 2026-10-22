# [H] Safe can be bricked because threshold is up-

## Summary
Severity: High
Contest weight: 0.7786
Dataset id: 19778
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The safe's threshold is supposed to be set with the lower value of the validSignerCount and the targetThreshold (intended to serve as the maximum). However, the wrong value is used in the call to the safe's function, which in some circumstances can lead to the safe being permanently bricked.
In reconcileSignerCount(), the valid signer count is calculated. We then create a value called newThreshold, and set it to the minimum of the valid signer count and the target threshold. This is intended to be the value that we update the safe's threshold with.
```solidity
if (validSignerCount <= target && validSignerCount != currentThreshold) {
    newThreshold = validSignerCount;
} else if (validSignerCount > target && currentThreshold < target) {
    newThreshold = target;
}
```
However, there is a typo in the contract call, which accidentally uses validSignerCount instead of newThreshold.
The result is that, if there are more valid signers than the targetThreshold that was set, the threshold will be set higher than intended, and the threshold check in checkAfterExecution() will fail for being above the max, causing all safe transactions to revert.
is a gate with a single hat signer, and the eligibility module for the hat doesn't have a way to turn off eligibility, there will be no way to reduce the number of signers. If this number is greater than maxSigners, there is no way to increase targetThreshold sufficiently to stop the reverting.
The result is that the safe is permanently bricked, and will not be able to perform any transactions.
All transactions will revert until validSignerCount can be reduced back below targetThreshold, which re

## Recommendation
Change the value in the function call from validSignerCount to newThreshold.
```solidity
if (newThreshold > 0) {
    bytes memory data = abi.encodeWithSignature("changeThreshold(uint256)", newThreshold);
    bool success = safe.execTransactionFromModule(
        address(safe), // to
        0, // value
        data, // data
        Enum.Operation.Call // operation
    );
    if (!success) {
        revert FailedExecChangeThreshold();
    }
}
```
