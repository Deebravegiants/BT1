# [M] Business Logic Error in unpauseSatellitePool()

## Summary
Severity: Medium
Contest weight: 0.4573
Dataset id: 11759
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As a contingency plan, the dev team and trustees could pause the BoringDAO system when there is an emergency through the pause() function in the Liquidation contract. Typically, pausing the whole system comes with paused Satellite pools. If there are more than 2/3 trustees reach an agreement with each others, the unpauseSatellitePool() could be used to unpause a paused Satellite pool. Specifically, as shown in the following code snippet, line 101 increments the unpausePoolConfirmCount[pool] whenever a trustee invokes unpauseSatellitePool(). Later on, in line 104, the pool is paused when the unpausePoolConfirmCount[pool] reaches the threshold.
```solidity
function unpauseSatellitePool(address pool)
    public
    onlyTrustee
{
    require(systemPause == true, "Liquidation::unpauseSatellitePool: systemPause should paused when call unpause()");
    require(isSatellitePool[pool] == true, "Liquidation::unpauseSatellitePool:Not SatellitePool");
    if (unpauseConfirm[msg.sender][pool] == false)
        unpauseConfirm[msg.sender][pool] == true;
    unpausePoolConfirmCount[pool] = unpausePoolConfirmCount[pool].add(1);
    uint trusteeCount = IHasRole(addressReso.requireAndKey2Address(BORING_DAO, "Liquidation::withdraw: boringDAO contract not exist")).getRoleMemberCount(TRUSTEE_ROLE);
    uint threshold = trusteeCount.mod(3) == 0 ? trusteeCount.mul(2).div(3) : trusteeCount.mul(2).div(3).add(1);
    if (unpausePoolConfirmCount[pool] >= threshold)
        IPause(pool).unpause();
}
```
However, the current implementation fails to check if the trustee has called unpauseSatellitePool() with the specific pool already. Since line 101 increments the count without checking unpauseConfirm[msg.sender][pool], a malicious trustee could call unpauseSatellitePool() multiple times to unpause any pool. In addition, line 99 has a typo (i.e., a duplicate =) such that unpauseConfirm[msg.sender][pool] would never be set to true.

## Recommendation
Increment unpausePoolConfirmCount[pool] only if unpauseConfirm[msg.sender][pool] is false. In addition, fix the typo in line 99.
