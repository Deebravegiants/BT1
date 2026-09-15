# [M] 5.3.3 safeApproveindepositTokencould revert for non-standard token likeUSDT.

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** AeraVaultV1.sol#L
**Description:** Some non-standard tokens likeUSDTwill revert when a contract or a user tries to approve an al-
lowance when the spender allowance has already been set to a non zero value. In the current code we have
not seen any real problem with this fact because theamountretrieved viadepositToken()is approved send to
the Balancer pool viajoinPool()andmanagePoolBalance(). Balancer transfers the same amount, lowering the
approval to 0 again. However, if the approval is not lowered to exactly 0 (due to a rounding error or another unfore-
seen situation) then the next approval indepositToken()will fail (assuming a token likeUSDTis used), blocking all
further deposits.
Note: Set to medium risk because the probability of this happening is low but impact would be high.
We also should note that OpenZeppelin has officially **deprecated** thesafeApprovefunction, suggesting to use
insteadsafeIncreaseAllowanceandsafeDecreaseAllowance.
**Recommendation:** Adopt a safer approach to cover edge cases such as the abovementionedUSDTtoken and
implement the following solution:
function depositToken(IERC20 token, uint256 amount) internal {
token.safeTransferFrom(owner(), address(this), amount);

- token.safeApprove(address(bVault), amount);
+ uint256 allowance = token.allowance(address(this), address(bVault));
+ if (allowance > 0) {
+ token.safeDecreaseAllowance(address(bVault), allowance);
+ }
+ token.safeIncreaseAllowance(address(bVault), amount);
}

Please note that theamountthat should be used as a parameter forsafeIncreaseAllowanceshould follow the
recommendationswritten in issueFee on transfer can block several functions.
