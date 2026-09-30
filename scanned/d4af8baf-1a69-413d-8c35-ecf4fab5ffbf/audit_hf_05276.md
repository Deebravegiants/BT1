# [H] RemoraToken Transfer Bricking

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23506
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
RemoraToken::adminTransferFrom, transfer and transferFrom always check if `from` is on the whitelist and if not, call `_unlockTokens`:

```solidity
bool fromWL = whitelist[from];
bool toWL = whitelist[to];
if (!fromWL) _unlockTokens(from, value, false);
if (!toWL) _lockTokens(to, value);
```

Scenarios that cause a bricked transfer:

1. `from` has nothing to unlock but has enough tokens to fulfill the transfer.  
   In this case the transfer reverts because `_unlockTokens` is called with an amount that cannot be unlocked.

2. `from` has 10 tokens, only 5 of those tokens are locked, and attempts to transfer 10 tokens.  
   The call to `_unlockTokens` uses the full transfer amount (10) instead of the required unlocked amount (5), leading to a revert.

Impact: RemoraToken transfers are bricked when `from` is not whitelisted, has sufficient tokens to transfer but no tokens locked since the call to `_unlockTokens` will revert.

## Proof of Concept
```solidity
function test_transferBricked_fromNotWhitelisted_ButHasTokensToTransfer() external {
    address from = users[0];
    address to = users[1];
    uint256 amountToTransfer = 1;
    // fund `from` with remora tokens
    remoraTokenProxy.mint(from, amountToTransfer);
    assertEq(remoraTokenProxy.balanceOf(from), amountToTransfer);
    // remove `from` from whitelist
    remoraTokenProxy.removeFromWhitelist(from);
    // set lock time
    remoraTokenProxy.setLockUpTime(3600);
    vm.expectRevert(); // reverts with InsufficientTokensUnlockable
    vm.prank(from);
    remoraTokenProxy.transfer(to, amountToTransfer);
}
```

```solidity
function test_transferBricked_whitelistedHolderIsRemovedFromWhitelist() external {
    address from = users[0];
    address to = users[1];
    uint256 amountToTransfer = 10;
    _whitelistAndMintTokensToUser(from, amountToTransfer);
    // set lock time
    remoraTokenProxy.setLockUpTime(3600);
    // remove `from` from whitelist
    remoraTokenProxy.removeFromWhitelist(from);
    // fund `from` with remora tokens once it is not whitelisted
    remoraTokenProxy.mint(from, amountToTransfer);
    // 10 when was whitelisted and 10 when from was not whitelisted
    assertEq(remoraTokenProxy.balanceOf(from), amountToTransfer * 2);
    // forward beyond the lockup time to demonstrate the removed whitelisted holder can't do transfers
    vm.warp(3600 + 1);
    // reverts because from has only 10 tokens locked
    vm.expectRevert(); // reverts with InsufficientTokensUnlockable
    vm.prank(from);
    remoraTokenProxy.transfer(to, 11);
    // verify from can only transfer the 10 tokens that he received after he was removed from whitelist
    vm.prank(from);
    remoraTokenProxy.transfer(to, 10);
}
```

## Recommendation
Recommended Mitigation: A simple and elegant solution may be:

1) check `from` balance; if smaller than amount required for transfer revert  
2) in transfer functions if the user is not whitelisted, calculate their `uint256 unlockedBalanceToSend = balance - getTokensLocked(sender);` then if `unlockedBalanceToSend < amount` call `_unlockTokens(sender, value - unlockedBalanceToSend..);`

This solution only attempts to unlock the exact amount needed to fulfill a transfer, and doesn't attempt unlock if nothing to unlock or not required as the user has enough unlocked tokens to fulfill the transfer.
