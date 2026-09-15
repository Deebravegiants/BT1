# [M] 5.1.2 Reentrancy inwithdrawExcessCollateral()andwithdrawExcessPayment()functions.

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** Bond.sol#L212, Bond.sol#

**Description:** withdrawExcessCollateral()andwithdrawExcessPayment()enable the caller to withdraw excess
collateral and payment tokens respectively. Both functions are guarded by anonlyOwnermodifier, limiting their
access to the owner of the contract.

```
function withdrawExcessCollateral(uint256 amount, address receiver) external onlyOwner
function withdrawExcessPayment(address receiver) external onlyOwner
```
When transferring tokens, execution flow is handed over to the token contract. Therefore, if a malicious token
manages to call the owner’s address it can also call these functions again to withdraw more tokens than required.

As an example consider the following case where the collateral token’stransferFrom()function calls the owner’s
address:


```
function transferFrom(
address from,
address to,
uint256 amount
) public virtual override returns (bool) {
if (reenter) {
reenter = false;
owner.attack(bond, amount);
}
address spender = _msgSender();
_spendAllowance(from, spender, amount);
_transfer(from, to, amount);
return true;
}
```
and the owner contract has a function:

```
function attack(address _bond, uint256 _amount) external {
IBond(_bond).withdrawExcessCollateral(_amount, address(this));
}
```
WhenwithdrawExcessCollateral()is called byowner, it allows it to withdraw double the amount via reentrancy.

**Recommendation:** Consider applying thenonReentrantmodifier on both of these functions.

**Porter:** Implemented in PR #284.

**Spearbit:** Acknowledged, recommendation has been implemented.
