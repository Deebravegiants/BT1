# [M] 5.2.5 Reduce impact ofemergencyUpdatequestPeriod()

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** MultiMerkleDistributor.sol#L311-L

**Description:** FunctionemergencyUpdatequestPeriod()allows the merkle tree to be updated.

The merkle tree contains an embedded index parameter which is used to prevent double claims. When the
merkleRoot is updated, the layout of indexes in the merkle tree could become different.

Example:

```
Suppose the initial merkle tree contains information for:
```
- user A: index=1, account = 0x1234, amount=
- user B: index=2, account = 0x5689, amount=
Then user A claims => _setClaimed(..., 1) is set.

```
Now it turns out a mistake is made with the merkle tree, and it should contain:
```
- user B: index=1, account = 0x5689, amount=
- user C: index=2, account = 0xabcd, amount=

```
Now user B will not be able to claim because bit 1 has already been set.
```
Under this situation the following issues can occur:

- Someone who has already claimed might be able to claim again.
- Someone who has already claimed has too much.
- Someone who has already claimed has too little, and cannot longer claim the rest because_setClaimed()
    has already been set.
- someone who has not yet claimed might not be able to claim because_setClaimed()has already been set
    by another user.

Note: Set to medium risk because the likelihood of this happening is low, but the impact is high.

**Recommendation:** The following steps can be taken to reduce the impact:

- Only allow an update if no claims have been done yet, by checking no bits have been set yet. However this
    has limited use.


- Make sure the index number of a user always stays the same, although this doesn’t help if the user is entitled
    to an higher amount.
- Exclude already claimed tokens from the new merkle tree. To prevent claiming in the mean time, it might be
    a good idea to pause the claiming to make sure no claims are done in the mean time. Reset all the bits after
    the update.
- Consider storing how much each account has claimed and allow the account to claim less on future claims,
    in case the account has claimed too much. However this requires some complicated logic.

Note: The contract needs to store the size of the merkle tree (e.g. the largest index) to be able to check/reset all
the bits.

**Paladin:** In the case where a new amount of token is transferred to the contract to cover losses from wrong
calculated claims, we might need to change that amount to allow them to claim. Added a parameteraddedRewards
to increasequestRewardsPerPeriod, but never decrease it. Implemented in #16.

Explanation for the emergency update procedure:

1. Block claims for the Quest period by using this method to set an incorrect MerkleRoot, where no proof
    matches the root.
2. Prepare a new Merkle Tree, taking into account previous user claims on that period and missing/overpaid
    rewards. a) For all new claims to be added, set them after the last index of the previous Merkle Tree. b) For
    users that did not claim, keep the same index and adjust the amount to be claimed if needed. c) For indexes
    that were claimed, place an empty node in the Merkle Tree (with an amount at 0 & the address0xdeadas
    the account).
3. Update the Quest period with the correct MerkleRoot (no need to change the Bitmap, as the new MerkleTree
    will account for the indexes already claimed).

**Spearbit:** Acknowledged. Implemented in part technically and procedurally.
