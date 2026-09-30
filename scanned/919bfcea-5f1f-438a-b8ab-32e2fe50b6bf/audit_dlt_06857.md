# [M] not able to create claim

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-vtvl
Published: 2022-09-22
Source: https://github.com/code-423n4/2022-09-vtvl-findings/issues/140
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-09-vtvl/blob/f68b7f3e61dad0d873b5b5a1e8126b839afeab5f/contracts/VTVLVesting.sol#L418-L437
https://github.com/code-423n4/2022-09-vtvl/blob/f68b7f3e61dad0d873b5b5a1e8126b839afeab5f/contracts/VTVLVesting.sol#L245-L253
https://github.com/code-423n4/2022-09-vtvl/blob/f68b7f3e61dad0d873b5b5a1e8126b839afeab5f/contracts/VTVLVesting.sol#L123-L140


# Vulnerability details

## Impact
if admin revoked any recipient’s claim, admin can not create claim for the same recipient because `startTimestamp` is not updated to initial value on revoke claim.
There will be a need to create a claim again for any reason like, 1. mistakenly revoked claim 2. Wrong info provided to claim 3. new vesting period starts, etc.


## Proof of Concept
1. Alice create claim for Bob
2. Alice revoke claim of Bob
    - On r`evokeClaim()`, claim’s isActive will be false, but `startTimestamp` will be remain as it is
    - https://github.com/code-423n4/2022-09-vtvl/blob/f68b7f3e61dad0d873b5b5a1e8126b839afeab5f/contracts/VTVLVesting.sol#L418-L437
3. Alice try to create claim for Bob but claim will not create because it has modifier `hasNoClaim()` which is checked for claim should not active and it checks for `require(_claim.startTimestamp == 0, "CLAIM_ALREADY_EXISTS");`
-    https://github.com/code-423n4/2022-09-vtvl/blob/f68b7f3e61dad0d873b5b5a1e8126b839afeab5f/contracts/VTVLVesting.sol#L245-L253
-    https://github.com/code-423n4/2022-09-vtvl/blob/f68b7f3e61dad0d873b5b5a1e8126b839afeab5f/contracts/VTVLVesting.sol#L123-L140


## Tools Used
Manual Analysis

## Recommended Mitigation Steps
Update `startTimestamp to 0` on `revokeClaim()`
