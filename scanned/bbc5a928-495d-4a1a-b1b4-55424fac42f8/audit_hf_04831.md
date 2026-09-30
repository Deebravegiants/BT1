# [H] If repayLoanCallback address doesn't imple-

## Summary
Severity: High
Contest weight: 0.5794
Dataset id: 22719
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If repayLoanCallback address doesn't implement repayLoanCallback try/catch won't go into the catch and will revert the tx
If a contract, which is set as loanRepaymentListener from a lender doesn't implement repayLoanCallback transaction will revert and catch block won't help.
This is serious and even crucial problem, because a malicous lender could prevent borrowers from repaying their loans, as repayLoanCallback is called inside the only function used to repay loans. This way he guarantees himself their collateral tokens.
Conversation explaining why try/catch helps only if transaction is reverted in the target, contract, which is not the case here
```solidity
if (loanRepaymentListener != address(0)) {
try
ILoanRepaymentListener(loanRepaymentListener).repayLoanCallback{
gas: 80000
}( //limit gas costs to prevent lender griefing repayments
_bidId,
_msgSenderForMarket(bid.marketplaceId),
_payment.principal,
_payment.interest
)
{} catch {}
}
```
Lenders can stop borrowers from repaying their loans, forcing their loans to default.

## Recommendation
Maybe use a wrapper contract, which is trusted to you and is internally calling the repayLoanCallback on the untrusted target.
