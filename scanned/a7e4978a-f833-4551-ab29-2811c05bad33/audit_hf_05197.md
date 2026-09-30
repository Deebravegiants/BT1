# [H] Frozen Investor Payout Loss on Resolve

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23307
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Resolving a frozen investor causes all the pending payouts for the entire time the investor was frozen to be lost  

Description: When an investor is frozen, they do not receive payouts while the freeze is active. However, once the sanction is lifted, the investor is entitled to receive the accumulated payouts for the entire duration of the freeze. Resolving a frozen user does not unfreeze the investor before resolving the pending payouts. This means that the payouts of the investor will be calculated up to the payoutIndex at which they were frozen; any subsequent payouts will not be included in the calculation.  

//ChildToken.sol//  
```solidity
function resolveUser(address oldAddress, address newAddress) external nonReentrant restricted {
...
_resolvePay(oldAddress, newAddress); // moves any unclaimed payouts to new account
...
}
```  

//DividendManager.sol//  
```solidity
function _resolvePay(address oldAddress, address newAddress) internal {
//@audit => Payouts as calculated on payoutBalance() from oldAddress are migrated to newAddress
@> _getHolderManagementStorage()._resolvedPay[newAddress] =
SafeCast.toUint128(_claimPayout(oldAddress));,!
emit PaymentResolved(oldAddress, newAddress);
}
function _claimPayout(
address holder
) internal returns (uint256 payoutAmount) {
HolderManagementStorage storage $ = _getHolderManagementStorage();
payoutAmount = payoutBalance(holder);
...
}
```  

```solidity
function payoutBalance(address holder) public returns (uint256) {
...
uint256 payoutAmount;
//@audit => Payouts for frozen investors are paid out up to the index when they were frozen
@> uint16 payRangeStart = rHolderStatus.isFrozen
? rHolderStatus.frozenIndex - 1
: currentPayoutIndex - 1;
...
for (uint16 i = payRangeStart; i >= payRangeEnd; --i) {
...
}
...
}
```  

Given that resolving a user causes the entire balance to be transferred to the new address, the oldAddress will get its user data deleted because on the DividenManager::_updateHolders, the from (oldAddress) won't have any balance, any payouts, nor calculatedPayout, both of them were reset to 0 in the call to _claimPayout() triggered from _resolvePay()  

//ChildToken.sol//  
```solidity
function resolveUser(address oldAddress, address newAddress) external nonReentrant restricted {
...
_resolvePay(oldAddress, newAddress); // moves any unclaimed payouts to new account
...
//@audit => Transfer all the balance of the oldAddress
uint256 value = balanceOf(oldAddress);
_validateBalance(false, false, oldAddress, value);
_validateCompliance(false, true, oldAddress, newAddress, value);
@> super._transfer(oldAddress, newAddress, value); // tokens already locked with
_newAccountSameLocks,!
}
```  

This means the new address will receive all the old address tokens, but the payouts for the duration of the freeze on the old address will be lost.

## Recommendation
Add to the ChildToken::resolveUser logic to verify if the oldAddress is frozen; if so, unfreeze it before resolving the pending payments. And, at the end of the execution, consider freezing the new address in case the old address was frozen.
