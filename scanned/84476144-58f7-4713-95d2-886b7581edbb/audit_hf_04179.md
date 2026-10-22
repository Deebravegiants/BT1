# [H] H-01 | Blacklisted Lenders Force Defaults

## Summary
Severity: High
Contest weight: 0.1709
Dataset id: 20860
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the makeLoanPayment function, the lendingDesk.erc20 token is transferred directly to the lender address: IERC20(lendingDesk.erc20).safeTransferFrom(msg.sender, lender, _amount); Therefore any lender that is blacklisted for the payment token will prevent the user from making loan payments. The lender will then force the user to be liquidated as they cannot pay back their loan in time. Furthermore, in the case of tokens with hooks after transfers, like ERC777, the receiver can make the transfer revert, preventing the borrower to make any payments to the loan as well.

## Recommendation
Do not push the lendingDesk.erc20 tokens directly to the lender address, instead increment a uint256 value in a mapping for an individual erc20 token and allow lenders to claim this amount with a separate function (pull-over-push pattern).
