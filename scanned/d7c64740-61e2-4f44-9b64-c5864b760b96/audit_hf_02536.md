# [H] depositWithCommand() undercounts deposited when reserve is ETH

## Summary
Severity: High
Contest weight: 0.7890
Dataset id: 13536
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
IndexCommandsLib.depositWithCommand() has the following logic:
1. Records the index's current reserve and currency balance:
```solidity
uint256 reserveBefore = reserve.balanceOfSelf();
uint256 balanceBefore = commandParams.currency.balanceOfSelf();
if (commandParams.currency.isNative()) balanceBefore -= msg.value;
```
2. Transfers currency from the user into the contract and executes user-specified commands:
```solidity
commandParams.currency.selfDeposit(params.amount);
CommandLib.callCommand(
    commandParams.command,
    params.config.shared.metadata,
    CommandLib.BalanceState(commandParams.currency, balanceBefore)
);
```
3. Calculates deposited as the difference between the reserve balance after and the recorded reserve balance:
```solidity
if (commandParams.currency.balanceOfSelf() < balanceBefore) revert InvalidDepositData();
deposited = uint96(reserve.balanceOfSelf() - reserveBefore);
```
Since it is possible for reserve or currency to be native tokens, msg.value is subtracted from balanceBefore when commandParams.currency is native tokens. This ensures that the difference between commandParams.currency.balanceOfSelf() and balanceBefore afterwards will include msg.value. However, msg.value is not subtracted from reserveBefore, which means that any ETH sent along with the call will be included in reserveBefore. Consequently, the ETH sent will then be excluded from deposited, which is problematic as deposited represents the amount of funds deposited by the user into the index. This will undercount the user's deposit when reserve is native tokens, for example:
• Assume that reserve is ETH, and a user wants to deposit 1 ETH and 2000 USDC in one call.
• He calls Index.depositWithCommand() with:
  – msg.value = 1 ether
  – commandParams.currency as USDC, and params.amount = 2000e6
• In IndexCommandsLib.depositWithCommand():
  – reserveBefore = 1 ether, since it includes msg.value.
  – 2000 USDC is transferred into the contract and swapped to 1 ETH.
  – Afterwards, reserve.balanceOfSelf() = 2 ether, so deposited = 1 ether.
• As a result, his deposit is recorded as only 1 ETH, causing him to lose the other 1 ETH.

## Recommendation
Subtract msg.value from reserveBefore when reserve is ETH:
```diff
uint256 reserveBefore = reserve.balanceOfSelf();
uint256 balanceBefore = commandParams.currency.balanceOfSelf();
+ if (reserve.isNative()) reserveBefore -= msg.value;
if (commandParams.currency.isNative()) balanceBefore -= msg.value;
```
