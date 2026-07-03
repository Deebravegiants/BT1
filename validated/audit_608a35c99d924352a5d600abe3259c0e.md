### Title
Unconditional Zero-Value Fee Transfer in `claim()` Permanently Freezes User Rewards When `feeInBPS == 0` - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

---

### Summary

`MerkleDistributor.claim()` unconditionally calls `IERC20(token).safeTransfer(protocolTreasury, fee)` even when `fee == 0`. When `feeInBPS` is set to zero (a valid configuration), any token that reverts on zero-value transfers will cause every single claim to revert permanently, freezing all user rewards in the contract.

---

### Finding Description

In `contracts/utils/MerkleDistributor/MerkleDistributor.sol`, the `claim` function computes a fee and then unconditionally transfers it to `protocolTreasury`:

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

// Send the fee to the protocol treasury
IERC20(token).safeTransfer(protocolTreasury, fee);  // <-- no zero-check
``` [1](#0-0) 

When `feeInBPS == 0`, `fee` evaluates to `0`, and `safeTransfer(protocolTreasury, 0)` is called. Certain ERC20 tokens (e.g., LEND, BNB, USDT on some deployments) revert on zero-value transfers. In that case, every call to `claim()` reverts, making all user allocations permanently unclaimable.

`feeInBPS` can legitimately be zero: the `initialize` function accepts `_feeInBPS == 0` without reverting, and `setFeeInBPS` only enforces an upper bound (`> MAX_FEE_IN_BPS`), not a lower bound: [2](#0-1) [3](#0-2) 

Contrast this with the sibling contracts `KernelMerkleDistributor` and `KernelTop100MerkleDistributor`, which both correctly guard the fee transfer:

```solidity
if (fee > 0) {
    kernel.safeTransfer(protocolTreasury, fee);
}
``` [4](#0-3) [5](#0-4) 

`MerkleDistributor` is the only distributor that omits this guard.

---

### Impact Explanation

When `feeInBPS == 0` and the distributed token reverts on zero-value transfers, `claim()` always reverts. The user's claim state is updated **before** the transfers (lines 134–135), but since the entire transaction reverts, the state is rolled back. However, the claim itself can never succeed — every attempt reverts at the zero-value fee transfer. All tokens held in the contract for distribution become permanently unclaimable.

**Impact: Medium — Permanent freezing of unclaimed yield.** [6](#0-5) 

---

### Likelihood Explanation

- `feeInBPS == 0` is a valid and expected configuration (no lower-bound check exists).
- The `MerkleDistributor` is a generic distributor; the token it distributes is set via `setToken()` and can be any ERC20, including tokens known to revert on zero-value transfers.
- Any user with a valid Merkle proof triggers the path — no special role or privilege required.
- The condition is deterministic: once `feeInBPS == 0` and the token is zero-transfer-reverting, **every** claim fails.

---

### Recommendation

Add a zero-value guard before the fee transfer, matching the pattern already used in `KernelMerkleDistributor` and `KernelTop100MerkleDistributor`:

```solidity
if (fee > 0) {
    IERC20(token).safeTransfer(protocolTreasury, fee);
}
``` [7](#0-6) 

---

### Proof of Concept

1. Deploy `MerkleDistributor` with a token that reverts on zero-value transfers (e.g., LEND) and `feeInBPS = 0`.
2. Owner calls `setMerkleRoot(root)` with a valid distribution root containing Alice's allocation.
3. Alice calls `claim(index, alice, cumulativeAmount, proof)` with a valid Merkle proof.
4. Inside `claim()`: `fee = (claimableAmount * 0) / 10_000 = 0`.
5. `IERC20(token).safeTransfer(alice, claimableAmount)` succeeds.
6. `IERC20(token).safeTransfer(protocolTreasury, 0)` reverts because the token disallows zero-value transfers.
7. The entire transaction reverts. Alice's tokens remain locked in the contract forever, as every subsequent attempt produces the same revert. [8](#0-7)

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

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L97-146)
```text
    function claim(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        external
        override
        whenNotPaused
    {
        if (currentMerkleRoot == bytes32(0)) {
            revert ZeroValueProvided();
        }

        if (index == 0 || index > currentIndex) {
            revert InvalidIndex();
        }

        if (isClaimed(index, account)) {
            revert AlreadyClaimed();
        }

        // Verify the merkle proof.
        bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
        if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
            revert InvalidMerkleProof();
        }

        // Calculate the claimable amount
        uint256 claimableAmount = cumulativeAmount - userClaims[account].cumulativeAmount;

        // Ensure there is something to claim
        if (claimableAmount == 0) {
            revert NoTokensToClaim();
        }

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

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L332-334)
```text
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
```
