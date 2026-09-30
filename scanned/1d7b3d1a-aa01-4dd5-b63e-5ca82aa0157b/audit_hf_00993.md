# [H] Refactor _paymentAH()

## Summary
Severity: High
Contest weight: 0.2439
Dataset id: 3189
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
_paymentAH() has several vulnerabilities:
• stack is a memory parameter. So all the updates made to stack are not applied back to the corresponding storage variable.
• No need to update stack[position] as it's deleted later.
• decreaseEpochLienCount() is always passed 0, as stack[position] is already deleted. Also decreaseEpochLienCount() expects epoch, but end is passed instead.
• This if/else block can be merged. updateAfterLiquidationPayment() expects msg.sender to be LIEN_TOKEN, so this should work.

## Recommendation
Apply this diff:
```diff
function _paymentAH(
    LienStorage storage s,
    uint256 collateralId,
-   AuctionStack[] memory stack,
+   AuctionStack[] storage stack,
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
-   if (owing > payment.safeCastTo88()) {
-       stack[position].amountOwed -= payment.safeCastTo88();
-   } else {
+   if (owing < payment.safeCastTo88()) {
        payment = owing;
    }
    s.TRANSFER_PROXY.tokenTransferFrom(s.WETH, payer, payee, payment);
    delete s.lienMeta[lienId]; //full delete
    delete stack[position];
    _burn(lienId);
    if (_isPublicVault(s, payee)) {
-       if (owner == payee) {
            IPublicVault(payee).updateAfterLiquidationPayment(
                IPublicVault.LiquidationPaymentParams({lienEnd: end})
            );
-       } else {
-           IPublicVault(payee).decreaseEpochLienCount(stack[position].end);
-       }
    }
    emit Payment(lienId, payment);
    return payment;
}
```
Also note other issues related to _paymentAH():
• Avoid shadowing variables
• Comment or remove unused function parameters
