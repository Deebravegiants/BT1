Audit Report

## Title
Unauthorized Forced Claim Enables Fee Theft from Any User - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

## Summary

`MerkleDistributor.claim` accepts a caller-supplied `account` parameter with no check that `msg.sender == account`. Any caller with a valid merkle proof for a victim can force-claim on the victim's behalf, triggering the fee deduction at the current `feeInBPS` rate and permanently diverting up to 10% of the victim's claimable amount to `protocolTreasury`. The sister contract `KernelMerkleDistributor` explicitly guards against this with `if (account != msg.sender) { revert Unauthorized(); }`, confirming the protocol recognizes the requirement but omitted it from the generic distributor.

## Finding Description

`MerkleDistributor.claim` (L97–147) accepts `account` as a caller-supplied parameter and performs no authorization check before executing the fee-deducting transfer: [1](#0-0) 

The fee is computed and the remainder sent to `account`, with the fee permanently sent to `protocolTreasury`: [2](#0-1) 

`feeInBPS` is mutable up to `MAX_FEE_IN_BPS = 1000` (10%): [3](#0-2) 

Merkle proofs are public off-chain data. An attacker reads the proof for any victim and calls `claim` with the victim's `account`. The contract marks the claim as consumed (`userClaims[account].lastClaimedIndex = index`), making re-claim impossible, while the fee is permanently lost. [4](#0-3) 

By contrast, `KernelMerkleDistributor._processClaim` explicitly blocks this at L311–313: [5](#0-4) 

## Impact Explanation

This is **High — Theft of unclaimed yield**. The victim's unclaimed token allocation is permanently reduced by up to 10% (`MAX_FEE_IN_BPS = 1000`). The fee is irreversibly transferred to `protocolTreasury`; the claim slot is consumed and cannot be re-claimed. Users who deliberately defer claiming to wait for `feeInBPS` to be reduced or zeroed are robbed of that yield with no recourse.

## Likelihood Explanation

Merkle proofs are published off-chain for users to self-claim. An attacker requires only the victim's `index`, `account`, `cumulativeAmount`, and the corresponding proof — all public data. No privileged access, no victim interaction, and no special on-chain conditions are required. The attack is trivially scriptable and can be applied to every eligible account in the tree simultaneously whenever `feeInBPS > 0`.

## Recommendation

Add the same guard present in `KernelMerkleDistributor._processClaim` at the top of `MerkleDistributor.claim`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
```

Alternatively, remove the `account` parameter entirely and use `msg.sender` as the recipient throughout.

## Proof of Concept

1. Owner publishes merkle root; `feeInBPS = 500` (5%).
2. Victim holds valid leaf `(index=1, account=victim, cumulativeAmount=1000e18)` and is waiting for `setFeeInBPS(0)`.
3. Attacker reads the published proof and calls:
   ```solidity
   merkleDistributor.claim(1, victim, 1000e18, victimProof);
   ```
4. Contract executes: `fee = 50e18`, `amountToSend = 950e18`.
5. Victim receives `950e18`; `50e18` is permanently sent to `protocolTreasury`.
6. `userClaims[victim].lastClaimedIndex = 1` — victim can never re-claim; 50 tokens are gone.

**Foundry test plan:** Deploy `MerkleDistributor`, initialize with `feeInBPS = 500`, set a merkle root for a victim leaf, call `claim` from a separate attacker address supplying the victim's proof, assert victim received `950e18` and `protocolTreasury` received `50e18`, assert `isClaimed(1, victim) == true`.

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L47-51)
```text
    uint256 public constant MAX_FEE_IN_BPS = 1000;

    address public override token;
    address public protocolTreasury;
    uint256 public feeInBPS;
```

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

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L133-135)
```text
        // Update user claim info, and send the token.
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeAmount = cumulativeAmount;
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L138-144)
```text
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;

        IERC20(token).safeTransfer(account, amountToSend);

        // Send the fee to the protocol treasury
        IERC20(token).safeTransfer(protocolTreasury, fee);
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L311-313)
```text
        if (account != msg.sender) {
            revert Unauthorized();
        }
```
