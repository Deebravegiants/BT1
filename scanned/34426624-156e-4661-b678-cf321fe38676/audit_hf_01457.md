# [H] All of the pairings' timestamps will be updated for epoch 0

## Summary
Severity: High
Contest weight: 0.7812
Dataset id: 7561
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An epoch is a pre-determined period of time which is used to decide when to reorganize tribes and redraw the clans. Therefore, it is used to store the values of any pairings for a given epoch in a mapping. The variable is initialized with default value 0 inside SupraSValueFeedVerifier :
```solidity
uint256 epochCount = 0;
```
Then it is used when the processCluster to getTimestamp and to update the timestamp by calling restrictedSetTimestamp :
```solidity
function processCluster(Smr.Vote memory vote, Smr.MinBatch memory smrBatch, Smr.MinTxn memory smrTxn, Smr.SignedCoherentCluster memory scc, uint batchIdx, uint txnIdx, uint clusterIdx, uint256[2] calldata sig) public {
    for (uint i = 0; i < cluster.pair.length; i++) {
        uint pair = cluster.pair[i];
        uint timestamp = cluster.timestamp[i];
        uint prevTimestamp = supraSValueFeedStorage.getTimestamp(pair, epochCount);
        if (prevTimestamp > timestamp) {
            continue;
        }
        supraSValueFeedStorage.restrictedSetTimestamp(pair, epochCount, timestamp);
    }
}
```
The problem arises from the fact that every time the calls to these functions are made, a value of 0 will be passed for the epoch parameter. The epochCount variable is not updated anywhere across the contracts.
If we take a look at how restrictedSetTimestamp is by performing checks that only the SupraSValueFeedVerifier can call it and then calls setTimestamp which looks like this:
```solidity
function setTimestamp(uint _tradingPair, uint256 _epoch, uint timestamp) internal {
    latestTimestamp[_tradingPair][_epoch] = timestamp;
}
```
This means that the timestamp will be always updated for epoch 0 for the specified _tradingPair.
Thus, the logic of using epochs is broken and they are completely unnecessary in the current implementation.

## Recommendation
Consider to implement a functionality which updates the epoch. This can be done by updating the epoch when a specific number of clusters are processed or when a given amount of time has passed (e.g. 2 days) as described in the documentation.
