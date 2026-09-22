# [C] 5.1.7 Fund duplication via ERC20 self-transfer

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk

**Context:** ERC20Rebasing.sol#L241-L

**Description:** Thefromandtobalances are fetched and cached, then updated via_setBalance(). Should a user
do an asset self-transfer such thatfrom == towith a specifiedamount, there would be fund duplication where his
balance would increase byamount.

**Recommendation:** Either shift the balance retrieval oftoto after the update offrom:

- uint256 toBalance = balanceOf(to);
    _setBalance(from, fromBalance - amount, currentSharePrice, false);
+ uint256 toBalance = balanceOf(to);
    _setBalance(to, toBalance + amount, currentSharePrice, false);

or use the_withdraw()and_deposit()methods:

```
function _transfer(
address from,
address to,
uint256 amount
) internal virtual {
if (from == address(0)) revert TransferFromZeroAddress();
if (to == address(0)) revert TransferToZeroAddress();
```
```
_withdraw(from, amount);
_deposit(to, amount);
```
```
emit Transfer(from, to, amount);
}
```
