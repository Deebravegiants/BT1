Audit Report

## Title
Unrestricted `claim` Caller Allows Any Address to Force Fee-Bearing Claims on Behalf of Any User - (File: `contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

## Summary
`MerkleDistributor.claim` accepts an arbitrary `account` parameter with no restriction that `msg.sender == account`. Any unprivileged caller can supply a valid merkle proof and trigger a claim for any user, causing the user's tokens to be transferred to them minus a protocol fee of up to 10% (`MAX_FEE_IN_BPS = 1000`). Once claimed, the state is permanently updated and the user cannot reclaim the deducted fee.

## Finding Description
The `claim` function at `contracts/utils/MerkleDistributor/MerkleDistributor.sol` L97–147 performs no check that `msg.sender == account`: [1](#0-0) 

All validation is purely merkle-proof-based — the proof is necessarily published off-chain for users to claim, so any observer can reconstruct valid `(index, account, cumulativeAmount, merkleProof)` tuples for any user. After proof verification, the contract deducts a fee and marks the claim as used: [2](#0-1) 

`userClaims[account].lastClaimedIndex` is updated to `index`, so `isClaimed` returns `true` for that user afterward, permanently preventing re-claim. The fee (up to 10%) is sent to `protocolTreasury`, not to the attacker.

By contrast, `KernelMerkleDistributor._processClaim` correctly enforces the caller restriction: [3](#0-2) 

`MerkleDistributor` is entirely missing this guard.

The concrete harm materializes when `feeInBPS > 0` (up to `MAX_FEE_IN_BPS = 1000`, i.e. 10%): [4](#0-3) 

A user waiting for the owner to reduce `feeInBPS` (e.g., to 0) before claiming can be front-run: an attacker forces the claim at the current higher fee rate, locking in the fee deduction before the reduction takes effect. The user permanently loses the fee delta with no recourse.

## Impact Explanation
**High — Theft of unclaimed yield.**

When `feeInBPS > 0`, an attacker can force any user's claim at the prevailing fee rate, permanently redirecting up to 10% of the user's entitled yield to `protocolTreasury`. The user cannot undo the claim or recover the fee. This is a direct, irreversible loss of unclaimed yield from any user whose merkle data is publicly available, matching the allowed impact "High. Theft of unclaimed yield."

## Likelihood Explanation
**High.** Merkle tree data (index, account, cumulativeAmount, proof) must be published off-chain for users to claim. Any observer can reconstruct valid call parameters for any user. No special privilege, capital, or timing is required beyond gas. The attack is most profitable when front-running a pending `feeInBPS` reduction (owner calls `setFeeInBPS` to lower the fee), which an attacker can monitor on-chain and exploit in the same block. It can be automated to target all users simultaneously.

## Recommendation
Add a caller restriction identical to the one in `KernelMerkleDistributor._processClaim`:

```solidity
function claim(
    uint256 index,
    address account,
    uint256 cumulativeAmount,
    bytes32[] calldata merkleProof
) external override whenNotPaused {
    if (account != msg.sender) revert Unauthorized();
    // ... rest of existing logic
}
```

This ensures only the rightful owner can trigger their own claim and decide when to incur the fee.

## Proof of Concept
1. Protocol publishes merkle tree. Alice's leaf: `(index=5, account=Alice, cumulativeAmount=1000e18)`. `feeInBPS = 500` (5%).
2. Owner submits a transaction to call `setFeeInBPS(0)`.
3. Attacker observes the pending `setFeeInBPS(0)` transaction in the mempool.
4. Attacker front-runs it by calling `MerkleDistributor.claim(5, Alice, 1000e18, aliceProof)` with higher gas.
5. Contract verifies proof (valid), computes `fee = 1000e18 * 500 / 10000 = 50e18`.
6. Alice receives `950e18`; `50e18` goes to `protocolTreasury`.
7. `userClaims[Alice].lastClaimedIndex = 5` — Alice's claim is permanently marked as used.
8. `setFeeInBPS(0)` executes afterward, but Alice's claim is already consumed.
9. Alice calls `claim` herself → reverts with `AlreadyClaimed`.
10. Alice has permanently lost `50e18` tokens she would have received in full had she claimed after the fee reduction.

**Foundry test sketch:**
```solidity
function test_forcedClaimAtHighFee() public {
    // Setup: deploy MerkleDistributor with feeInBPS=500, set merkle root
    // Alice's leaf in tree: (index=1, Alice, 1000e18)
    vm.prank(attacker);
    distributor.claim(1, alice, 1000e18, aliceProof);
    // Assert alice received 950e18, treasury received 50e18
    assertEq(token.balanceOf(alice), 950e18);
    assertEq(token.balanceOf(treasury), 50e18);
    // Assert alice cannot claim again
    vm.prank(alice);
    vm.expectRevert(IMerkleDistributor.AlreadyClaimed.selector);
    distributor.claim(1, alice, 1000e18, aliceProof);
}
```

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L47-47)
```text
    uint256 public constant MAX_FEE_IN_BPS = 1000;
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

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L133-146)
```text
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
