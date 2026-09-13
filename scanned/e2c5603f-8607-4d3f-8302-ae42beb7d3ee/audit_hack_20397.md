# [H] 5.2.2 Inflated voting balance due to duplicatedveNFTswithin a checkpoint

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** VotingEscrow.sol#L1309, VotingEscrow.sol#L
**Description:**
Note: This issue affectsVotingEscrow._moveTokenDelegates andVotingEscrow._moveAllDele-
gatesfunctions
A checkpoint can contain duplicated veNFTs (tokenIDs) under certain circumstances leading to double counting
of voting balance. Malicious users could exploit this vulnerability to inflate the voting balance of their accounts and
participate in governance and gauge weight voting, potentially causing loss of assets or rewards for other users if
the inflated voting balance is used in a malicious manner (e.g. redirect rewards to gauges where attackers have a
vested interest).
Following is the high-level pseudo-code of the existing_moveTokenDelegatesfunction, which is crucial for under-
standing the issue.

1. Assuming moving tokenID=888 from Alice to Bob.
2. Source Code Logic (Moving tokenID=888 out of Alice)
    - Fetch the existing Alice's token IDs and assign them tosrcRepOld
    - Create a new empty array =srcRepNew
    - Copy all the token IDs insrcRepOldtosrcRepNewexcept for tokenID=
3. Destination Code Logic (Moving tokenID=888 into Bob)
    - Fetch the existing Bobs' token IDs and assign them todstRepOld
    - Create a new empty array =dstRepNew
    - Copy all the token IDs indstRepOldtodstRepNew
    - Copy tokenID=888 todstRepNew
