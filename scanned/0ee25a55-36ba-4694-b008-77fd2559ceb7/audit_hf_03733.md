# [M] when execute deposit fails, cancel deposit and keeper loses execution fee

## Summary
Severity: Medium
Contest weight: 0.4209
Dataset id: 19866
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When execute deposit fails, the deposit will be automatically cancelled. However, since executeDeposit has taken up a portion of the execution fee, execution fee left for cancellation might be little and keeper will lose out on execution fee.
In executeDeposit when an error is thrown, _handleDepositError is called.
_handleDepositError(
key,
startingGas,
reasonBytes
);
Notice that in _handleDepositError that cancelDeposit is called which will pay execution fee to the keeper. However, since the failure can have failed at the late stage of executeDeposit, the execution fee left for the cancellation will be little for the keeper.
```solidity
function _handleDepositError(
bytes32 key,
uint256 startingGas,
bytes memory reasonBytes
) internal {
(string memory reason, /* bool hasRevertMessage */) =
ErrorUtils.getRevertMessage(reasonBytes);
bytes4 errorSelector = ErrorUtils.getErrorSelectorFromData(reasonBytes);
if (OracleUtils.isEmptyPriceError(errorSelector)) {
ErrorUtils.revertWithCustomError(reasonBytes);
}
DepositUtils.cancelDeposit(
dataStore,
eventEmitter,
depositVault,
key,
msg.sender,
startingGas,
reason,
reasonBytes
);
}
```
Keeper will lose out on execution fee in the event of a failed deposit.

## Recommendation
Recommend increasing the minimum required execution fee to account for failed deposit and refund the excess to the user when a deposit succeeds.
