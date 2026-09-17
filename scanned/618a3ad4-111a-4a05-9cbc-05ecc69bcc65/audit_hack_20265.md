# [M] **3.3.1 Missing check in the number of Received Tokens when tokens are

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
transferred directly**

**Severity:** Medium Risk

**Context:** LSSVM\contracts,LSSVMPairERC20.sol#L41-

**Description:** Within the function_validateTokenInput()ofLSSVMPairERC20,
two methods exist to transfer tokens. In the first method viarouter.pairTrans
ferERC20From()a check is performed on the number of received tokens. In the
second method no checks are done.

Recent hacks (e.g. Qubit finance) have successfully exploitedsafeTransfer-
From()functions which did not revert nor transfer tokens. Additionally, with
malicious or re-balancing tokens the number of transferred tokens might be dif-
ferent from the amount requested to be transferred.


```
function _validateTokenInput(...) ... {
...
if (isRouter) {
...
// Call router to transfer tokens from user
uint256 beforeBalance = _token.balanceOf(_assetRecipient);
router.pairTransferERC20From(...)
// Verify token transfer (protect pair against malicious router)
require( _token.balanceOf(_assetRecipient) - beforeBalance ==
,! inputAmount, "ERC20 not transferred in");
} else {
// Transfer tokens directly
_token.safeTransferFrom(msg.sender, _assetRecipient, inputAmount);
}
}
```
**Recommendation:** Spearbit recommends Sudoswap to verify the number of
tokens received when these are transferred directly.

**Sudoswap:** Risks acknowledged but no changes at this time. Paircreators
would have to willingly create deploy anNFT/Tokenpair for a Token using non-
standardERC20token behavior to be at risk.

**Spearbit:** Acknowledged.
