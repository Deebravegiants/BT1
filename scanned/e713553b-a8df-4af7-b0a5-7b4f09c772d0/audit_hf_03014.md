# [M] not able to create claim

## Summary
Severity: Medium
Contest weight: 0.2781
Dataset id: 16858
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If admin revoked any recipient’s claim, admin can not create claim for the same recipient because `startTimestamp` is not updated to initial value on revoke claim.  
There will be a need to create a claim again for any reason like: 1) mistakenly revoked claim, 2) wrong info provided to claim, 3) new vesting period starts, etc.

## Proof of Concept
1. Alice creates claim for Bob
2. Alice revokes claim of Bob
   * On `revokeClaim()`, claim’s `isActive` will be false, but `startTimestamp` will remain as it is
   * [VTVLVesting.sol#L418-L437](https://github.com/code-423n4/2022-09-vtvl/blob/f68b7f3e61dad0d873b5b5a1e8126b839afeab5f/contracts/VTVLVesting.sol#L418-L437)
3. Alice tries to create claim for Bob but claim will not create because it has modifier `hasNoClaim()` which is checked for claim should not active and it checks for `require(_claim.startTimestamp == 0, "CLAIM_ALREADY_EXISTS");`
4. [VTVLVesting.sol#L245-L253](https://github.com/code-423n4/2022-09-vtvl/blob/f68b7f3e61dad0d873b5b5a1e8126b839afeab5f/contracts/VTVLVesting.sol#L245-L253)
5. [VTVLVesting.sol#L123-L140](https://github.com/code-423n4/2022-09-vtvl/blob/f68b7f3e61dad0d873b5b5a1e8126b839afeab5f/contracts/VTVLVesting.sol#L123-L140)

## Recommendation
Update `startTimestamp` to 0 on `revokeClaim()`.

Downgrading to low severity. While true, why wouldn’t the employee just use a different address? There is no residual benefit to using the old address (unless it was a smart contract, which the warden doesn’t mention as part of their POC). The sponsor may want to fix this, since the fix is simple, but it poses very little risk and certainly no direct loss of funds. 

Spent a bit more time thinking about this one and do think that it qualifies as Medium severity since it does affect the availability of the protocol in a number of ways. Going to go ahead and revise to Medium. 

The vesting contract is designed to be created and used in a one-off manner and the revoke function is to prevent any mistakes made upon creation (wrong address / amount / timestamp etc.). In practical sense, if a claim (or the recipient address) is revoked, one (the admin) can always create a new vesting contract with the correct claim parameters. 

I therefore think that it is by design that the address is only able be claimable once per vesting contract, in all circumstance, the admin can re-create a new vesting contract to mitigate this issue and therefore this is a low risk / non-critical issue. 

I don’t think the tactic of deploying a new contract is the correct one here simply to be able to set up vesting for one botched person or someone whose vesting token amount changes for example. I am going to stick with the Medium severity on this one, but do appreciate the response and thoughts on possible mitigations.

I have explained one of the real use case scenarios where this protocol will fail to serve many. Refer to [issue 384](https://github.com/code-423n4/2022-09-vtvl-findings/issues/384).  
It is not always contract address or EOA which will decide the identity of a person. Each one will have unique ID. That id is going to be used in all the places.
