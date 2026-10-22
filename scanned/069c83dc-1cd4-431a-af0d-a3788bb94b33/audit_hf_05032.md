# [H] DistributionFeeDIP does not update previous

## Summary
Severity: High
Contest weight: 0.7855
Dataset id: 23036
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DistributionFeeDIP does not update previous distributor address.
When a user updates a Torex flow and sets a userData.distributor, the distributor would receives some inTokens as fees. The stats for distributors are stored in DistributionFeeDIP and updated using updateDistributionStats(). These fees are later claimed in DistributionFeeManager.
The issue is that inside updateDistributionStats(), the code does NOT update the current distributor for the trader. This means the old distributor is always address(0), and the new distributor's flowRate increases with each flow update.
For example:
1. User A creates a flowRate of 10 with distributor B. Distributor B now has a flowRate of 10, distributor address(0) has a flowRate of -10.
2. User A updates the flowRate to 20. Distributor B now has a flowRate of 30, distributor address(0) has a flowRate of -30.
This causes the entire distribution stats to be inaccurate.
```solidity
DistributionFeeDIP.sol
function updateDistributionStats(ITorex torex, address trader, address distributor,
int96 prevFlowRate, int96 newFlowRate) internal
{
    Storage storage $ = _getStorage();
    Time tnow = Time.wrap(uint32(block.timestamp));
    address prevDistributor = $.distributors[torex][trader];
    DistributionStats storage curStats = $.distributionStats[torex][prevDistributor];

    DistributionStats storage totalityStats = $.distributionStats[torex][_PSEUDO_DISTRIBUTOR_FOR_TOTALITY_STATS];

    if (prevDistributor == distributor) {
        (curStats.particle, totalityStats.particle) = curStats.particle.shift_flow2b
        (totalityStats.particle, FlowRate.wrap(newFlowRate - prevFlowRate), tnow);
    } else {
        DistributionStats storage newStats = $.distributionStats[torex][distributor];

        (curStats.particle, totalityStats.particle) = curStats.particle.shift_flow2b
        (totalityStats.particle, FlowRate.wrap(-prevFlowRate), tnow);
        (newStats.particle, totalityStats.particle) = newStats.particle.shift_flow2b
        (totalityStats.particle, FlowRate.wrap(newFlowRate), tnow);
    }
    // @bug: $.distributors[torex][trader] is not updated.
    emit DistributorUpdated(torex, trader, distributor, prevDistributor);
}
```
```solidity
SuperBoring.sol
function onInFlowChanged(address trader,
int96 prevFlowRate, int96 /*preFeeFlowRate*/, uint256 /*last Updated*/,
int96 newFlowRate, uint256 /*now*/,
bytes calldata userDataRaw) external override
onlyRegisteredTorex(msg.sender)
returns (int96 newFeeFlowRate)
{
    ...
    DistributionFeeDIP.updateDistributionStats(ITorex(msg.sender),
    trader, userData.distributor,
    prevFlowRate, newFlowRate);
    ...
}
```
The distributionStats accounting would be completely incorrect, and anyone can increase distributor's flowRate to a large value. Also, the flowRate for address(0) could underflow if it reaches -int128.max, which would DoS the entire protocol.

## Recommendation
Add $.distributors[torex][trader] = distributor in updateDistributionStats.
