# [M] Updating stake or updating flow may DoS if

## Summary
Severity: Medium
Contest weight: 0.4612
Dataset id: 23040
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Updating stake or updating flow may DoS if Torex doesn't enable QuadraticEmission in the beginning.
First, we need to understand that it's entirely possible for a Torex to be created and operate for a while before the admin enables QuadraticEmission (QE) for it. This is because Torex is created in a permissionless way - anyone can call SuperBoring.createUniV3PoolTwapObserverAndTorex to create it. The admin needs to explicitly call SuperBoring.govQEEnableForTorex to enable QE.
Now, let's see how enabling QE while the Torex has been active for a while could result in a DoS.
If a user updates their stake or flow, QuadraticEmissionTIP.onStakeUpdated and QuadraticEmissionTIP.onInFlowChanged are called. However, if QE is not enabled, these functions simply skip execution due to isQEEnabledForTorex(torex) being false. If QE is later enabled, performing operations like q0 + Math.sqrt(newStakedAmount) - Math.sqrt(oldStakedAmount); or emissionPool.getUnits(trader) + newTraderUnits - prevTraderUnits could revert due to underflow if the previous stake amount or traderUnits (flowRate) is larger than the new one.
An example is:
1. Torex is created, but QE is not enabled.
2. A user creates a flowRate of 100 units in QE.
3. QE is then enabled.
4. The user tries to reduce the flowRate to 50 units, but emissionPool.getUnits(trader) + newTraderUnits - prevTraderUnits reverts because it evaluates to 0 + 50 - 100.
This situation arises because QuadraticEmissionTIP incorrectly uses trader's units or stake amount when QE was not enabled, leading to incorrect calculations and potential underflows when QE is later enabled.
```solidity
function onStakeUpdated(EmissionTreasury emissionTreasury, ITorex torex, uint256 oldStakedAmount, uint256 newStakedAmount)
internal
{
    if (isQEEnabledForTorex(torex)) {
        Storage storage $ = _getStorage();
        uint256 q0 = EnumerableMap.get($.torexQs, address(torex));
        uint256 q1 = q0 + Math.sqrt(newStakedAmount) - Math.sqrt(oldStakedAmount);
        $.qqSum = $.qqSum + q1 * q1 - q0 * q0;
        EnumerableMap.set($.torexQs, address(torex), q1);
        adjustEmission(emissionTreasury, torex);
    }
}
// @dev This hook updates flow updater's emission share.
function onInFlowChanged(EmissionTreasury emissionTreasury, ITorex torex, address trader, address referrer,
int96 prevFlowRate, int96 newFlowRate) internal
{
    assert(trader != referrer); // please provide a nicer revert in the use-site
    if (isQEEnabledForTorex(torex)) {
        Storage storage $ = _getStorage();
        ISuperfluidPool emissionPool = emissionTreasury.getEmissionPool(address(torex));
        // update trader's reward to store prevTraderUnits.
        uint128 newTraderUnits = scaleInTokenFlowRateToBoringPoolUnits(torex, newFlowRate);
        {
            uint128 prevTraderUnits = scaleInTokenFlowRateToBoringPoolUnits(torex, prevFlowRate);
            emissionTreasury.updateMemberEmissionUnits(address(torex), trader,
            emissionPool.getUnits(trader) + newTraderUnits - prevTraderUnits);
        }
        ...
    }
}
```
Updating stake or updating flow may DoS.

## Recommendation
Maintain the user's flowRate and stakedAmount within QuadraticEmissionTIP and only update it after QE is enabled, and don't rely on passed in previous values.
