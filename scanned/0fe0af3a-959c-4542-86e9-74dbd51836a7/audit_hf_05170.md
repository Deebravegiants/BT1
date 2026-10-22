# [M] If a collection has been shut-

## Summary
Severity: Medium
Contest weight: 0.5846
Dataset id: 23238
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a collection has been shutdown, it can later be re-initialized for use in the protocol again. But any attempts to shut it down again will fail due to a variable not being reset when the first shutdown is made.
When a collection's shutdown has collected >=quorum votes, the admin can initiate the execution of shutdown which essentially sunsets the collection from the locker and lists all the NFTs in a sudoswap pool so owners of the collection token can later claim their share of the sale proceeds.
When the call to in Locker.sol is made, it deletes both the _collectionToken and collectionInitialized mappings' entries so that the collection can later be re-registered and initialized if there is interest:
```solidity
// Delete our underlying token, then no deposits or actions can be made
delete _collectionToken[_collection];
// Remove our `collectionInitialized` flag
delete collectionInitialized[_collection];
```
The issue is that nowhere during the shutdown process is the params.shutdownVotes variable reset back to 0. The only way for it to decrease is if a user reclaims their vote, but then the shutdown won't finalize at all. In normal circumstances, the variable is checked against to ensure it is 0 before starting a collection shutdown, in order to prevent starting 2 simultaneous shutdowns of the same collection.
```solidity
if (params.shutdownVotes != 0) revert ShutdownProcessAlreadyStarted();
```
Thus, since it is never reset back to 0 when the shutdown is executed, if the collection is later re-initialized into the protocol and an attempt to shutdown again is made, the call to start() will revert on this line.
A collection that has been shutdown and later re-initialized can never be shutdown again.

## Recommendation
Reset variable back to 0 when all users have claimed their tokens and the process of shutting down a collection is completely finished.
