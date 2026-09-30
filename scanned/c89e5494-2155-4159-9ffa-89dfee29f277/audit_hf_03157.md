# [H] Incorrect fees will be charged

## Summary
Severity: High
Contest weight: 0.7495
Dataset id: 17711
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If user has provided transferAmount which is greater than all lien.amount combined then initiatorPayment will be incorrect since it is charged on full amount when only partial was used as shown in poc 1. Observe the _handleIncomingPayment function 2. Lets say transferAmount was 1000 3. initiatorPayment is calculated on this full transferAmount
```solidity
uint256 initiatorPayment = transferAmount.mulDivDown(
    auction.initiatorFee,
);
```
4. Now all lien are iterated and lien.amount is kept on deducting from transferAmount until all lien are navigated
```solidity
if (transferAmount >= lien.amount) {
    payment = lien.amount;
    transferAmount -= payment;
} else {
    payment = transferAmount;
    transferAmount = 0;
}
if (payment > 0) {
    LIEN_TOKEN.makePayment(tokenId, payment, lien.position, payer);
}
```
5. Lets say after loop completes the transferAmount is still left as 100 6. This means only 400 transferAmount was used but fees was deducted on full amount 500 Excess initiator fees will be deducted which was not required

## Recommendation
Calculate the exact amount of transfer amount required for the transaction and calculate the initiator fee based on this amount
