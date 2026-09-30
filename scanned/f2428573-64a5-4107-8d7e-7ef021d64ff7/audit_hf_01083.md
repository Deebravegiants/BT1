# [H] joinRecurPool can incorrectly increment userPoolCounts

## Summary
Severity: High
Contest weight: 0.6355
Dataset id: 4140
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can call joinRecurPool to update their staked balance when their current stakeToken balance increases.
```solidity
function joinRecurPool(RecurPoolKey[] calldata keys) external nonReentrant {
    address msgSender = LibMulticaller.senderOrSigner();
    for (uint256 i; i < keys.length; i++) {
        RecurPoolKey calldata key = keys[i];
        // -----------------------------------------------------------------------
        /// Validation
        // -----------------------------------------------------------------------
        // key should be valid
        if (!isValidRecurPoolKey(key)) continue;
        // user should have non-zero balance
        uint256 balance = ERC20(address(key.stakeToken)).balanceOf(msgSender);
        if (balance == 0) {
            continue;
        }
        // user's balance should be locked with this contract as the unlocker
        if (!key.stakeToken.isLocked(msgSender) || key.stakeToken.unlockerOf(msgSender) != IERC20Unlocker(address(this))) {
            continue;
        }
        // -----------------------------------------------------------------------
        /// Storage loads
        // -----------------------------------------------------------------------
        RecurPoolId id = key.toId();
        RecurPoolState storage state = recurPoolStates[id];
        uint256 stakedBalance = state.balanceOf[msgSender];
        // can't stake in a pool twice
        if (balance <= stakedBalance) {
            continue;
        }
        // stake
        state.totalSupply = totalSupply - stakedBalance + balance;
        state.balanceOf[msgSender] = balance;
        // increment user pool count
        // @audit - this should check balance before is 0
        unchecked {
            ++userPoolCounts[msgSender][key.stakeToken];
        }
        // emit event
        emit JoinRecurPool(msgSender, keys[i]);
    }
}
```
However, it will also increment userPoolCounts even when the operation is only updating stakedBalance and not the first time joining the recur pool. Incorrectly incrementing userPoolCounts here will prevent users from unlocking their tokens.

## Recommendation
Increment userPoolCounts only if the previous stakedBalance is 0.
