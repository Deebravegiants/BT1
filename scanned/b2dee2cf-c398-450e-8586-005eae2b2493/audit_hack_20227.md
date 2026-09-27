# [M] 5.3.5 Fee on transfer can block several functions

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** AeraVaultV1.sol#L456-L
**Description:** Some tokens have a fee on transfer, for example USDT. Usually such fee is not enabled but could be
re-enabled at any time. With this fee enabled thewithdrawFromPool()function would receive slightly less tokens
than theamountsrequested from Balancer causing the nextsafeTransfer()call to fail because there are not
enough tokens inside the contract. This meanswithdraw()calls will fail.
Functionsdeposit()andcalculateAndDistributeManagerFees()can also fail because they have similar code.
Note: The functionreturnFunds()is more robust and can handle this problem. Note: The problem can be
alleviated by sending additional tokens directly to the Aera Vault contract to compensate for fees, lowering the
severity of the problem to medium.
function withdraw(uint256[] calldata amounts) ... {
...
withdrawFromPool(amounts);// could get slightly less than amount with a fee on transfer
...
for (uint256 i = 0; i < amounts.length; i++) {
if (amounts[i] > 0) {
tokens[i].safeTransfer(owner(), amounts[i]);// could revert it the full amounts[i] isn't
,! available
...
} ...
}
}

**Recommendation:** Check thebalanceOf()tokens before and after asafeTransfer()orsafeTransferFrom().
Use the difference as the amount of tokens sent/received.
