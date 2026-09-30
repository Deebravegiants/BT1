# [M] CollectionShutdown::execute(

## Summary
Severity: Medium
Contest weight: 0.1598
Dataset id: 23246
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
CollectionShutdown::execute() doesn't ensure that all tokens of the collection being shutdown are added to the sudoswap pool in order to be sold. This function takes as input an array of the token IDs to be sold via sudoswap pool. In case an NFT ID that's locked in the protocol is not in this array the NFT will stay locked and not sold. Even if the function is only callable by admins the admins have no control on the order and the moment transactions are executed and such scenarios should be handled at the moment of execution. Internal pre-conditions External pre-conditions Attack Path 1. The protocol currently holds NFTs 55 and 56, admin calls CollectionShutdown::execute() by passing as a parameter [55,56]. 2. While the CollectionShutdown::execute() transaction is in the mempool a deposit of NFT 60 is done via Locker::deposit(). 3. The CollectionShutdown::execute() transaction goes through and a sudoswap pool selling 55 and 56 is created 4. NFT 60 is locked in the protocol NFTs that should be sold are locked in the procotol, which leads to an indirect loss of funds to collection tokens holders.

## Recommendation
In CollectionShutdown::execute() make sure all tokens currently locked in the protocol are added to the sudoswap pool.
