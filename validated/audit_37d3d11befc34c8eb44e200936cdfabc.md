The code has been verified. The claim is accurate and the vulnerability is real.

**Verification:**

1. `MerkleDistributor.sol` line 144 unconditionally calls `IERC20(token).safeTransfer(protocolTreasury, fee)` with no zero-check. [1](#0-0) 

2. Both `initialize` and `setFeeInBPS` permit `feeInBPS = 0` — only an upper bound is enforced. [2](#0-1) [3](#0-2) 

3. `LRTWithdrawalManager.instantWithdrawal()` already applies the `if (fee > 0)` guard, confirming the protocol is aware of this pattern and intentionally uses it elsewhere. [4](#0-3) 

---

Audit Report

## Title
Unconditional Zero-Value Fee Transfer in `MerkleDistributor#claim` Blocks All Claims When `feeInBPS` Is Zero - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

## Summary
`MerkleDistributor.claim()` unconditionally calls `IERC20(token).safeTransfer(protocolTreasury, fee)` even when `fee` evaluates to zero (i.e., when `feeInBPS == 0`). Tokens that revert on zero-value transfers will cause every `claim()` invocation to revert, permanently blocking all users from claiming their allocated tokens for the duration that `feeInBPS` remains at zero.

## Finding Description
In `MerkleDistributor.sol` at lines 138–144, the `claim()` function computes a fee and unconditionally transfers it to `protocolTreasury`:

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

// Send the fee to the protocol treasury
IERC20(token).safeTransfer(protocolTreasury, fee);  // no zero-check
```

When `feeInBPS == 0`, `fee` is always `0` regardless of `claimableAmount`. The second `safeTransfer` then attempts a zero-value transfer. A well-documented class of non-standard ERC20 tokens (e.g., LEND) reverts on zero-value transfers, causing the entire `claim()` transaction to revert.

`feeInBPS = 0` is explicitly permitted: neither `initialize` (lines 77–79) nor `setFeeInBPS` (lines 198–203) enforce a non-zero lower bound — only the upper bound `MAX_FEE_IN_BPS = 1000` is checked. The `token` address is also configurable post-deployment via `setToken()`, meaning a zero-transfer-reverting token can be introduced at any time.

The `claim()` function has no access control (`whenNotPaused` only), so any address with a valid Merkle proof is affected. The protocol already applies the `if (fee > 0)` guard in `LRTWithdrawalManager.instantWithdrawal()` (lines 245–248), confirming awareness of this pattern — its absence in `MerkleDistributor` is an inconsistency.

## Impact Explanation
When `feeInBPS == 0` and the distributed token reverts on zero-value transfers, every `claim()` call reverts. All users with valid Merkle allocations are unable to claim their tokens for the entire duration that this configuration persists. This constitutes **permanent freezing of unclaimed yield** (Medium) — a concrete allowed impact. If the owner later raises `feeInBPS` above zero, the freeze becomes temporary, matching **temporary freezing of funds** (Medium).

## Likelihood Explanation
No attacker action is required. The DoS arises from the combination of two valid, independently reachable protocol configurations: (1) `feeInBPS = 0`, which can be set at initialization or via `setFeeInBPS(0)` at any time, and (2) a token that reverts on zero-value transfers, which can be configured via `setToken()`. Both are within the normal operational envelope of the contract. The `MerkleDistributor` is explicitly described as a generic distributor for arbitrary ERC20 tokens, making the use of non-standard tokens a realistic scenario.

## Recommendation
Add a zero-check before the fee transfer:

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

if (fee > 0) {
    IERC20(token).safeTransfer(protocolTreasury, fee);
}
```

This mirrors the existing guard in `LRTWithdrawalManager.instantWithdrawal()` at lines 245–248.

## Proof of Concept
1. Deploy `MerkleDistributor` with `feeInBPS = 0` (valid per `initialize`) and `token` set to any ERC20 that reverts on zero-value transfers (e.g., LEND).
2. Owner calls `setMerkleRoot(root)` with a valid Merkle root covering at least one user allocation.
3. User calls `claim(index, account, cumulativeAmount, merkleProof)` with a valid proof and `cumulativeAmount > 0`.
4. `fee = (cumulativeAmount * 0) / 10_000 = 0`.
5. `IERC20(token).safeTransfer(account, cumulativeAmount)` succeeds.
6. `IERC20(token).safeTransfer(protocolTreasury, 0)` reverts because the token rejects zero-value transfers.
7. The entire transaction reverts. All users are blocked from claiming. Repeat for every user — all claims fail identically.

**Foundry test sketch:**
```solidity
function test_claimRevertsOnZeroFeeWithRevertingToken() public {
    // Deploy mock ERC20 that reverts on zero-value transfer
    // Deploy MerkleDistributor with feeInBPS = 0
    // Set merkle root, fund distributor
    // Expect revert on claim()
    vm.expectRevert();
    distributor.claim(index, account, amount, proof);
}
```

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L77-79)
```text
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L138-144)
```text
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;

        IERC20(token).safeTransfer(account, amountToSend);

        // Send the fee to the protocol treasury
        IERC20(token).safeTransfer(protocolTreasury, fee);
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L198-203)
```text
    function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }

        feeInBPS = _feeInBPS;
```

**File:** contracts/LRTWithdrawalManager.sol (L245-248)
```text
        if (fee > 0) {
            _transferAsset(asset, feeRecipient, fee);
            emit InstantWithdrawalFeeCollected(msg.sender, asset, fee);
        }
```
