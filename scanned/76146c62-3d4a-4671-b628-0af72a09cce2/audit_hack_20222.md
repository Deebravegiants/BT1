# [H] 5.2.3 allowance()doesn’t limitwithdraw()s

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** PermissiveWithdrawalValidator.sol#L17-L27, IWithdrawalValidator.sol, AeraVaultV1.sol#L456-L
**Description:** Theallowance()function is meant to limit withdraw amounts. However,allowance()can only read
and not alter state because its visibility is set toview. Therefore, thewithdraw()function can be called on demand
until the entire Vault/Pool balance has been drained, rendering theallowance()function ineffective.
function withdraw(uint256[] calldata amounts) ... {
...
uint256[] memory allowances = validator.allowance();
...
for (uint256 i = 0; i < tokens.length; i++) {
if (amounts[i] > holdings[i] || amounts[i] > allowances[i]) {
revert Aera__AmountExceedAvailable(... );
}
}
}
// can't update state due to view
function allowance() external view override returns (uint256[] memory amounts) {
amounts = new uint256[](count);
for (uint256 i = 0; i < count; i++) {
amounts[i] = ANY_AMOUNT;
}
}

**Recommendation:** Remove theviewkeyword from theallowance()template, e.g. from bothIWithdrawal-
Validator.solandPermissiveWithdrawalValidator.solto be able to update state in future versions ofal-
lowance().
**Gauntlet:** I would say we need an additional callback to the Validator to notify it of actual withdraw amounts. In
case whenallowanceis greater thanholdingsthere is no way for the Validator to know how much of its allowance
was actually used.
