# [H] Disputers can recover bonds lost in dispute by stealing bonds of future claims

## Summary
Severity: High
Chain: Smart contract
Component: HATs-Arbitration-Contracts
Published: 2023-10-28
Source: https://github.com/hats-finance/HATs-Arbitration-Contracts-0x79a618f675857b45934ca1c413fd5f409cf89735/issues/37
Type: hats-finding

## Details
**Github username:** @bahurum
**Submission hash (on-chain):** 0x73d2cd9657a53d32a0afd8762b55b87e42a3ba04226fe1c7e6155fcda246d619
**Severity:** high

**Description:**
**Description**\
`HATArbitrator.reclaimBond()` refunds previously dismissed claim, but it shouldn't. This allows an attacker to make spam or malicious disputes, and then get those refunded using the bonds of successive claims, at the expense of the Expert committee or future disputers.

**Attack Scenario**
1. Claim A is submitted.
2. User 0 disputes Claim A by calling [`dispute()`](https://github.com/hats-finance/hats-contracts/blob/0d6ebbde912bc272d9b310140d434ee2aacd36d3/contracts/HATArbitrator.sol#L112). The `_bondAmount` he sends to `HATArbitrator` is stored in the `disputersBonds` mapping.
3. The Expert Committee dismisses the dispute over Claim A by calling [`dismissDispute()`](https://github.com/hats-finance/hats-contracts/blob/0d6ebbde912bc272d9b310140d434ee2aacd36d3/contracts/HATArbitrator.sol#L153). All tokens sent by disputers as bonds for Claim A are transferred to the Expert Committee.
4. A new Claim B is submitted for the same vault.
5. User 1 disputes Claim B by calling `dispute()`. The `_bondAmount` she sends to `HATArbitrator` is stored in the `disputersBonds` mapping
6. User 0 calls [`reclaimBond()`](https://github.com/hats-finance/hats-contracts/blob/0d6ebbde912bc272d9b310140d434ee2aacd36d3/contracts/HATArbitrator.sol#L268) to reclaim the bonds used previously to dispute Claim A. Note that this should fail.
   1. `bondClaimable[msg.sender][_vault][_claimId] == false` and the current claim is Claim B, so `claim.claimId != _claimId`.
   2. [`disputerBond`](https://github.com/hats-finance/hats-contracts/blob/0d6ebbde912bc272d9b310140d434ee2aacd36d3/contracts/HATArbitrator.sol#L286) is assigned the value previously stored in the `disputersBonds` mapping which is untouched. This amount of tokens is transferred to User 0.
7. The Expert committee dismisses the dispute over Claim B by calling `dismissDispute()` but this time:
   1. [`token.safeTransfer(msg.sender, totalBondsOnClaim[_vault][_claimId])`](https://github.com/hats-finance/hats-contracts/blob/0d6ebbde912bc272d9b310140d434ee2aacd36d3/contracts/HATArbitrator.sol#L164) will fail since a part of the bonds has been taken back by User 0 and now the balance of the `HATArbitrator` is insufficient.

**Recommendation**\
A way to fix this issue is to subtract the values reclaimed by the disputers from `totalBondsOnClaim[_vault][_claimId]`. This will make calls to `reclaimBond()` fail after `dismissDispute()` has been called for that a given claim.

```diff
function reclaimBond(IHATClaimsManager _vault, bytes32 _claimId) external {
    if (!bondClaimable[msg.sender][_vault][_claimId]) {
        // the bond is claimable if either
        // (a) it is not part of the curr

        IHATClaimsManager.Claim memory claim = _vault.getActiveClaim();

        if (
            claim.claimId == _claimId &&  // claim must be not active anymore and periods passed
            block.timestamp <
            claim.createdAt + claim.challengePeriod + claim.challengeTimeOutPeriod
        ) {
            revert CannotClaimBond();
        }
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/HATs-Arbitration-Contracts-0x79a618f675857b45934ca1c413fd5f409cf89735/issues/37_
