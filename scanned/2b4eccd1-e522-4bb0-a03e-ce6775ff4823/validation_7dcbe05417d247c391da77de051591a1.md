### Title
Fee Can Be Updated During Active Vesting Period, Reducing Claimant Yield - (File: contracts/KERNEL/KernelTop100MerkleDistributor.sol)

### Summary
`KernelTop100MerkleDistributor` applies `feeInBPS` at the moment of each `claim()` / `claimAndStake()` call rather than locking it when the merkle root is established. Because the owner can call `setFeeInBPS()` at any time, users who have already verified their total entitlement from the merkle root and begun vesting will receive less KERNEL than the root guarantees if the fee is raised mid-vesting. The same structural flaw exists in `KernelMerkleDistributor`.

### Finding Description
`KernelTop100MerkleDistributor` distributes KERNEL tokens over a fixed 30-day vesting window. The merkle root encodes each user's **total** claimable amount; users call `claim()` repeatedly as time passes to collect their pro-rata share.

At every claim the live `feeInBPS` is read and deducted:

```solidity
// KernelTop100MerkleDistributor.sol L328-329
uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
uint256 amountToSend = claimableAmount - fee;
``` [1](#0-0) 

The owner can raise this value at any time with no delay or cap beyond 10 %:

```solidity
// KernelTop100MerkleDistributor.sol L426-431
function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
    if (_feeInBPS > MAX_FEE_IN_BPS) revert InvalidFeeInBPS();
    feeInBPS = _feeInBPS;
    emit FeeInBPSUpdated(feeInBPS);
}
``` [2](#0-1) 

The `WithdrawalRequest` struct stores no fee snapshot; neither does the `UserClaim` struct:

```solidity
struct UserClaim {
    uint256 lastClaimTimestamp;
    uint256 amountClaimed;
}
``` [3](#0-2) 

The identical pattern exists in `KernelMerkleDistributor._processClaim()`: [4](#0-3) 
with the same unconstrained `setFeeInBPS()`: [5](#0-4) 

### Impact Explanation
Any KERNEL tokens that have vested but not yet been claimed are subject to whatever fee is in effect at the moment of the next `claim()` call. A fee increase from 0 % to the maximum 10 % applied to all remaining unclaimed vested tokens constitutes direct theft of unclaimed yield from every active claimant. Impact: **High — theft of unclaimed yield**.

### Likelihood Explanation
The 30-day vesting window in `KernelTop100MerkleDistributor` guarantees a multi-week gap between the merkle root being set and all tokens being claimed. During that window a routine fee-parameter update — a normal, permissioned protocol operation — silently changes the economics of every in-flight claim. No exploit transaction is required beyond the ordinary admin call; the loss materialises automatically on the user's next `claim()`. Likelihood: **Medium**.

### Recommendation
Snapshot `feeInBPS` at the time the merkle root (or vesting schedule) is established and store it immutably alongside the root. Apply only the snapshotted fee when processing claims, so that a fee update affects only future distribution rounds, not claims already in progress. This mirrors the fix applied to the Batched Bancor Market Maker: store the fee in the batch/order at creation time.

### Proof of Concept
1. Owner deploys `KernelTop100MerkleDistributor` with `feeInBPS = 0` and a merkle root granting Alice 1 000 KERNEL over 30 days.
2. After 15 days Alice calls `claim()` and correctly receives 500 KERNEL (0 % fee).
3. Owner calls `setFeeInBPS(1000)` (10 %) — a routine protocol revenue adjustment.
4. After the remaining 15 days Alice calls `claim()` for her remaining 500 KERNEL.
5. Line 328 computes `fee = 500 * 1000 / 10_000 = 50`; Alice receives only 450 KERNEL.
6. Alice's total receipt is 950 KERNEL instead of the 1 000 KERNEL guaranteed by the merkle root — 50 KERNEL silently redirected to `protocolTreasury` without Alice's knowledge or consent. [6](#0-5)

### Citations

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L152-155)
```text
    struct UserClaim {
        uint256 lastClaimTimestamp;
        uint256 amountClaimed;
    }
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L327-335)
```text
        // Calculate fee
        uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
        uint256 amountToSend = claimableAmount - fee;

        // Transfer tokens
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
        kernel.safeTransfer(user, amountToSend);
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L426-431)
```text
    function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }
        feeInBPS = _feeInBPS;
        emit FeeInBPSUpdated(feeInBPS);
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L337-343)
```text
        // Calculate the fee and the amount to send
        uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
        uint256 amountToSend = claimableAmount - fee;

        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
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
