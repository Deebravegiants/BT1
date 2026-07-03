### Title
Mutable `feeInBPS` Retroactively Applied to Already-Accrued Unclaimed Rewards - (`contracts/utils/MerkleDistributor/MerkleDistributor.sol`, `contracts/KERNEL/KernelMerkleDistributor.sol`, `contracts/KERNEL/KernelTop100MerkleDistributor.sol`)

---

### Summary

Three Merkle distributor contracts allow the owner to change `feeInBPS` at any time with no timelock. Because the fee is computed at the moment of `claim()` using the current global `feeInBPS`, any increase immediately and retroactively reduces the net yield received by users for rewards that were already accrued under a lower (or zero) fee rate.

---

### Finding Description

Each distributor tracks cumulative rewards off-chain and publishes them via a Merkle root. When a user calls `claim()`, the contract computes the incremental claimable amount and deducts a fee using the **current** `feeInBPS`:

**`MerkleDistributor.sol`:**
```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;
``` [1](#0-0) 

**`KernelMerkleDistributor.sol`:**
```solidity
uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
uint256 amountToSend = claimableAmount - fee;
``` [2](#0-1) 

**`KernelTop100MerkleDistributor.sol`:**
```solidity
uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
uint256 amountToStake = claimableAmount - fee;
``` [3](#0-2) 

The owner can update `feeInBPS` at any time with no delay:

```solidity
function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
    if (_feeInBPS > MAX_FEE_IN_BPS) {
        revert InvalidFeeInBPS();
    }
    feeInBPS = _feeInBPS;
    emit FeeInBPSUpdated(feeInBPS);
}
``` [4](#0-3) [5](#0-4) [6](#0-5) 

`MAX_FEE_IN_BPS = 1000` (10%) in all three contracts. [7](#0-6) [8](#0-7) 

There is no snapshot of the fee rate at the time rewards were earned, no per-user fee record, and no timelock on `setFeeInBPS()`. The new rate applies immediately to all pending unclaimed balances.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

A user who accrued 1,000 KERNEL tokens when `feeInBPS = 0` expects to receive 1,000 KERNEL on claim. If the owner raises `feeInBPS` to `MAX_FEE_IN_BPS = 1000` before the user claims, the user receives only 900 KERNEL — 100 KERNEL (10%) is silently redirected to the protocol treasury. This is a direct, quantifiable reduction of yield that was already earned and is owed to the user.

---

### Likelihood Explanation

**Medium.**

- No timelock or delay protects `setFeeInBPS()` in any of the three contracts.
- The owner can call it in a single transaction, instantly affecting all pending claims.
- A fee increase from 0% to 10% is within the allowed range and requires no extraordinary action.
- Users have no on-chain mechanism to detect or react to the change before their claim is processed (unless they monitor the mempool and front-run, which is not a reliable protection).

---

### Recommendation

1. **Snapshot the fee at reward-accrual time** — embed the applicable `feeInBPS` in the Merkle leaf or store it per-epoch so that each batch of rewards is always claimed at the rate that was in effect when it was published.
2. **Add a timelock** — require a mandatory delay (e.g., 48–72 hours) between calling `setFeeInBPS()` and the new rate taking effect, giving users time to claim under the old rate.
3. **Apply fee changes only to future Merkle roots** — track a `feeInBPS` per `currentMerkleRootIndex` and use the stored rate for each index rather than the live global value.

---

### Proof of Concept

1. Alice has 1,000 KERNEL accrued in the Merkle tree. `feeInBPS = 0`. She has not yet claimed.
2. The owner calls `setFeeInBPS(1000)` (10%), which takes effect immediately.
3. Alice calls `claim()`. The contract computes:
   - `claimableAmount = 1000`
   - `fee = (1000 * 1000) / 10_000 = 100`
   - `amountToSend = 900`
4. Alice receives 900 KERNEL instead of the 1,000 she earned. 100 KERNEL is sent to `protocolTreasury`.
5. Alice had no way to prevent this without monitoring the mempool and front-running the owner's transaction.

The same scenario applies identically in `KernelMerkleDistributor` (`claim()` / `claimAndStake()`) and `KernelTop100MerkleDistributor` (`claim()` / `claimAndStake()`), where vested KERNEL rewards are subject to the same retroactive fee deduction. [9](#0-8) [10](#0-9)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L47-47)
```text
    uint256 public constant MAX_FEE_IN_BPS = 1000;
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L138-139)
```text
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;
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

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L146-146)
```text
    uint256 public constant MAX_FEE_IN_BPS = 1000;
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L250-265)
```text
    function claim(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        external
        override
        nonReentrant
        whenNotPaused
    {
        uint256 amountToSend = _processClaim(index, account, cumulativeAmount, merkleProof);

        kernel.safeTransfer(account, amountToSend);

        emit Claimed(index, account, amountToSend);
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L338-339)
```text
        uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
        uint256 amountToSend = claimableAmount - fee;
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L388-396)
```text
    function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }

        feeInBPS = _feeInBPS;

        emit FeeInBPSUpdated(feeInBPS);
    }
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L310-338)
```text
    function claim(uint256 amount, bytes32[] calldata merkleProof) external nonReentrant whenNotPaused {
        address user = msg.sender;

        // Verify merkle proof and update user claim data
        _verifyClaimProof(user, amount, merkleProof);

        // Get claimable amount
        uint256 claimableAmount = _getUnclaimedVestedAmount(user, amount);

        if (claimableAmount == 0) {
            revert NoTokensToClaim();
        }

        // Update user claim data
        userClaims[user].lastClaimTimestamp = block.timestamp;
        userClaims[user].amountClaimed += claimableAmount;

        // Calculate fee
        uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
        uint256 amountToSend = claimableAmount - fee;

        // Transfer tokens
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
        kernel.safeTransfer(user, amountToSend);

        emit Claimed(user, amountToSend);
    }
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L363-364)
```text
        uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
        uint256 amountToStake = claimableAmount - fee;
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L426-432)
```text
    function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }
        feeInBPS = _feeInBPS;
        emit FeeInBPSUpdated(feeInBPS);
    }
```
