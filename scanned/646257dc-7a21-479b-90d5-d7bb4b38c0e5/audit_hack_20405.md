# [M] 5.3.12 ThefromBlockvariable of a checkpoint is not initialized

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** VotingEscrow.sol#L1353, VotingEscrow.sol#L1256
**Description:** A checkpoint contains afromBlockvariable which stores the block number the checkpoint is created.
/// @notice A checkpoint for marking delegated tokenIds from a given block
struct Checkpoint {
uint256 fromBlock;
uint256[] tokenIds;
}

However, it was found that thefromBlock variable of a checkpoint was not initialized anywhere in the codebase.
Therefore, any function that relies on thefromBlockof a checkpoint will break.
TheVotingEscrow._findWhatCheckpointToWriteandVotingEscrow.getPastVotesIndexfunctions were found
to rely on thefromBlockvariable of a checkpoint for computation. The following is a list of functions that calls
these two affected functions.
_findWhatCheckpointToWrite -> _moveTokenDelegates -> _transferFrom
_findWhatCheckpointToWrite -> _moveTokenDelegates -> _mint
_findWhatCheckpointToWrite -> _moveTokenDelegates -> _burn
_findWhatCheckpointToWrite -> _moveAllDelegates -> _delegate -> delegate/delegateBySig
getPastVotesIndex -> getTokenIdsAt
getPastVotesIndex -> getPastVotes -> GovernorSimpleVotes._getVotes

**Instance 1 -** VotingEscrow._findWhatCheckpointToWrite **function**
TheVotingEscrow._findWhatCheckpointToWritefunction verifies if thefromBlockof the latest checkpoint of an
account is equal to the current block number. If true, the function will return the index number of the last checkpoint.
function _findWhatCheckpointToWrite(address account) internal view returns (uint32) {
uint256 _blockNumber = block.number;
uint32 _nCheckPoints = numCheckpoints[account];
if (_nCheckPoints > 0 && _checkpoints[account][_nCheckPoints - 1].fromBlock == _blockNumber) {
return _nCheckPoints - 1;
} else {
return _nCheckPoints;
}
}

As such, this function does not work as intended and will always return the index of a new checkpoint.
**Instance 2 -** VotingEscrow.getPastVotesIndex **function**
TheVotingEscrow.getPastVotesIndexfunction relies on thefromBlockof the latest checkpoint for optimization
purposes. If the request block number is the most recently updated checkpoint, it will return the latest index
immediately and skip the binary search. Since thefromBlockvariable is not populated, the optimization will not
work.


```
function getPastVotesIndex(address account, uint256 blockNumber) public view returns (uint32) {
uint32 nCheckpoints = numCheckpoints[account];
if (nCheckpoints == 0) {
return 0;
}
// First check most recent balance
if (_checkpoints[account][nCheckpoints - 1].fromBlock <= blockNumber) {
return (nCheckpoints - 1);
}
// Next check implicit zero balance
if (_checkpoints[account][0].fromBlock > blockNumber) {
return 0;
}
uint32 lower = 0;
uint32 upper = nCheckpoints - 1;
while (upper > lower) {
uint32 center = upper - (upper - lower) / 2;// ceil, avoiding overflow
Checkpoint storage cp = _checkpoints[account][center];
if (cp.fromBlock == blockNumber) {
return center;
} else if (cp.fromBlock < blockNumber) {
lower = center;
} else {
upper = center - 1;
}
}
return lower;
}
```
**Recommendation:** Initialize thefromBlockvariable of the checkpoint in the codebase.
**Velodrome:** Fixed in commit a670bf.
**Spearbit:** Verified.
