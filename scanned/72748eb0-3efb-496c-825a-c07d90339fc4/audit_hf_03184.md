# [H] Canceling an auction will result in a loss of funds due to double initiator fee

## Summary
Severity: High
Contest weight: 0.2256
Dataset id: 17757
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The initiator fee on the current bid has already been accounted during that bid but is expected to be paid again on cancellation by the borrower. Consider an active auction with a reserve price of 10 ETH and a current bid of 9 ETH. If the auction gets canceled, the transferAmount will be 10 ETH. Once the cancellation logic adds repayment to current bidder (see other finding reported on this issue), the initiator fees for cancellation should only be calculated on the delta payment of 1 ETH because the fees for the earlier 9 ETH bid has already been paid to the initiator. However, this is not accounted and requires the borrower to pay the initiator fees on the entire reserve price leading to overpayment towards the initiator and loss of funds for the borrower. Canceling an auction will require paying (a lot) more initiator fees than needed resulting in a loss of funds for the borrower.

## Recommendation
The cancellation amount required should be the reserve price + liquidation fee, where the fee is calculated on (reserve price - current bid) and not the reserve price.
