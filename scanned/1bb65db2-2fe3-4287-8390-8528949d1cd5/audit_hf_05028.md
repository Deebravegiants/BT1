# [M] Any user can DOS BorrowNFT.modifyof any other

## Summary
Severity: Medium
Contest weight: 0.2214
Dataset id: 23029
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ETH balance is required to be 0 at the end of modify:
require(address(this).balance == 0, "Aloe: antes sum");
This allows any user to front-run this transaction, deposit 1 wei of ETH (for example via calling payable multicall function with 1 wei and empty array), and the modify transaction will revert in the require referenced above.
This can be kept forever only at the gas cost, DOS'ing the modification of position, making it impossible for the other user(s) to do anything with their accounts, especially withdrawing/borrowing, which can be a lost opportunity or loss of funds for the user (for example, user wanted to withdraw collateral to fund another position to avoid liquidation, but due to DOS he can't withdraw + deposit and is liquidated).
BorrowNFT.modify sends out ETH to all user borrower accounts for ante, requiring remaining balance in the BorrowNFT contract to be exactly 0:
y/src/borrower-nft/BorrowerNFT.sol#L111
Since user doesn't control amount of ETH in the contract (and it's easy to send ETH to the contract via payable multicall or mint functions), it's easy to DOS the modify non-zero and revert.
Internal pre-conditions
Any user call BorrowNFT.modify
External pre-conditions
None
Attack Path
Front-running BorrowNFT.modify with depositing 1 wei of ETH to BorrowNFT via multicall payable function with empty array.
DOS the NFT borrow position modification of any user. This makes it impossible for the user(s) to do any actions with their accounts, such as withdrawals, borrows etc.
This can be a lost opportunity or loss of funds for the user (for example, user wanted to withdraw collateral to fund another position to avoid liquidation, but due to DOS he can't withdraw + deposit and is liquidated).

## Recommendation
Consider sending remainder of ETH back to user instead of requiring it to be 0.
