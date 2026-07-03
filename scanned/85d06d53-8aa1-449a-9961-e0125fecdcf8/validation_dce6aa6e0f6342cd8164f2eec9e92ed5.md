### Title
Unchecked `account` Parameter in `MerkleDistributor.claim()` Allows Anyone to Force-Claim for Any User, Stealing Their Fee-Portion of Yield — (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

---

### Summary

`MerkleDistributor.claim()` accepts an arbitrary `account` address without verifying that `msg.sender == account`. Any external caller who possesses a valid merkle proof for a victim can force-trigger the victim's claim at any time, causing the protocol fee to be deducted from the victim's allocation without their consent. The victim permanently loses the fee portion of their unclaimed yield.

---

### Finding Description

The `claim()` function in `MerkleDistributor` takes `account` as a caller-supplied parameter and transfers tokens to that address after deducting a fee. There is no check that `msg.sender == account`. [1](#0-0) 

The function verifies only that the merkle proof is valid for the supplied `(index, account, cumulativeAmount)` tuple: [2](#0-1) 

It then deducts a fee of up to 10% (`MAX_FEE_IN_BPS = 1000`) and sends the remainder to `account`, with the fee going to `protocolTreasury`: [3](#0-2) 

Merkle proofs for all eligible users are published off-chain (the README explicitly states users obtain proofs from "off-chain services or tools"). An attacker can observe any user's proof and call `claim()` on their behalf at any time, forcing the fee deduction.

By contrast, `KernelMerkleDistributor._processClaim()` correctly enforces `account == msg.sender`: [4](#0-3) 

`MerkleDistributor` has no equivalent guard.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

The victim receives `claimableAmount - fee` instead of `claimableAmount`. The fee (up to 10%) is permanently redirected to `protocolTreasury` without the victim's consent. The victim cannot reclaim it; the state is updated (`userClaims[account].cumulativeAmount = cumulativeAmount`) so the claim is marked consumed. The victim has no way to prevent or reverse this. [5](#0-4) 

---

### Likelihood Explanation

**High.** The entry path requires no special role or privilege — only a valid merkle proof, which is publicly distributed off-chain to all eligible users. Any observer of the off-chain proof distribution can immediately execute the attack against any victim. No capital is required and no on-chain state needs to be manipulated beforehand. [6](#0-5) 

---

### Recommendation

Add a caller check at the top of `claim()` (mirroring `KernelMerkleDistributor`):

```solidity
if (account != msg.sender) revert Unauthorized();
```

This ensures only the rightful owner can trigger their own claim and decide when to accept the fee deduction. [4](#0-3) 

---

### Proof of Concept

1. The protocol publishes a merkle tree. Alice is entitled to `1000 KERNEL` at `index=5`, `cumulativeAmount=1000`. Her proof `P` is publicly available.
2. `feeInBPS = 500` (5%).
3. Attacker calls `MerkleDistributor.claim(5, alice, 1000, P)`.
4. The contract verifies the proof (valid), computes `claimableAmount = 1000`, `fee = 50`, `amountToSend = 950`.
5. `950 KERNEL` is sent to Alice; `50 KERNEL` is sent to `protocolTreasury`.
6. `userClaims[alice].cumulativeAmount = 1000` — Alice's claim is permanently consumed.
7. Alice never consented to claiming now, never received the full `1000 KERNEL`, and cannot recover the `50 KERNEL` fee. [7](#0-6)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L97-106)
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
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L119-146)
```text
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

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L311-313)
```text
        if (account != msg.sender) {
            revert Unauthorized();
        }
```
