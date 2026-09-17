# [H] 5.2.10 Refactor_paymentAH()

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** LienToken.sol#L571
**Description:** _paymentAH()has several vulnerabilities:

- stackis a memory parameter. So all the updates made tostackare not applied back to the corresponding
    storage variable.
- No need to updatestack[position]as it's deleted later.
- decreaseEpochLienCount()is always passed 0 , asstack[position]is already deleted. AlsodecreaseEp-
    ochLienCount()expects epoch, butendis passed instead.
- This if/else block can be merged. updateAfterLiquidationPayment()expectsmsg.senderto beLIEN_-
    TOKEN, so this should work.
**Recommendation:** Apply this diff:
function _paymentAH(
LienStorage storage s,
uint256 collateralId,
- AuctionStack[] memory stack,
+ AuctionStack[] storage stack,
uint256 position,
uint256 payment,
address payer
) internal returns (uint256) {
uint256 lienId = stack[position].lienId;
uint256 end = stack[position].end;
uint256 owing = stack[position].amountOwed;
//checks the lien exists
address owner = ownerOf(lienId);
address payee = _getPayee(s, lienId);
- if (owing > payment.safeCastTo88()) {
- stack[position].amountOwed -= payment.safeCastTo88();
- } else {
+ if (owing < payment.safeCastTo88()) {
payment = owing;
}
s.TRANSFER_PROXY.tokenTransferFrom(s.WETH, payer, payee, payment);
delete s.lienMeta[lienId]; //full delete
delete stack[position];
_burn(lienId);
if (_isPublicVault(s, payee)) {
- if (owner == payee) {
IPublicVault(payee).updateAfterLiquidationPayment(
IPublicVault.LiquidationPaymentParams({lienEnd: end})
);
- } else {
- IPublicVault(payee).decreaseEpochLienCount(stack[position].end);
- }


```
}
emit Payment(lienId, payment);
return payment;
}
```
Also note other issues related to_paymentAH():

- Avoid shadowing variables
- Comment or remove unused function parameters
**Astaria:** Fixed in PR 201.
**Spearbit:** Verified.
