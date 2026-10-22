# [M] Return data from the external call not veri-

## Summary
Severity: Medium
Contest weight: 0.5942
Dataset id: 20004
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The deposit and redemption functions did not verify the return data from the external call, which might cause the contract to wrongly assume that the deposit/redemption went well although the action has actually failed in the background.
acts/internal/balances/protocols/GenericToken.sol#L63
File: GenericToken.sol
```solidity
function executeLowLevelCall(
    address target,
    uint256 msgValue,
    bytes memory callData
) internal {
    (bool status, bytes memory returnData) = target.call{value: msgValue}(callData);
    require(status, checkRevertMessage(returnData));
}
```
When the external call within the GenericToken.executeLowLevelCall function reverts, the status returned from the .call will be false. In this case, Line 69 above will revert.
acts/internal/balances/TokenHandler.sol#L375
File: TreasuryAction.sol
```solidity
for (uint256 j; j < depositData.targets.length; ++j) {
    // This will revert if the individual call reverts.
    GenericToken.executeLowLevelCall(
        depositData.targets[j],
        depositData.msgValue[j],
        depositData.callData[j]
    );
}
```
For deposit and redeem, Notional assumes that all money markets will revert if the deposit/mint and redeem/burn has an error. Thus, it does not verify the return data
However, this is not always true due to the following reasons:
• Some money markets might not revert when errors occur but instead return false (0). In this case, the current codebase will wrongly assume that the deposit/redemption went well although the action has failed.
• Compound might upgrade its contracts to return errors instead of reverting in the future.
The gist of prime cash is to integrate with multiple markets. Thus, the codebase should be written in a manner that can handle multiple markets. Otherwise, the contract will wrongly assume that the deposit/redemption went well although the action has actually failed in the background, which might potentially lead to some edge cases where assets are sent to the users even though the redemption fails.

## Recommendation
Consider checking the returnData to ensure that the external money market different. Some protocols return 1 on a successful action, while Compound return zero (NO_ERROR).
