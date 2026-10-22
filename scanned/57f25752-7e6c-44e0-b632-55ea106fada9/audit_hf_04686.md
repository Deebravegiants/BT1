# [H] Off-chain health check for withdrawal and the

## Summary
Severity: High
Contest weight: 0.6411
Dataset id: 22450
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
The protocol logic requires off-chain app to check the subaccount health before executing on-chain withdrawals. However, on-chain withdrawal logic ignores unrealized profit and loss as it doesn't check user health. Even though off-chain logic should prevent situations when user becomes unhealthy after withdrawal, there are certain scenarios possible when incorrect withdrawals can still happen.
That is, if account state changes between offchain calculation and on-chain transaction execution, which can happen for a variety of reasons outside of the offchain app control (pending withdrawal executed on-chain by the user, on-chain permissionless liquidation or some accounting bug happening just before the ingresso withdrawal action).
The other operations (such as MatchOrder and ForceSwap) do not check account health either and are vulnerable as well, but the withdrawal operation is the most severe one.
OrderDispatcher action to withdraw calls Ciao.executeWithdrawal function, which only checks that quantity to withdraw is not larger than user balance before proceeding with withdrawal:
if (quantityE18 == 0 || quantityE18 > balances[subAccount][asset]) revert Errors.WithdrawQuantityInvalid();
// if the caller is the orderDispatch then execute the withdrawal normally
if (msg.sender == _orderDispatch()) {
_withdraw(account, subAccount, quantityE18, asset);
} else if (msg.sender == account) {
The _withdraw internal function simply reduces user balance without any account health checks:
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
This means that off-chain app must ensure user account is healthy after the action, as there is no such on-chain check. However, it's still possible that user account becomes unhealthy or even in bad debt after withdrawal even if off-chain app makes sure it is healthy:
• When several actions are chained together in the same ingresso call, intermediate results between these actions might be tricky to calculate, so if for whatever reason the calculations are incorrect, the withdrawal might be allowed off-chain while account will become unhealthy on-chain
• Any on-chain bug (such as the other reported bug with incorrect taker filled quantities applied multiple times when matching with multiple makers) which provides unexpected user positions will become more severe, because from a harmless "causes unexpected position" bug it becomes "causes bad debt and loss of funds" bug.
• Any unexpected transaction, which comes before the ingresso transaction, which modifies the user state unexpectedly, which off-chain app didn't expect and thus didn't include in the user account health calculations. Currently, this can be on-chain liquidation if premissionless liquidations are on, and also executeWithdrawal action by the user (if request was pending and not executed by the offchain app with a certain timeout, then user requested off-chain withdrawal, and then front-runs ingresso withdrawal transaction with user-initiated executeWithdrawal transaction, withdrawing twice).
It's possible that user account becomes unhealthy (liquidatable) or in a bad debt in certain situations. Some harmless on-chain bugs can become more severe as unexpected user state will cause liquidations and/or bad debt and loss of funds for all users of the protocol.
```

## Recommendation
Do on-chain account health check after the withdrawal, because off-chain app can not ensure that account is healthy after withdrawal in 100% of cases due to unepected things which are out of off-chain app control.
Additionally, do the on-chain account health check after MatchOrder and ForceSwap operations.
