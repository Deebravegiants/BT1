# [H] executeWithdrawal can be called by user after

## Summary
Severity: High
Contest weight: 0.6382
Dataset id: 22447
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
User can initiate withdrawal on-chain via calling Ciao.requestWithdrawal. If the protocol's off-chain app doesn't process this request in time (minimumWithdrawalWaitTime), user can proceed to call Ciao.executeWithdrawal to finish the withdrawal.
The problem is that this function doesn't check any unrealized loss user has, allowing the user to withdraw full balance. If the user has large unrealized loss, this allows to withdraw full balance creating large bad debt for the user and loss of funds for the other protocol users (they won't be able to withdraw everything they've deposited due to bad debt).
When user calls Ciao.executeWithdrawal function, it only checks that the quantity matches the requested quantity and minimumWithdrawalWaitTime has passed:
} else if (msg.sender == account) {
// otherwise check the withdrawal receipt validity
Structs.WithdrawalReceipt memory receipt = withdrawalReceipts[
subAccount
][asset];
// check the quantity being withdrawn is equal to the quantity requested
if (quantityE18 != receipt.quantity) revert Errors.WithdrawQuantityInvalid();
// check the minimum withdrawal wait time has passed
if (
receipt.requestTimestamp + minimumWithdrawalWaitTime >
block.timestamp
) revert Errors.MinimumWaitTimeNotPassed();
_withdraw(account, subAccount, quantityE18, asset);
} else revert Errors.SenderInvalid();
Additionally, the _withdraw internal function simply reduces user balance without any account health checks, the only check is that withdrawn quantity should not be greater than the user's balance (which doesn't include any unrealized profit or loss):
function _withdraw(
address account,
address subAccount,
uint256 quantity,
address asset
) internal {
// The account has the full quantity withdrawn from balance
_changeBalance(subAccount, asset, -int256(quantity));
// if the balance becomes zero then remove the asset from the set
if (balances[subAccount][asset] == 0) {
subAccountAssets[subAccount].remove(asset);
}
uint256 quantityRealDecimals = Commons.convertFromE18(
quantity,
ERC20(asset).decimals()
);
// clear the withdrawal receipt
delete withdrawalReceipts[subAccount][asset];
// Transfer asset to sender
SafeTransferLib.safeTransfer(
ERC20(asset),
account,
quantityRealDecimals
);
}
This means that any user with any unrealized loss can cause bad debt and loss of funds for the other users if off-chain app doesn't do anything for user's withdrawal request, this can happen for a variety of reasons, including:
• user account in not healthy after withdrawal - off-chain app will check this and won't execute the withdrawal, but the user can still force withdraw after withdrawal wait time passes, because the withdrawal request is not cleared;
• off-chain app is down for whatever reason and user simply withdraws whatever he requests ignoring any unrealized loss.
Any user can withdraw more than he should be allowed due to absence of account health check during on-chain withdrawal execution
```

## Recommendation
Re-consider the withdrawal flow. Either use the latest submitted price to check account health, even if it's outdated, or remove the user execution of withdrawal request completely.
