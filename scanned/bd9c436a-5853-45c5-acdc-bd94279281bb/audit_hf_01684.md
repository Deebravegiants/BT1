# [M] RewardRecipientGateway.slashValidator() prevents legacy reward recipient from using the buffer with non-zero _amount

## Summary
Severity: Medium
Contest weight: 0.6647
Dataset id: 9174
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
RewardRecipientGateway.slashValidator() is meant to be called from two addresses - directly by the KEEPER_ROLE, or from the legacy RewardRecipient contract's slashValidator() function. When calling RewardRecipientGateway.slashValidator() with _useBuffer = true, msg.value has to be zero:
```solidity
if (_useBuffer && msg.value > 0) {
    revert Errors.NoETHAllowed();
}
```
However, this check makes it impossible to call RewardRecipient.slashValidator() with _useBuffer = true and a non-zero _amount. When calling this function, RewardRecipient.slashValidator() forwards msg.value + _amount:
```solidity
pirexEth.slashValidator{value: _amount + msg.value}();
```
Therefore, when this check is reached, msg.value will not be 0 if _amount is non-zero, causing this check to fail. As such, the keeper will not be able to dissolve a validator using ETH unstaked from the validator and the buffer, which will be required in scenarios where validators are partially penalized.

## Recommendation
Consider enforcing this check only when slashValidator() is not called through the legacy RewardRecipient contract:
```solidity
if (msg.sender != legacyRewardRecipient && _useBuffer && msg.value > 0) {
    revert Errors.NoETHAllowed();
}
```
