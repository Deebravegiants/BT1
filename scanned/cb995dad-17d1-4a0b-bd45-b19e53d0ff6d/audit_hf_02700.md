# [C] Unlocking oﬀers does not return any funds

## Summary
Severity: Critical
Contest weight: 0.2072
Dataset id: 14645
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user unlocks (ie. cancels) an oﬀer, the oﬀer is deleted from the protocol, but the purchase tokens are not returned to the user.
On line [235] of TermAuctionOfferLocker.sol, a call to termRepoServicer.unlockOfferAmount() should return the purchase tokens for an oﬀer to the oﬀerer. However, it is called with the argument offerToUnlock.amount. offerToUnlock is declared on line [228] as a variable of type storage. Storage variables are simply pointers, or references to existing storage locations. Therefore, when the variable which offerToUnlock points to is deleted on line [230], the contents of offerToUnlock are deleted too. This means that offerToUnlock.amount will be zero, and so no tokens will be returned.

## Recommendation
Use a memory variable to copy values that are about to be deleted from storage. The variable type on line [228] could be changed to memory, but gas could be saved by instead copying only the information required:
uint256 amountToUnlock = offers[id].amount;
Note that uint256 variables inside functions are automatically of type memory.
