Audit Report

## Title
Unchecked `msg.sender` in `claim()` Allows Anyone to Force-Claim on Behalf of Any User, Extracting Fees Without Consent - (`contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

## Summary

`MerkleDistributor.claim()` accepts a caller-supplied `account` parameter but never verifies that `msg.sender == account`. Because all Merkle proof data is public, any unprivileged caller can submit a valid proof for any eligible user, permanently consuming that user's claim state and routing the protocol fee to `protocolTreasury` without the user's knowledge or consent. The user receives the post-fee amount, but the fee portion of their unclaimed yield is irreversibly extracted.

## Finding Description

`MerkleDistributor.claim()` performs no authorization check on the relationship between `msg.sender` and `account`: [1](#0-0) 

The Merkle proof only proves that `account` is entitled to `cumulativeAmount`; it does not prove that the caller is `account`. After proof verification, the fee is computed and deducted: [2](#0-1) 

The claim state is then permanently consumed: [3](#0-2) 

By contrast, `KernelMerkleDistributor._processClaim()` explicitly enforces the caller identity check: [4](#0-3) 

`MerkleDistributor` has no equivalent guard, making the missing check a clear omission relative to the sibling contract's design.

## Impact Explanation

**High — Theft of unclaimed yield.** When a forced claim is executed, `fee = claimableAmount * feeInBPS / 10_000` is sent to `protocolTreasury` rather than to the user. If the owner later reduces `feeInBPS`, a user who intended to wait would have received more tokens net of fees. By forcing the claim at the current (higher) fee rate, the attacker permanently reduces the user's realized yield. The claim state is marked consumed, so the user can never reclaim at a more favorable rate. The principal (`amountToSend`) is correctly delivered to `account`, so this is yield theft, not principal theft.

## Likelihood Explanation

All inputs required to call `claim()` — `index`, `account`, `cumulativeAmount`, and `merkleProof` — are derived from public off-chain distribution data or observable on-chain events. No special privilege, role, or insider access is required. Any EOA can execute this against any eligible user at any time while the contract is unpaused. The attack is trivially repeatable across all eligible accounts in a single block.

## Recommendation

Add a `msg.sender == account` guard inside `claim()`, mirroring the pattern already enforced in `KernelMerkleDistributor._processClaim()`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
```

Alternatively, remove the `account` parameter entirely and derive it from `msg.sender` directly, eliminating the ambiguity at the interface level.

## Proof of Concept

1. Deploy `MerkleDistributor` with `feeInBPS = 500` (5%).
2. Set a Merkle root that entitles Alice (`alice`) to `1000e18` tokens at `index = 1`.
3. Alice decides to wait, anticipating the owner will call `setFeeInBPS(0)`.
4. Bob (attacker) reads Alice's `(index, account, cumulativeAmount, merkleProof)` from the public off-chain distribution data.
5. Bob calls `MerkleDistributor.claim(1, alice, 1000e18, proof)` from his own EOA.
6. The call succeeds: Alice receives `950e18` tokens; `50e18` tokens go to `protocolTreasury`.
7. `userClaims[alice].lastClaimedIndex = 1` and `userClaims[alice].cumulativeAmount = 1000e18` are set.
8. Alice's claim is permanently consumed. Even if the owner later sets `feeInBPS = 0`, Alice cannot reclaim; `isClaimed(1, alice)` returns `true` and any retry reverts with `AlreadyClaimed`.

**Foundry test sketch:**
```solidity
function test_forceClaim() public {
    // Setup: alice is eligible for 1000e18, feeInBPS = 500
    vm.prank(bob); // attacker
    distributor.claim(1, alice, 1000e18, aliceProof);
    // Alice receives 950e18, treasury receives 50e18
    assertEq(token.balanceOf(alice), 950e18);
    assertEq(token.balanceOf(treasury), 50e18);
    // Alice's claim is consumed
    assertTrue(distributor.isClaimed(1, alice));
}
```

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

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L134-135)
```text
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
