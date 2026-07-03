### Title
`setMerkleRoot()` Accepts Merkle Root Without Validating Contract Token Balance Can Cover All Encoded Claims - (File: contracts/KERNEL/KernelMerkleDistributor.sol)

---

### Summary

`KernelMerkleDistributor.setMerkleRoot()` and `MerkleDistributor.setMerkleRoot()` accept a new merkle root with no on-chain check that the contract's token balance is sufficient to cover the sum of all cumulative amounts encoded in the tree's leaves. If the off-chain system sets a root whose total claimable amounts exceed the contract's actual balance, later claimants will have their `claim()` or `claimAndStake()` calls revert, permanently freezing their unclaimed yield.

---

### Finding Description

Both `KernelMerkleDistributor` and `MerkleDistributor` use a cumulative-claim model: each leaf encodes a `cumulativeAmount` per user, and the claimable delta is `cumulativeAmount - userClaims[account].cumulativeAmount`. The owner sets a new distribution by calling `setMerkleRoot()`, which only validates that the root is non-zero:

```solidity
// KernelMerkleDistributor.sol:402-413
function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
    if (_merkleRootToSet == bytes32(0)) {
        revert ZeroValueProvided();
    }
    currentMerkleRoot = _merkleRootToSet;
    currentMerkleRootIndex++;
    currentIndex++;
    emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
}
```

There is no check that `kernel.balanceOf(address(this)) >= sum_of_all_leaf_claimable_amounts`. [1](#0-0) 

When a user calls `claim()`, `_processClaim()` computes the claimable delta, deducts a fee (sent to `protocolTreasury`), and returns `amountToSend`. The caller then executes `kernel.safeTransfer(account, amountToSend)`:

```solidity
// KernelMerkleDistributor.sol:261-265
function claim(...) external override nonReentrant whenNotPaused {
    uint256 amountToSend = _processClaim(index, account, cumulativeAmount, merkleProof);
    kernel.safeTransfer(account, amountToSend);
    emit Claimed(index, account, amountToSend);
}
``` [2](#0-1) 

The fee transfer inside `_processClaim()` also consumes contract balance before `amountToSend` is returned:

```solidity
// KernelMerkleDistributor.sol:338-342
uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
uint256 amountToSend = claimableAmount - fee;
if (fee > 0) {
    kernel.safeTransfer(protocolTreasury, fee);
}
``` [3](#0-2) 

The identical pattern exists in `MerkleDistributor.setMerkleRoot()` and `MerkleDistributor.claim()`: [4](#0-3) [5](#0-4) 

Because the contract relies entirely on off-chain correctness with no on-chain balance guard at root-setting time, any discrepancy between the merkle tree's total encoded amounts and the contract's actual token balance will cause the last claimants' transactions to revert.

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

If the sum of all users' claimable deltas in the merkle tree exceeds `kernel.balanceOf(address(this))` at the time claims are processed, the `safeTransfer` calls for the last claimants will revert with an ERC-20 insufficient-balance error. Those users' yield is frozen: their `userClaims` state is not updated (the revert rolls back the state change at line 334–335), so they can retry, but the contract has no tokens to pay them. Unless the owner manually tops up the contract, those rewards are permanently inaccessible. [6](#0-5) 

---

### Likelihood Explanation

**Medium.** The off-chain system is solely responsible for ensuring the contract is funded before `setMerkleRoot()` is called. Common failure modes include:

- Merkle root set before the corresponding token transfer is confirmed on-chain (race condition).
- Off-chain accounting error where the tree's total exceeds the deposited amount.
- Tokens accidentally sent to the wrong address or contract before the root is set.

No attacker action is required; the failure is triggered by any reward claimant who calls `claim()` or `claimAndStake()` after the balance is exhausted by earlier claimants. [7](#0-6) 

---

### Recommendation

Add a balance sufficiency check inside `setMerkleRoot()` by requiring the caller to also supply the total distribution amount `_totalAmount`, and verify it against the current contract balance:

```solidity
function setMerkleRoot(bytes32 _merkleRootToSet, uint256 _totalAmount) external onlyOwner {
    if (_merkleRootToSet == bytes32(0) || _totalAmount == 0) revert ZeroValueProvided();
    if (kernel.balanceOf(address(this)) < _totalAmount) revert InsufficientBalance();
    // ... existing logic
}
```

This mirrors the pattern recommended in the external report and ensures the contract can always satisfy all claims encoded in the active root. Apply the same fix to `MerkleDistributor.setMerkleRoot()`. [4](#0-3) 

---

### Proof of Concept

1. Owner calls `kernel.transfer(address(kernelMerkleDistributor), 900e18)` — deposits 900 KERNEL.
2. Off-chain system generates a merkle tree where 10 users each have `cumulativeAmount = 100e18` (total = 1000e18, exceeding the 900 KERNEL balance).
3. Owner calls `setMerkleRoot(root)` — succeeds with no balance check. [1](#0-0) 
4. Users 1–9 each call `claim()` — succeeds, draining 900 KERNEL (assuming `feeInBPS == 0` for simplicity).
5. User 10 calls `claim()` — `kernel.safeTransfer(account, 100e18)` reverts because `kernel.balanceOf(address(this)) == 0`. [2](#0-1) 
6. User 10's 100 KERNEL of unclaimed yield is permanently frozen unless the owner manually tops up the contract.

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L261-265)
```text
        uint256 amountToSend = _processClaim(index, account, cumulativeAmount, merkleProof);

        kernel.safeTransfer(account, amountToSend);

        emit Claimed(index, account, amountToSend);
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L270-285)
```text
    function claimAndStake(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        external
        nonReentrant
        whenNotPaused
    {
        uint256 amountToStake = _processClaim(index, account, cumulativeAmount, merkleProof);

        IKernelDepositPool(kernelDepositPool).stakeFor(account, amountToStake);

        emit ClaimedAndStaked(index, account, amountToStake);
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L333-336)
```text
        // Update user claim info
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeAmount = cumulativeAmount;

```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L338-343)
```text
        uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
        uint256 amountToSend = claimableAmount - fee;

        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L402-413)
```text
    function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
        if (_merkleRootToSet == bytes32(0)) {
            revert ZeroValueProvided();
        }

        currentMerkleRoot = _merkleRootToSet;

        currentMerkleRootIndex++;
        currentIndex++;

        emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L137-144)
```text
        // Send the claimable amount to the user - deducting the fee
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;

        IERC20(token).safeTransfer(account, amountToSend);

        // Send the fee to the protocol treasury
        IERC20(token).safeTransfer(protocolTreasury, fee);
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L156-167)
```text
    function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
        if (_merkleRootToSet == bytes32(0)) {
            revert ZeroValueProvided();
        }

        currentMerkleRoot = _merkleRootToSet;

        currentMerkleRootIndex++;
        currentIndex++;

        emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
    }
```
