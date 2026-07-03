### Title
Unconditional Zero-Value Fee Transfer in `MerkleDistributor.claim()` Permanently Freezes All User Claims - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

---

### Summary

`MerkleDistributor.claim()` unconditionally transfers the protocol fee to `protocolTreasury` even when `fee == 0`. When `feeInBPS` is set to zero (a valid configuration) and the distributed token does not allow zero-value transfers, every call to `claim()` reverts, permanently freezing all unclaimed tokens for all users.

---

### Finding Description

In `contracts/utils/MerkleDistributor/MerkleDistributor.sol`, the `claim()` function computes a fee and then unconditionally executes two `safeTransfer` calls:

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

// Send the fee to the protocol treasury
IERC20(token).safeTransfer(protocolTreasury, fee);  // ← always called, even when fee == 0
``` [1](#0-0) 

When `feeInBPS == 0`, `fee` evaluates to `0`, and `safeTransfer(protocolTreasury, 0)` is called unconditionally. Certain ERC-20 tokens revert on zero-value transfers. If the `token` configured in this distributor is such a token, every invocation of `claim()` will revert.

`feeInBPS` can legitimately be zero in two ways:

1. During initialization — `initialize()` only rejects values `> MAX_FEE_IN_BPS` (1000), so `_feeInBPS = 0` is accepted.
2. Post-deployment — `setFeeInBPS(0)` is valid for the same reason. [2](#0-1) [3](#0-2) 

---

### Impact Explanation

When triggered, **no user can claim any tokens** from the distributor. The tokens remain locked in the contract with no alternative withdrawal path for users. This constitutes a **permanent freezing of unclaimed yield** for all claimants.

Impact classification: **Medium — Permanent freezing of unclaimed yield.**

---

### Likelihood Explanation

Two conditions must hold simultaneously:

1. `feeInBPS` is set to `0` — this is a normal operational choice (zero-fee distribution), explicitly permitted by the contract's validation logic.
2. The configured `token` reverts on zero-value transfers — a known property of several deployed ERC-20 tokens (e.g., `LEND`, `cUSDCv3`, and others).

Neither condition requires any privileged compromise beyond normal admin configuration. The combination is realistic whenever the protocol deploys a zero-fee distributor for a token with this transfer restriction.

---

### Recommendation

Guard the fee transfer with a zero-check, mirroring the pattern already used in `KernelMerkleDistributor` and `KernelTop100MerkleDistributor`:

```solidity
// Before (vulnerable):
IERC20(token).safeTransfer(protocolTreasury, fee);

// After (fixed):
if (fee > 0) {
    IERC20(token).safeTransfer(protocolTreasury, fee);
}
``` [4](#0-3) 

---

### Proof of Concept

1. Deploy `MerkleDistributor` with `feeInBPS = 0` and a `token` that reverts on zero-value transfers (e.g., a token implementing `require(amount > 0)`).
2. Owner calls `setMerkleRoot(root)` with a valid distribution root.
3. Any user calls `claim(index, account, cumulativeAmount, merkleProof)` with a valid proof and non-zero `cumulativeAmount`.
4. Execution reaches line 138: `fee = (claimableAmount * 0) / 10_000 = 0`.
5. Line 141 succeeds: `safeTransfer(account, claimableAmount)`.
6. Line 144 reverts: `safeTransfer(protocolTreasury, 0)` — the token rejects the zero-value transfer.
7. The entire transaction reverts. The user's claim state was already updated at lines 134–135 before the revert, but since the whole transaction reverts, state is rolled back — however the user can never successfully claim because every attempt hits the same revert. [5](#0-4)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L71-87)
```text
    function initialize(address token_, address _protocolTreasury, uint256 _feeInBPS) external initializer {
        // token can be set later but not the protocol treasury
        if (_protocolTreasury == address(0)) {
            revert ZeroValueProvided();
        }

        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }

        __Ownable_init();
        __Pausable_init();

        token = token_;
        protocolTreasury = _protocolTreasury;
        feeInBPS = _feeInBPS;
    }
```

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
