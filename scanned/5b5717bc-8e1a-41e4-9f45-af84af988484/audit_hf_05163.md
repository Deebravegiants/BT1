# [M] Malicious user can bypass execute shutdown prevention

## Summary
Severity: Medium
Contest weight: 0.6920
Dataset id: 23229
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Malicious user bypasses CollectionShutdown::preventShutdown by calling CollectionShutdown::start then CollectionShutdown::reclaimVote making the use of checks in preventShutdown useless. In preventShutdown function there a check to make sure there isn't currently a shutdown in progress.
```solidity
function preventShutdown(address _collection, bool _prevent) public {
    // Make sure our user is a locker manager
    if (!locker.lockerManager().isManager(msg.sender)) revert ILocker.CallerIsNotManager();

    // Make sure that there isn't currently a shutdown in progress
    if (_collectionParams[_collection].shutdownVotes != 0) revert ShutdownProcessAlreadyStarted();

    // Update the shutdown to be prevented
    shutdownPrevented[_collection] = _prevent;
    emit CollectionShutdownPrevention(_collection, _prevent);
}
```
This check doesn't confirm that the shutdown is in progress or not user can call CollectionShutdown::start to start a shutdown. Then CollectionShutdown::reclaimVote to set shutdownVotes back to 0. Calling start function indeed increases the votes by calling _vote.
```solidity
function start(address _collection) public whenNotPaused {
    //code
    // Cast our vote from the user
    _collectionParams[_collection] = _vote(_collection, params);
}
```
In _votes the count of shutdownVotes increase which is normal.
```solidity
function _vote(address _collection, CollectionShutdownParams memory params) internal returns (CollectionShutdownParams memory) {
    //code
    // Register the amount of votes sent as a whole, and store them against the user
    params.shutdownVotes += uint96(userVotes);
}
```
There is no prevention for the user initiated the shutdown from calling reclaimVote.
```solidity
function reclaimVote(address _collection) public whenNotPaused {
    //code
    // We delete the votes that the user has attributed to the collection
    params.shutdownVotes -= uint96(userVotes);
}
```
This line resets back the shutdownVotes to 0, making CollectionShutdown::preventShutdown checks useless.
Internal pre-conditions
• lockerManager calling CollectionShutdown::preventShutdown .
Attack Path 1
1. lockerManager calling CollectionShutdown::preventShutdown.
2. Malicious user front run the CollectionShutdown::preventShutdown by calling CollectionShutdown::start and CollectionShutdown::reclaimVote .
3. lockerManger believe this collection is prevented from shutdown but its not.
Attack Path 2
1. Malicious user calling CollectionShutdown::start and CollectionShutdown::reclaimVote .
2. lockerManager calling CollectionShutdown::preventShutdown.
3. lockerManger believe this collection is prevented from shutdown but its not.
Bypass preventShutdown function making it useless.

## Recommendation
• When doing a shutdown check for quorumVotes or check during vote() that the collection is prevented from shutdown. Change the check in preventShutdown.
```solidity
if (_collectionParams[_collection].quorumVotes != 0) revert ShutdownProcessAlreadyStarted();
```
