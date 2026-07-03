### Title
Unconditional Zero-Amount Fee Transfer in `claim()` Blocks All Token Claims — (`contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

---

### Summary

`MerkleDistributor.claim()` unconditionally calls `IERC20(token).safeTransfer(protocolTreasury, fee)` even when `fee == 0`. When `feeInBPS` is set to zero (a valid configuration) and the distributed token reverts on zero-value transfers, every `claim()` invocation reverts, permanently freezing all unclaimed yield for every user of the distributor.

---

### Finding Description

In `MerkleDistributor.claim()`, after computing the fee:

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

// Send the fee to the protocol treasury
IERC20(token).safeTransfer(protocolTreasury, fee);   // ← no zero-check
``` [1](#0-0) 

When `feeInBPS == 0`, `fee` evaluates to `0`, and the unconditional `safeTransfer(protocolTreasury, 0)` is executed. The `token` address is owner-configurable via `setToken()` and can be any ERC20. [2](#0-1) 

`feeInBPS` is also owner-configurable and explicitly allows the value `0` — the only upper bound is `MAX_FEE_IN_BPS = 1000`: [3](#0-2) 

Tokens that revert on zero-value transfers (e.g., LEND, BNB, and others documented at [weird-erc20](https://github.com/d-xo/weird-erc20#revert-on-zero-value-transfers)) are a known class of ERC20 tokens. When such a token is configured as the distributed asset and `feeInBPS` is 0, the `safeTransfer(protocolTreasury, 0)` call reverts on every invocation of `claim()`.

---

### Impact Explanation

Every user's `claim()` call reverts. No user can retrieve their entitled tokens from the distributor. This constitutes **permanent freezing of unclaimed yield** — the tokens remain locked in the contract with no alternative claim path available to users.

Impact: **Medium — Permanent freezing of unclaimed yield.**

---

### Likelihood Explanation

Two independent, owner-controlled configuration choices must coincide:

1. `feeInBPS` is set to `0` — a natural "no-fee" configuration that is explicitly permitted by the contract.
2. The distributed `token` is one that reverts on zero-value transfers — a known ERC20 variant.

Neither condition requires an attacker. Both are reachable through normal, legitimate protocol administration. Once both are in effect, the freeze is immediate and affects all claimants simultaneously. There is no user-controlled escape path.

Likelihood: **Medium.**

---

### Recommendation

Guard the treasury fee transfer with a zero-amount check, mirroring the pattern already used elsewhere in the codebase (e.g., `KernelMerkleDistributor` and `KernelTop100MerkleDistributor`):

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

if (fee > 0) {
    IERC20(token).safeTransfer(protocolTreasury, fee);
}
``` [4](#0-3) 

---

### Proof of Concept

1. Owner deploys `MerkleDistributor` with a token that reverts on zero-value transfers (e.g., LEND) and `feeInBPS = 0`.
2. Owner sets a valid Merkle root; users accumulate claimable balances.
3. Any user calls `claim(index, account, cumulativeAmount, proof)`.
4. `fee = (claimableAmount * 0) / 10_000 = 0`.
5. `IERC20(token).safeTransfer(account, claimableAmount)` succeeds.
6. `IERC20(token).safeTransfer(protocolTreasury, 0)` reverts — the token rejects zero-value transfers.
7. The entire transaction reverts. The user's `userClaims` state was already updated at step 4 (lines 134–135), but because the revert unwinds all state changes, the user can retry — however, every retry will hit the same revert. All claims are permanently blocked until the owner changes either the token or the fee. [5](#0-4)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L133-146)
```text
        // Update user claim info, and send the token.
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeAmount = cumulativeAmount;

        // Send the claimable amount to the user - deducting the fee
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;

        IERC20(token).safeTransfer(account, amountToSend);

        // Send the fee to the protocol treasury
        IERC20(token).safeTransfer(protocolTreasury, fee);

        emit Claimed(index, account, claimableAmount);
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L185-193)
```text
    function setToken(address _token) external onlyOwner {
        if (_token == address(0)) {
            revert ZeroValueProvided();
        }

        token = _token;

        emit TokenUpdated(_token);
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L198-206)
```text
    function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }

        feeInBPS = _feeInBPS;

        emit FeeInBPSUpdated(_feeInBPS);
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L341-343)
```text
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
```
