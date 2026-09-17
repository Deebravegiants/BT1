# [M] Possible to grief and prevent all users from claiming via front-running `multiClaim()` calls

## Summary
Severity: Medium
Chain: Smart contract
Component: Paladin
Published: 2024-02-07
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/18
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0x817995d3f1136e0a82180f5bd5384b9c6e324737ac69a74fd720e8f542ba7d9c
**Severity:** medium

**Description:**
## Impact
Griefing users with gas fees and reverting transactions. Blocking all multi claims.

## Description
The root of the problem is that anyone can claim rewards on behalf of an `account` in `MultiMerkleDistributorV2.sol` claim functions. This allows an attacker to monitor `multiClaim()` and `claimQuest()` calls to the contract and front-run them with a `claim()` with exactly the same valid parameters as the user including the `merkleProof`. To maximize griefing impact aka gas fees paid by the user, the attacker will copy the last `claim` of the user so that the user will have to pay for the previous `claims` but the function will still fail. 

**Note:** The attacker can monitor the `MultiMerkleDistributorV2` contract and do this with each and every `multiClaim()` and `claimQuest()` calls made by the users. This would essentially disable any multi claim functionality and force users to use single claim on each of their quest reward claims.

## Proof of Concept
1. User calls `multiClaim()` with `7` `claims`
2. Attacker reads `calldata` params of the user's transaction, including user's `merkleProof`
3. Attacker front-runs user's `multiClaim()` tx and calls `claim()` with the last claim of the user (copying their claim params)
4. User's transaction will fail on their last `claim` in the `multiClaim()` call (because of attacker already claimed on their behalf and `isClaimed()` check will fail) and the user has to pay for all of the gas fees for the reverting transaction up to that point
5. User is frustrated and calls `multiClaim()` again with `6` `claims`, excluding the already claimed `claim` by the attacker
6. Attacker simply repeats their exploit and front-run the user again to grief them with gas fees one more time
7. Either the user is forced to claim their claims one by one or the attacker has more chances to grief them. It doesn't matter for the attacker as he can easily find more victims.

## Recommendation
Consider to disallow arbitrary `account` address claims on `multiClaim()` and `claimQuest()`  functions and only allow the `msg.sender` to claim. This would reduce some flexibility, but improve safety and completely prevent this attack and this type of front-running attacks. Optionally the functionality could be extended so that the `user` could allow some addresses that can claim on behalf of their `account`.

**Alternative:** A different radical type of mitigation could be to completely remove `multiClaim()` and `claimQuest()` and handle multiple claim loops on the front-end.
