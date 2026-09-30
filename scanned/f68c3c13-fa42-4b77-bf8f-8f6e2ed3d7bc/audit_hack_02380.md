# [M] \[M01\] Double counting rewards

## Summary
Severity: Medium
Source: https://github.com/pooltogether/pooltogether-contracts/tree/78ac6863f4616269f7d04a0ddd1d60bdfc454937/contracts/ERC777Pool.sol#L338
Type: audit-issue

## Details
After each draw with a winner, the [awardWinnings function](https://github.com/pooltogether/pooltogether-contracts/tree/78ac6863f4616269f7d04a0ddd1d60bdfc454937/contracts/ERC777Pool.sol#L338) is called. This updates the `balances` mapping, adds the reward to the current open draw on the winner’s behalf and emits the `Minted` and `Transfer` events. However, at this point in the process, the new Pool Tokens have not been created (since the deposit is in the open draw).

When the draw is subsequently committed, the balance of the draw becomes active and the [corresponding events are emitted](https://github.com/pooltogether/pooltogether-contracts/tree/78ac6863f4616269f7d04a0ddd1d60bdfc454937/contracts/ERC777Pool.sol#L331-L332). This means that the `Minted` and `Transfer` events associated with the reward are emitted twice: first sending the prize to the winner address and then implicitly when the open supply is sent to the contract. This will cause a mismatch between the total supply created and the `Minted` events.

Consider removing the [awardWinnings function in the ERC777Pool contract](https://github.com/pooltogether/pooltogether-contracts/tree/78ac6863f4616269f7d04a0ddd1d60bdfc454937/contracts/ERC777Pool.sol#L338-L341), and instead relying on the [overridden function in the BasePool contract](https://github.com/pooltogether/pooltogether-contracts/tree/78ac6863f4616269f7d04a0ddd1d60bdfc454937/contracts/BasePool.sol#L374-L380).

Note: this issue is related to [**“\[H02\] Winners can stall the system”**](#h02) and any mitigation should consider both simultaneously.

**Update**: _Fixed in [PR#3](https://github.com/pooltogether/pooltogether-contracts/pull/3/files/0255b953a964e41902198e428bd429ce48b117ac). The `awardWinnings` function has been removed. This pull request actually removes the `Minted` and `Transfer` events entirely as part of a broader code refactoring, but they are reintroduced in [PR#4](https://github.com/pooltogether/pooltogether-contracts/pull/4/commits/85fb9a8f05824b8aabde22795f2eb0408e8401da)_
