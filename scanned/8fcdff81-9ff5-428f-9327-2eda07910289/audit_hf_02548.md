# [M] Using uint96 to store balances is incompatible for tokens with low value or high decimals

## Summary
Severity: Medium
Contest weight: 0.5958
Dataset id: 13555
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Throughout the codebase, uint96 is used to store token balances. An example of this would be using a160u96 to store constituents, with the upper 96 bits for the token balance and the lower 160 bits for the token address.
However, uint96 will be too small for tokens with high decimals or low value. type(uint96).max is around 7e28, which can overflow in realistic scenarios.
For example, consider SHIB, which has 18 decimals and a current price of $0.000009714. To calculate how much USD worth of SHIB would overflow uint96:
type(uint96).max / 1e18 * 0.000009714 = 769622
As seen from above, an amount of SHIB worth more than $770K would overflow uint96. This is a problem in several parts of the codebase.
Firstly, when depositing reserve using Index.deposit(), CurrencyLib.selfDeposit() is called, which contains an unsafe cast of the amount transferred in to uint96:
```solidity
uint256 _balance = token.balanceOf(address(this));
token.safeTransferFrom(msg.sender, address(this), amount);
// safe cast, transferred amount is <= 2^96-1
deposited = uint96(token.balanceOf(address(this)) - _balance);
```
If the reserve currency was SHIB and the user transferred in more than $770K worth of SHIB, token.balanceOf(address(this)) - _balance would be more than uint96. The unsafe cast would then overflow, causing the user to lose nearly all of his deposited amount.
The same problem exists in Index.depositWithCommand(), since it uses an unsafe cast in IndexCommandsLib.depositWithCommand():
```solidity
deposited = uint96(reserve.balanceOfSelf() - reserveBefore);
```
Secondly, due to the use of uint96 to represent balances throughout the codebase, such as in OrderBook.sol and AnatomyValidationLib.sol, the rebalancing process could revert if a constituent balance ends up becoming larger than uint96.

## Recommendation
In CurrencyLib.selfDeposit() and IndexCommandsLib.depositWithCommand(), consider using safeCastTo96() instead of performing unsafe casts:
```diff
// safe cast, transferred amount is <= 2^96-1
- deposited = uint96(token.balanceOf(address(this)) - _balance);
+ deposited = (token.balanceOf(address(this)) - _balance).safeCastTo96();
- deposited = uint96(reserve.balanceOfSelf() - reserveBefore);
+ deposited = (reserve.balanceOfSelf() - reserveBefore).safeCastTo96();
```
This ensures that Index.deposit() and Index.depositWithCommand() will revert if a user attempts to deposit more than type(uint96).max tokens.
Additionally, to ensure that rebalancing does not revert unexpectedly, consider not using tokens with high decimals or low prices as constituents.
