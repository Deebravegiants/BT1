# [M] Block other users from executing `QueueInternal._redeemMax`

## Summary
Severity: Medium
Reporter: 0xc0ffEE
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L140-L150
Type: audit-issue

## Details
# Block other users from executing `QueueInternal._redeemMax`

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L140-L150

This function logic is to redeem all claim tokens from previous epochs by looping through all token ids of `owner` and `redeem` each if `tokenId != currentTokenId`. This execution can exceed block gas limit when `owner` has many `tokenIds`, meaning that he has many claim tokens at many epochs

Imagine scenario that Alice wants to grief Bob
Alice uses many addresses to deposit to many epochs, each epoch uses a different address with a small deposit amount so that he could get claim tokens at many epochs. 
Alice then transfers all claim tokens he has to Bob's address
After that, the execution of  `_redeemMax` with `owner == <Bob's address>` would be blocked

The impact is that Bob could fail when `redeemMax` , `deposit` and even though when executing `Vault.withdraw`. At this time Bob has to transfer out the tokens he received from Alice if he wants the execution not to fail, this will cost Alice's gas
Recommendation: consider not allowing user to transfer tokens at previous epochs