The existing logic works fine as long as a new empty array (srcRepNew OR dstRepNew) is created every single
time. The code relies on the_findWhatCheckpointToWritefunction to return the index of a new checkpoint.
function _moveTokenDelegates(
..SNIP..
uint32 nextSrcRepNum = _findWhatCheckpointToWrite(srcRep);
uint256[] storage srcRepNew = _checkpoints[srcRep][nextSrcRepNum].tokenIds;

However, the problem is that the_findWhatCheckpointToWritefunction does not always return the index of a new
checkpoint (Refer to Line 1357 below). It will return the last checkpoint if it has already been written once within
the same block.
function _findWhatCheckpointToWrite(address account) internal view returns (uint32) {
uint256 _blockNumber = block.number;
uint32 _nCheckPoints = numCheckpoints[account];
if (_nCheckPoints > 0 && _checkpoints[account][_nCheckPoints - 1].fromBlock == _blockNumber) {
return _nCheckPoints - 1;
} else {
return _nCheckPoints;
}
}

If someone triggers the_moveTokenDelegatesmore than once within the same block (e.g. perform NFT transfer
twice to the same person), the_findWhatCheckpointToWritefunction will return a new checkpoint in the first
transfer but will return the last/previous checkpoint in the second transfer. This will cause the move token delegate
logic to be off during the second transfer.


**First Transfer at Block 1000**
Assume the following states:
numCheckpoints[Alice] = 1
_checkpoints[Alice][0].tokenIds = [n1, n2] <== Most recent checkpoint
numCheckpoints[Bob] = 1
_checkpoints[Bob][0].tokenIds = [n3] <== Most recent checkpoint

To move tokenID=2 from Alice to Bob, the_moveTokenDelegates(Alice, Bob, n2)function will be triggered.
The_findWhatCheckpointToWritewill return the index of 1 which points to a new array.
The end states of the first transfer will be as follows:
numCheckpoints[Alice] = 2
_checkpoints[Alice][0].tokenIds = [n1, n2]
_checkpoints[Alice][1].tokenIds = [n1] <== Most recent checkpoint
numCheckpoints[Bob] = 2
_checkpoints[Bob][0].tokenIds = [n3]
_checkpoints[Bob][1].tokenIds = [n2, n3] <== Most recent checkpoint

Everything is working fine at this point in time.
**Second Transfer at Block 1000** (same block)
To move tokenID=1 from Alice to Bob, the_moveTokenDelegates(Alice, Bob, n1)function will be triggered.
This time round since the last checkpoint block is the same as the current block, the_findWhatCheckpointToWrite
function will return the last checkpoint instead of a new checkpoint.
ThesrcRepNewanddstRepNewwill end up referencing the old checkpoint instead of a new checkpoint. As such,
thesrcRepNewanddstRepNewarray will reference back to the old checkpoint_checkpoints[Alice][1].tokenIds
and_checkpoints[Bob][1].tokenIdsrespectively.
The end state of the second transfer will be as follows:
numCheckpoints[Alice] = 3
_checkpoints[Alice][0].tokenIds = [n1, n2]
_checkpoints[Alice][1].tokenIds = [n1] <== Most recent checkpoint
numCheckpoints[Bob] = 3
_checkpoints[Bob][0].tokenIds = [n3]
_checkpoints[Bob][1].tokenIds = [n2, n3, n2, n3, n1] <== Most recent checkpoint

Four (4) problems could be observed from the end state:

1. ThenumCheckpointsis incorrect. Should be two (2) instead to three (3)
2. TokenID=1 has been added to Bob's Checkpoint, but it has not been removed from Alice's Checkpoint
3. Bob's Checkpoint contains duplicated tokenIDs (e.g. there are two TokenID=2 and TokenID=3)
4. TokenID is not unique (e.g. TokenID appears more than once)
Since the token IDs within the checkpoint will be used to determine the voting power, the voting power will be
inflated in this case as there will be a double count of certain NFTs.
function _moveTokenDelegates(
..SNIP..
uint32 nextSrcRepNum = _findWhatCheckpointToWrite(srcRep);
uint256[] storage srcRepNew = _checkpoints[srcRep][nextSrcRepNum].tokenIds;


**Additional Comment about** nextSrcRepNum **variable and** _findWhatCheckpointToWrite **function**
In Line 1320 below, the code wrongly assumes that the_findWhatCheckpointToWritefunction will always return
the index of the next new checkpoint. The_findWhatCheckpointToWritefunction will return the index of the latest
checkpoint instead of a new one ifblock.number == checkpoint.fromBlock.

```
function _moveTokenDelegates(
address srcRep,
address dstRep,
uint256 _tokenId
) internal {
if (srcRep != dstRep && _tokenId > 0) {
if (srcRep != address(0)) {
uint32 srcRepNum = numCheckpoints[srcRep];
uint256[] storage srcRepOld = srcRepNum > 0
? _checkpoints[srcRep][srcRepNum - 1].tokenIds
: _checkpoints[srcRep][0].tokenIds;
uint32 nextSrcRepNum = _findWhatCheckpointToWrite(srcRep);
uint256[] storage srcRepNew = _checkpoints[srcRep][nextSrcRepNum].tokenIds;
```
**Additional Comment about** numCheckpoints
In Line 1330 below, the function computes the new number of checkpoints by incrementing thesrcRepNumby one.
However, this is incorrect because ifblock.number == checkpoint.fromBlock, then the number of checkpoints
remains the same and does not increment.
function _moveTokenDelegates(
address srcRep,
address dstRep,
uint256 _tokenId
) internal {
if (srcRep != dstRep && _tokenId > 0) {
if (srcRep != address(0)) {
uint32 srcRepNum = numCheckpoints[srcRep];
uint256[] storage srcRepOld = srcRepNum > 0
? _checkpoints[srcRep][srcRepNum - 1].tokenIds
: _checkpoints[srcRep][0].tokenIds;
uint32 nextSrcRepNum = _findWhatCheckpointToWrite(srcRep);
uint256[] storage srcRepNew = _checkpoints[srcRep][nextSrcRepNum].tokenIds;
// All the same except _tokenId
for (uint256 i = 0; i < srcRepOld.length; i++) {
uint256 tId = srcRepOld[i];
if (tId != _tokenId) {
srcRepNew.push(tId);
}
}
numCheckpoints[srcRep] = srcRepNum + 1;
}

**Recommendation:** Update the move token delegate logic within the affected functions (VotingEscrow._moveTok-
enDelegatesandVotingEscrow._moveAllDelegates) to ensure that the latest checkpoint is overwritten correctly
when the functions are triggered more than once within a single block.
Further, ensure that the following invariants hold in the new code:

- No duplicated veNFTs (tokenIDs) within a checkpoint
- When moving a tokenID, it must be deleted from the sourcetokenIdslist and added to the destination
    tokenIdslist
- No more than one checkpoint within the same block for an account. Otherwise, the binary search within the
    VotingEscrow.getPastVotesIndexwill return an incorrect number of votes


Sidenote: Another separate issue is that thefromBlockof a checkpoint is not set anywhere in the codebase.
Therefore, the_findWhatCheckpointToWritefunction will always create and return a new checkpoint, which is
not working as intended. This issue will be raised in another report"The fromBlock variable of a checkpoint is
not initialized". Since the remediation of this issue also depends on fixing thefromBlockproblem, this is being
highlighted here again for visibility.
**Velodrome:** Fixed in commit a670bf.
**Spearbit:** Verified.
