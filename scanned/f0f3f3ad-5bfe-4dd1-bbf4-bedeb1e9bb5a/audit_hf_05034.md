# [H] A malicious attacker can manipulate distribu-

## Summary
Severity: High
Contest weight: 0.3962
Dataset id: 23038
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the SuperBoring.onInFlowChanged function, userDataRaw contains the information of distributor. If a user sets this as address(1) that represents a pseudo distributor for totality stats, totality stats are updated incorrectly. As a result, member units of distributors are updated incorrectly and they get incorrect fee.
In the SuperBoring.onInFlowChanged function, userDataRaw contains the information of distributor. If user provide the info for distributor, userData.distributor will be an address of distributor provided by the user.
File: averagex-contracts-cloned\packages\evm-contracts\src\SuperBoring.sol
219: if (userDataRaw.length > 0) {
220: // This may revert, and it will make create/update flow fail.
221: userData = abi.decode(userDataRaw, (InFlowUserData));
222: if (trader == userData.referrer) revert NO_SELF_REFERRAL();
238: DistributionFeeDIP.updateDistributionStats(ITorex(msg.sender),
239: trader, userData.distributor,
240: prevFlowRate, newFlowRate);
Then, in the DistributionFeeDIP.updateDistributionStats function, it will update global distribution stats. If distributor is address(1), newStats and totalityStats will point the same storage variable from L69 if prevDistributor is not address(1).
File: averagex-contracts-cloned\packages\evm-contracts\src\BoringPrograms\DistributionFeeDIP.sol
62: address prevDistributor = $.distributors[torex][trader];
63: DistributionStats storage curStats = $.distributionStats[torex][prevDistributor];
64: DistributionStats storage totalityStats = $.distributionStats[torex][_PSEUDO_DISTRIBUTOR_FOR_TOTALITY_STATS];
65: if (prevDistributor == distributor) {
66: (curStats.particle, totalityStats.particle) = curStats.particle.shift_flow2b
67: (totalityStats.particle, FlowRate.wrap(newFlowRate - prevFlowRate), tnow);
68: } else {
69: DistributionStats storage newStats = $.distributionStats[torex][distributor];
70: (curStats.particle, totalityStats.particle) = curStats.particle.shift_flow2b
71: (totalityStats.particle, FlowRate.wrap(-prevFlowRate), tnow);
72: (newStats.particle, totalityStats.particle) = newStats.particle.shift_flow2b
73: (totalityStats.particle, FlowRate.wrap(newFlowRate), tnow);
74: }
Then, $.distributionStats[torex][_PSEUDO_DISTRIBUTOR_FOR_TOTALITY_STATS] that contains totality stats will be updated with incorrect value. If totality stats are updated with wrong value, the getTotalityStats function will return wrong value and the sync function will work incorrectly due to wrong information of totality stats from L85.
File: averagex-contracts-cloned\packages\evm-contracts\src\BoringPrograms\DistributionFeeManager.sol
85: (int256 dvol,) = p.getDistributorStats(torex, distributor);
86: (int256 tvol,) = p.getTotalityStats(torex);
87: if (tvol > 0) {
88: units = uint128(SafeCast.toUint256(dvol * INT_100PCT_PM / tvol));
89: }
90: }
91: pool.updateMemberUnits(distributor, units);
As a result, distributors will get wrong distribution fee.
Distributors will get wrong distribution fee. Furthermore, a malicious distributor can get all distribution fee by manipulating totality stats.

## Recommendation
In the DistributionFeeDIP.updateDistributionStats function, if distributor is address(1), it should be reverted.
File: averagex-contracts-cloned\packages\evm-contracts\src\BoringPrograms\DistributionFeeDIP.sol
57: function updateDistributionStats(ITorex torex, address trader, address distributor,
58: int96 prevFlowRate, int96 newFlowRate) internal {
+   require(distributor != _PSEUDO_DISTRIBUTOR_FOR_TOTALITY_STATS, 'Invalid Distributor');
59: Storage storage $ = _getStorage();
60: Time tnow = Time.wrap(uint32(block.timestamp));
