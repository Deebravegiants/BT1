### Title
`batchStakeFor` Reverts Entirely on Single-Entry Failure, Temporarily Freezing All Batched Users' KERNEL Tokens — (File: `contracts/KERNEL/KernelReceiver.sol`)

---

### Summary

`KernelReceiver.batchStakeFor` iterates over an array of users and amounts, calling the internal `_stakeFor` for each entry. Because `_stakeFor` contains hard `revert` paths and there is no per-entry error isolation, a failure on any single entry causes the entire batch transaction to revert. All users in the batch lose their stake attempt, and their KERNEL tokens remain stranded in the `KernelReceiver` contract until the operator manually retries with a corrected batch.

---

### Finding Description

`batchStakeFor` loops over `users` and `amounts` and delegates to `_stakeFor`: [1](#0-0) 

`_stakeFor` contains two hard-revert guards before the external stake call: [2](#0-1) 

The `InsufficientKernelBalance` guard is particularly dangerous in a batch context. After each successful `stakerGateway.stakeFor(...)` call, the contract's KERNEL balance decreases. If the cumulative amounts in the batch exceed the contract's balance at the time of the call, the check for a later entry will fail. Because there is no `try/catch` or per-entry error handling, the revert propagates upward and rolls back the entire transaction — including all previously successful stakes within the same batch.

This is the direct Solidity analog of the reported Rust bug: a `return` (here, a `revert`) inside a loop body terminates the entire processing task instead of skipping the failing entry and continuing.

---

### Impact Explanation

All users whose entries appeared in the failing batch have their KERNEL tokens frozen inside `KernelReceiver`. They are not staked in the Kernel Protocol, so they earn no staking rewards during the delay. The tokens are not permanently lost, but they are inaccessible to users until the operator identifies the offending entry, reconstructs a valid batch, and retries. This constitutes **temporary freezing of funds** for every user in the batch.

---

### Likelihood Explanation

KERNEL tokens are bridged from Ethereum mainnet to BSC via LayerZero and land in `KernelReceiver` asynchronously. An operator constructing a batch from observed bridge events may include entries whose tokens have not yet fully settled, or may include a dust entry with `amount == 0` from a malformed bridge message. Either condition causes the entire batch to revert. Because bridging latency is inherent to cross-chain operations, this scenario is realistic under normal operating conditions.

---

### Recommendation

Wrap each `_stakeFor` call inside `batchStakeFor` with a `try/catch` block. On failure, emit a dedicated event (e.g., `KernelStakeForFailed(user, amount, reason)`) and `continue` to the next entry. This mirrors the recommended fix in the external report: replace early-terminating `return` with `continue` so that a single failure does not abort the entire batch.

```solidity
for (uint256 i = 0; i < users.length; ++i) {
    try this.stakeForExternal(users[i], amounts[i]) {
        // success
    } catch (bytes memory reason) {
        emit KernelStakeForFailed(users[i], amounts[i], reason);
    }
}
```

---

### Proof of Concept

1. User A bridges 50 KERNEL; User B bridges 60 KERNEL. Only User A's tokens have arrived — `KernelReceiver` holds 50 KERNEL.
2. Operator calls `batchStakeFor([A, B], [50, 60])`.
3. `_stakeFor(A, 50)`: balance check passes (50 ≥ 50); `stakerGateway.stakeFor` transfers 50 KERNEL out; contract balance → 0.
4. `_stakeFor(B, 60)`: balance check `0 < 60` → `revert InsufficientKernelBalance()`.
5. The entire transaction reverts. User A's stake is rolled back. Both users' KERNEL tokens remain in `KernelReceiver`.
6. Users earn no staking rewards until the operator retries with a corrected batch. [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/KERNEL/KernelReceiver.sol (L140-160)
```text
    function batchStakeFor(
        address[] calldata users,
        uint256[] calldata amounts
    )
        external
        nonReentrant
        whenNotPaused
        onlyRole(OPERATOR_ROLE)
    {
        if (users.length == 0) {
            revert ZeroArrayLength();
        }

        if (users.length != amounts.length) {
            revert ArrayLengthMismatch();
        }

        for (uint256 i = 0; i < users.length; ++i) {
            _stakeFor(users[i], amounts[i]);
        }
    }
```

**File:** contracts/KERNEL/KernelReceiver.sol (L206-219)
```text
    function _stakeFor(address user, uint256 amount) internal {
        UtilLib.checkNonZeroAddress(user);

        if (amount == 0) {
            revert InvalidKernelAmount();
        }

        if (kernel.balanceOf(address(this)) < amount) {
            revert InsufficientKernelBalance();
        }

        ++lastStakedDepositId;
        stakerGateway.stakeFor(address(kernel), user, amount, "");

```
