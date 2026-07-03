Audit Report

## Title
Attacker Can Front-Run Victim's First Claim by Seeding a Stale Cumulative Baseline — (`contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol`)

## Summary

`claim()` accepts an arbitrary `account` parameter with no `msg.sender == account` restriction, and the index guard permits any value in `[1, currentIndex]`. An attacker can call `claim` on behalf of a victim at a stale lower index before the victim acts, permanently setting the victim's cumulative baseline to a historical value. The victim's subsequent claim at `currentIndex` then yields only the delta above that injected baseline, permanently reducing their Blast Points and Blast Gold entitlement.

## Finding Description

**Root cause 1 — no caller restriction.**
`claim()` at [1](#0-0)  accepts an arbitrary `account` with no `require(msg.sender == account)` guard, allowing any third party to submit a claim on behalf of any address.

**Root cause 2 — index range permits historical indices.**
The only index guard at [2](#0-1)  rejects `index == 0` and `index > currentIndex`, but accepts any value in `[1, currentIndex]`. A claim at `oldIndex < currentIndex` is structurally valid.

**Root cause 3 — `isClaimed` uses `>=`, not `==`.** [3](#0-2)  returns `true` only when `lastClaimedIndex >= index`. For a first-time claimant (`lastClaimedIndex == 0`), every index from 1 to `currentIndex` passes the `!isClaimed` check.

**Root cause 4 — baseline is overwritten with the claimed cumulative.**
After a successful claim, [4](#0-3)  sets `lastClaimedIndex`, `cumulativeBlastPointAmount`, and `cumulativeBlastGoldAmount` to the leaf values. Any future claim at a higher index subtracts this injected baseline.

**Attack sequence (precondition: current root encodes leaves for both index 1 and index 2 for the victim — the expected design given the contract allows `index < currentIndex`):**

| Step | Actor | Action | State after |
|------|-------|--------|-------------|
| 1 | Attacker | `claim(1, victim, 100, 10, proof1)` | `victim.lastClaimedIndex=1`, baselines=(100,10) |
| 2 | Victim | `claim(2, victim, 200, 20, proof2)` | receives `200-100=100` pts, `20-10=10` gold |
| — | Expected | victim claims at index 2 first | would receive `200-0=200` pts, `20-0=20` gold |

The attacker spends only gas; their own claim state is unaffected. The victim's loss is permanent because `lastClaimedIndex=1` prevents re-claiming at index 1, and the baseline is already set.

## Impact Explanation

The `Claimed` event at [5](#0-4)  records the reduced `claimableBlastPoints`/`claimableBlastGold`. The off-chain Blast Points operator distributes yield based on these events. The victim permanently receives fewer Blast Points and Blast Gold than their full cumulative entitlement — a direct, partial theft of unclaimed yield. This matches the allowed impact: **High — Theft of unclaimed yield**.

## Likelihood Explanation

- No special role or privilege is required; `claim()` is a public, permissionless function.
- The attacker only needs a valid Merkle proof for `(oldIndex, victim, lowCumulative, lowGold)` against the current root. This is available whenever the operator publishes a tree that includes leaves for multiple historical indices — which is the implied design, since the contract explicitly permits `index < currentIndex` and uses a cumulative accounting model.
- The attack can be executed as a front-run or at any time before the victim's first claim.
- No funds are at risk for the attacker; cost is a single transaction.

## Recommendation

1. **Restrict `claim` to the account itself:** Add `require(msg.sender == account, "caller != account")` at the top of `claim()`. This eliminates the ability for any third party to set another user's baseline.
2. **Alternatively, only allow claiming at `currentIndex`:** Change the index check to `require(index == currentIndex)`, so stale-index leaves are never usable.
3. **Or track claimed state per index:** Use `mapping(address => mapping(uint256 => bool))` so a claim at index 1 does not affect the baseline for index 2.

## Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Foundry test outline:
// 1. Deploy MerkleBlastPointsDistributor (proxy + initialize).
// 2. Build a two-leaf Merkle tree:
//    leaf1 = keccak256(abi.encodePacked(uint256(1), victim, uint256(100), uint256(10)))
//    leaf2 = keccak256(abi.encodePacked(uint256(2), victim, uint256(200), uint256(20)))
//    root  = merkleRoot([leaf1, leaf2])
// 3. Owner calls setMerkleRoot(root) twice so currentIndex == 2 and currentMerkleRoot == root.
//    (Both calls use the same root so both index-1 and index-2 proofs verify against it.)

// Attack:
// 4. Attacker (any address) calls:
distributor.claim(1, victim, 100, 10, proof1);
// State: victim.lastClaimedIndex=1, cumulativeBlastPointAmount=100, cumulativeBlastGoldAmount=10

// 5. Victim calls:
distributor.claim(2, victim, 200, 20, proof2);
// claimableBlastPoints = 200 - 100 = 100  (expected: 200)
// claimableBlastGold   = 20  - 10  = 10   (expected: 20)

// Assert:
// Claimed event emits (2, victim, 100, 10) instead of (2, victim, 200, 20).
// Victim permanently lost 100 Blast Points and 10 Blast Gold.
// Re-claiming at index 1 reverts with AlreadyClaimed (isClaimed(1, victim) == true).
```

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L79-83)
```text
    function isClaimed(uint256 index, address account) public view override returns (bool) {
        if (index == 0) revert ZeroValueProvided();

        return userClaims[account].lastClaimedIndex >= index;
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L86-96)
```text
    function claim(
        uint256 index,
        address account,
        uint256 cumulativeBlastPointAmount,
        uint256 cumulativeBlastGoldAmount,
        bytes32[] calldata merkleProof
    )
        external
        override
        whenNotPaused
    {
```

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L101-103)
```text
        if (index == 0 || index > currentIndex) {
            revert InvalidIndex();
        }
```

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L126-128)
```text
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeBlastPointAmount = cumulativeBlastPointAmount;
        userClaims[account].cumulativeBlastGoldAmount = cumulativeBlastGoldAmount;
```

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L130-130)
```text
        emit Claimed(index, account, claimableBlastPoints, claimableBlastGold);
```
