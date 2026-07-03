Audit Report

## Title
Unconditional Zero-Amount `safeTransfer` to `protocolTreasury` Permanently Freezes All Claims When `feeInBPS == 0` - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

## Summary
`MerkleDistributor.sol`'s `claim()` function unconditionally calls `IERC20(token).safeTransfer(protocolTreasury, fee)` at line 144 even when `fee` is zero. When `feeInBPS` is set to `0`, any token that reverts on zero-value transfers will cause every `claim()` invocation to revert, permanently blocking all users from withdrawing their entitled tokens. The sibling contract `KernelMerkleDistributor` correctly guards this transfer with `if (fee > 0)`, confirming the intended pattern.

## Finding Description
In `MerkleDistributor.sol`, the `claim()` function computes the fee and unconditionally transfers it:

```solidity
// Line 138-144
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

// Send the fee to the protocol treasury
IERC20(token).safeTransfer(protocolTreasury, fee);  // ← no zero-check
``` [1](#0-0) 

`setFeeInBPS` explicitly permits `0` as a valid value (only values `> MAX_FEE_IN_BPS` are rejected): [2](#0-1) 

When `feeInBPS == 0`, `fee == 0` for every claim, and `safeTransfer(protocolTreasury, 0)` is executed unconditionally. Tokens such as BNB and LEND revert on zero-value transfers, causing every `claim()` call to revert after the user's state has already been updated (lines 134–135), meaning the user's `lastClaimedIndex` and `cumulativeAmount` are written before the revert — but since the entire transaction reverts, state is rolled back and the user is permanently blocked from claiming.

`KernelMerkleDistributor._processClaim()` correctly guards this transfer: [3](#0-2) 

`MerkleDistributor` lacks this guard entirely.

## Impact Explanation
**Medium — Permanent freezing of unclaimed yield.** When `feeInBPS == 0` and the distributed token reverts on zero-value transfers, every `claim()` call reverts at the unconditional `safeTransfer(protocolTreasury, 0)` line. No user can claim any tokens. The tokens remain locked in the contract with no user-accessible recovery path. Setting `feeInBPS > 0` to work around the bug would incorrectly charge users a fee they were not supposed to pay.

## Likelihood Explanation
`feeInBPS == 0` is a natural and expected configuration for a zero-fee distribution. The `MerkleDistributor` is explicitly described as a generic contract whose `token` is set by the owner and can be any ERC20. The combination of a zero-fee configuration and a token that reverts on zero-value transfers requires no attacker action — any user calling `claim()` triggers the revert. No privileged collusion or external compromise is needed.

## Recommendation
Add a zero-amount guard before the fee transfer, mirroring the pattern already used in `KernelMerkleDistributor`:

```solidity
if (fee > 0) {
    IERC20(token).safeTransfer(protocolTreasury, fee);
}
```

## Proof of Concept
1. Owner deploys `MerkleDistributor` with token `T` that reverts on zero-value transfers (e.g., BNB).
2. Owner calls `setFeeInBPS(0)` — a zero-fee configuration, explicitly permitted by the contract.
3. Owner sets a merkle root; users are entitled to claim tokens.
4. User calls `claim(index, account, cumulativeAmount, merkleProof)` with a valid proof.
5. `claimableAmount > 0`, `fee = (claimableAmount * 0) / 10_000 = 0`, `amountToSend = claimableAmount`.
6. `IERC20(T).safeTransfer(account, amountToSend)` succeeds.
7. `IERC20(T).safeTransfer(protocolTreasury, 0)` reverts because token `T` does not allow zero-value transfers.
8. The entire transaction reverts. The user receives nothing. All subsequent `claim()` calls by any user revert identically. All claimable tokens are permanently frozen in the contract.

**Foundry test plan:** Deploy a mock ERC20 that reverts on `transfer(addr, 0)`, initialize `MerkleDistributor` with it and `feeInBPS = 0`, set a merkle root, and call `claim()` with a valid proof — assert the call reverts. Then apply the `if (fee > 0)` guard and assert the call succeeds.

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
