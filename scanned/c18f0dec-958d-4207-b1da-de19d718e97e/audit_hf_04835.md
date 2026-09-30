# [H] _sendOrEscrowFundswill brick LCG funds caus-

## Summary
Severity: High
Contest weight: 0.2773
Dataset id: 22727
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LenderCommitmentGroup (LCG) will have its funds stuck if transferFrom inside _sendOrEscrowFunds reverts for some reason. This will increase the share price but not transfer any funds, causing insolvency.
_sendOrEscrowFunds has try and catch, where try attempts transferFrom, and if transferFrom reverts, ensuring the repay/liquidation call does not. If transferFrom reverts due to any reason, the tokens will be stored inside EscrowVault, allowing the lender to withdraw them at any time.
However, for LCG, if such a deposit happens, the tokens will be stuck inside EscrowVault since LCG lacks a withdraw implementation. The share price will still increase, as the next if will pass, but this will cause more damage to the pool. Not only did it lose capital, but it also became insolvent.
Not only did it lose capital, but it also became insolvent.
ILoanRepaymentListener(loanRepaymentListener).repayLoanCallback{gas: 80000}(
_bidId,
_msgSenderForMarket(bid.marketplaceId),
_payment.principal,
_payment.interest
)
The pool is insolvent because the share value has increased, but the assets in the pool have not, meaning the last few LPs won't be able to withdraw.
Fund loss for LCG and insolvency for the pool, as share price increases, but assets do not.

## Recommendation
Implement the withdraw function inside LCG, preferably callable by anyone.
