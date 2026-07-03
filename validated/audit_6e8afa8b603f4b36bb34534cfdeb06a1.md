### Title
Unconditional Zero-Value `safeTransfer` to `protocolTreasury` in `claim()` Permanently Blocks All User Claims When `feeInBPS` Is Zero — (File: `contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

---

### Summary

`MerkleDistributor.sol`'s `claim()` function unconditionally calls `safeTransfer(protocolTreasury, fee)` even when `fee == 0`. For ERC20 tokens that revert on zero-value transfers (e.g., USDT), this causes every single user claim to revert whenever `feeInBPS` is set to zero, permanently freezing all unclaimed yield in the distributor.

---

### Finding Description

In `MerkleDistributor.sol`, the `claim()` function computes a fee and then unconditionally transfers it to `protocolTreasury`:

```solidity
// contracts/utils/MerkleDistributor/MerkleDistributor.sol  lines 138–144
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

// Send the fee to the protocol treasury
IERC20(token).safeTransfer(protocolTreasury, fee);   // ← unconditional
``` [1](#0-0) 

When `feeInBPS == 0`, `fee` evaluates to `0`, and `safeTransfer(protocolTreasury, 0)` is still executed. Several widely-deployed ERC20 tokens (USDT being the canonical example) revert on zero-value transfers. Because `MerkleDistributor` is a generic distributor whose `token` can be set to any ERC20 via `setToken()`, this path is reachable in production. [2](#0-1) 

The `initialize()` function imposes **no lower bound** on `_feeInBPS` — it only rejects values above `MAX_FEE_IN_BPS` — so the contract can be deployed with `feeInBPS = 0` from day one:

```solidity
// contracts/utils/MerkleDistributor/MerkleDistributor.sol  lines 71–87
function initialize(address token_, address _protocolTreasury, uint256 _feeInBPS) external initializer {
    ...
    if (_feeInBPS > MAX_FEE_IN_BPS) {   // only upper bound; 0 is accepted
        revert InvalidFeeInBPS();
    }
    ...
    feeInBPS = _feeInBPS;
}
``` [3](#0-2) 

Similarly, `setFeeInBPS(0)` is a valid owner call at any time after deployment: [4](#0-3) 

**Contrast with `KernelMerkleDistributor`**, which correctly guards the fee transfer:

```solidity
// contracts/KERNEL/KernelMerkleDistributor.sol  lines 341–343
if (fee > 0) {
    kernel.safeTransfer(protocolTreasury, fee);
}
``` [5](#0-4) 

`MerkleDistributor` is missing this guard entirely.

---

### Impact Explanation

When `feeInBPS == 0` and the distributed token reverts on zero-value transfers, **every call to `claim()` reverts** after the user's tokens have already been accounted for (state is updated at lines 134–135 before the transfer). All users are blocked from withdrawing their entitled yield. The tokens remain locked in the contract with no user-accessible exit path until the owner intervenes.

Impact classification: **Medium — Permanent freezing of unclaimed yield** (until owner corrects `feeInBPS`). [6](#0-5) 

---

### Likelihood Explanation

- `feeInBPS = 0` is a legitimate, non-adversarial owner action (e.g., "remove protocol fees"). No key compromise or governance capture is required.
- The contract is generic; it can be pointed at any ERC20 token via `setToken()`. USDT and several other production tokens revert on zero-value transfers.
- The combination of `feeInBPS = 0` (or initialized as 0) with such a token is a realistic deployment scenario.

---

### Recommendation

Mirror the guard used in `KernelMerkleDistributor`:

```solidity
if (fee > 0) {
    IERC20(token).safeTransfer(protocolTreasury, fee);
}
```

Apply this fix at line 143–144 of `MerkleDistributor.sol`. Additionally, consider whether `feeInBPS = 0` should be explicitly allowed or rejected at initialization and in `setFeeInBPS`.

---

### Proof of Concept

1. Deploy `MerkleDistributor` with `token = USDT`, `feeInBPS = 0`, valid `protocolTreasury`.
2. Owner calls `setMerkleRoot(root)` with a valid distribution.
3. User calls `claim(index, account, cumulativeAmount, proof)` with a valid proof.
4. Execution reaches line 138: `fee = (claimableAmount * 0) / 10_000 = 0`.
5. Line 141: `safeTransfer(account, claimableAmount)` succeeds.
6. Line 144: `safeTransfer(protocolTreasury, 0)` — USDT reverts on zero-value transfer.
7. The entire transaction reverts. The user receives nothing. State is rolled back.
8. Every subsequent `claim()` call by any user hits the same revert. All unclaimed yield is frozen. [7](#0-6)

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

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L96-147)
```text
    /// @inheritdoc IMerkleDistributor
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
    }
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
