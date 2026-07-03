### Title
Unconditional Zero-Value Fee Transfer in `claim()` Freezes User Claims for Revert-on-Zero ERC20 Tokens - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

### Summary
`MerkleDistributor.claim()` unconditionally calls `safeTransfer(protocolTreasury, fee)` even when `fee == 0`, which causes a revert for any ERC20 token that rejects zero-value transfers, permanently blocking all users from claiming their tokens.

### Finding Description
In `MerkleDistributor.sol`, the `claim()` function computes a fee and then unconditionally transfers it to `protocolTreasury`:

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

// Send the fee to the protocol treasury
IERC20(token).safeTransfer(protocolTreasury, fee);  // ← no zero-check
```

`fee` evaluates to `0` in two realistic scenarios:
1. `feeInBPS == 0` — the owner can set this via `setFeeInBPS(0)`, which passes the `_feeInBPS > MAX_FEE_IN_BPS` guard. When `feeInBPS == 0`, **every single claim** produces `fee == 0`.
2. `claimableAmount * feeInBPS < 10_000` — integer division truncates to zero for small claim amounts even with a non-zero `feeInBPS`.

The `token` address is a generic, owner-configurable ERC20 (set via `setToken`). The contract places no restriction on which token is used. Tokens that revert on zero-value transfers (e.g., LEND, BNB, and others documented in the [weird-erc20](https://github.com/d-xo/weird-erc20#revert-on-zero-value-transfers) list) will cause every `claim()` call to revert when `fee == 0`.

The sibling contracts `KernelMerkleDistributor` and `KernelTop100MerkleDistributor` correctly guard this transfer:
```solidity
if (fee > 0) {
    kernel.safeTransfer(protocolTreasury, fee);
}
```
`MerkleDistributor` is missing this guard.

### Impact Explanation
When the distributed token reverts on zero-value transfers and `fee` computes to `0`, the `claim()` function reverts for every user. All claimable token allocations are frozen inside the contract — users cannot receive their entitled tokens. If `feeInBPS` is set to `0`, this affects 100% of claims for the lifetime of that configuration, constituting a **permanent freeze of unclaimed yield** for all eligible recipients.

### Likelihood Explanation
- `feeInBPS` is explicitly allowed to be `0` by the `setFeeInBPS` validation logic.
- The token is generic and owner-configurable; deploying with a zero-revert token is a realistic operational scenario.
- No attacker action is required — the freeze is triggered by any ordinary user calling `claim()` under these conditions.
- The pattern is already fixed in two sibling contracts in the same repository, confirming the team is aware of the risk class.

### Recommendation
Add a zero-check before the fee transfer, consistent with the pattern used in `KernelMerkleDistributor` and `KernelTop100MerkleDistributor`:

```solidity
if (fee > 0) {
    IERC20(token).safeTransfer(protocolTreasury, fee);
}
```

### Proof of Concept
1. Deploy `MerkleDistributor` with a token that reverts on zero-value transfers (e.g., LEND).
2. Call `setFeeInBPS(0)` (valid — passes the `> MAX_FEE_IN_BPS` guard).
3. Set a valid merkle root and have a user call `claim()` with a valid proof.
4. The call computes `fee = (claimableAmount * 0) / 10_000 = 0`.
5. `IERC20(token).safeTransfer(protocolTreasury, 0)` reverts because the token rejects zero-value transfers.
6. The user's claim is permanently blocked; their tokens remain locked in the contract.

Alternatively, even with `feeInBPS > 0`, a user with a small `claimableAmount` such that `claimableAmount * feeInBPS < 10_000` will also trigger `fee == 0` and the same revert.

**Root cause line:** [1](#0-0) 

**Fee computation (no floor check):** [2](#0-1) 

**`feeInBPS` can be set to zero (no lower-bound guard):** [3](#0-2) 

**Correct pattern used in sibling contract `KernelMerkleDistributor`:** [4](#0-3) 

**Correct pattern used in sibling contract `KernelTop100MerkleDistributor`:** [5](#0-4)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L138-144)
```text
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;

        IERC20(token).safeTransfer(account, amountToSend);

        // Send the fee to the protocol treasury
        IERC20(token).safeTransfer(protocolTreasury, fee);
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L198-205)
```text
    function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }

        feeInBPS = _feeInBPS;

        emit FeeInBPSUpdated(_feeInBPS);
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L341-343)
```text
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L332-334)
```text
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
```
