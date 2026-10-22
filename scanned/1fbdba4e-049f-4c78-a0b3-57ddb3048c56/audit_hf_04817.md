# [M] distributeYield() calls earningsTrancheuse()

## Summary
Severity: Medium
Contest weight: 0.6963
Dataset id: 22687
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The distributeYield() function internally calls earningsTrancheuse() on L232 which calculates & returns the _seniorTranche & _juniorTranche yield distribution. However, this call results in earningsTrancheuse() using outdated values of emaSTT & emaJTT on L461-L462 as these variables are updated only on L238-L239 after the call to earningsTrancheuse() is concluded.
File: src/ZivoeYDL.sol
```solidity
213: function distributeYield() external nonReentrant {
214:     require(unlocked, "ZivoeYDL::distributeYield() !unlocked");
215:     require(
216:         block.timestamp >= lastDistribution + daysBetweenDistributions * 86400,
217:         "ZivoeYDL::distributeYield() block.timestamp < lastDistribution + daysBetweenDistributions * 86400"
218:     );
219: 
220:     // Calculate protocol earnings.
221:     uint256 earnings = IERC20(distributedAsset).balanceOf(address(this));
222:     uint256 protocolEarnings = protocolEarningsRateBIPS * earnings / BIPS;
223:     uint256 postFeeYield = earnings.floorSub(protocolEarnings);
224: 
225:     // Update timeline.
226:     distributionCounter += 1;
227:     lastDistribution = block.timestamp;
228: 
229:     // Calculate yield distribution (trancheuse = "slicer" in French).
230:     (
231:         uint256[] memory _protocol, uint256 _seniorTranche, uint256 _juniorTranche, uint256[] memory _residual
232:     ) = earningsTrancheuse(protocolEarnings, postFeeYield);
233: 
234:     emit YieldDistributed(_protocol, _seniorTranche, _juniorTranche, _residual);
235: 
236:     // Update ema-based supply values.
237:     (uint256 aSTT, uint256 aJTT) = IZivoeGlobals_YDL(GBL).adjustedSupplies();
238:     emaSTT = MATH.ema(emaSTT, aSTT, retrospectiveDistributions.min(distributionCounter));
239:     emaJTT = MATH.ema(emaJTT, aJTT, retrospectiveDistributions.min(distributionCounter));
...
```
and
File: src/ZivoeYDL.sol
```solidity
447: function earningsTrancheuse(uint256 yP, uint256 yD) public view returns (
448:     uint256[] memory protocol, uint256 senior, uint256 junior, uint256[] memory residual
449: ) {
450:     protocol = new uint256[](protocolRecipients.recipients.length);
451:     residual = new uint256[](residualRecipients.recipients.length);
452: 
453:     // Accounting for protocol earnings.
454:     for (uint256 i = 0; i < protocolRecipients.recipients.length; i++) {
455:         protocol[i] = protocolRecipients.proportion[i] * yP / BIPS;
456:     }
457: 
458:     // Accounting for senior and junior earnings.
459:     uint256 _seniorProportion = MATH.seniorProportion(
460:         IZivoeGlobals_YDL(GBL).standardize(yD, distributedAsset),
461:         MATH.yieldTarget(emaSTT, emaJTT, targetAPYBIPS, targetRatioBIPS, daysBetweenDistributions),
462:         emaSTT, emaJTT, targetAPYBIPS, targetRatioBIPS, daysBetweenDistributions
463:     );
464:     senior = (yD * _seniorProportion) / RAY;
465:     junior = (yD * MATH.juniorProportion(emaSTT, emaJTT, _seniorProportion, targetRatioBIPS)) / RAY;
466: 
467:     // Handle accounting for residual earnings.
468:     yD = yD.floorSub(senior + junior);
469:     for (uint256 i = 0; i < residualRecipients.recipients.length; i++) {
470:         residual[i] = residualRecipients.proportion[i] * yD / BIPS;
471:     }
472: }
```
As the docs explain, the EMA plays a significant role in yield distribution calculations. Returns are calculated using the adjusted supply of tranche tokens, with an Exponential Moving Average (EMA) playing a significant role. The EMA smoothens the change in the supply of tranche tokens over a look-back period of 2.5 months. The EMA is used to calculate the: • yield target via a call to MATH.yieldTarget() which expects "ema-based supply of zSTT & zJTT" as its params. • senior tranche yield proportion via a call to MATH.seniorProportion() which again expects ema-based yT, eSTT & eJTT. Both the above mentioned calls happen inside earningsTrancheuse() here. The issue is that these global variables emaSTT and emaJTT are still outdated and correspond to the ones belonging to the lastDistribution timestamp instead of current updated ones. These values are updated only after the call to earningsTrancheuse() has concluded here. Imagine that in the last 30 days, JTT supply has reduced due to defaulted loans. As a result, the target yield yTreal would come down too (i.e. yTreal < yT where yT is the protocol calculated incorrect target yield) and the junior tranche ditributable yield will be smaller than before. However if there is excess yield, then the junior tranche would receive more than their fair share since last 30 days have not been considered by the protocol calculations. If the quantum of defaulted loans is high (and hence yTreal has dipped significantly), the impact is not only limited to the junior tranche, but then also effects the senior tranche. On the flip side an increase in the adjusted supplies of STT and JTT in the last 30 days will have a impact on the smoothened emaSTT and emaJTT, making the values go higher. As a result, target yield yTreal would go up too. Thus, it could happen that yD is less than yTreal but the protocol is oblivious to that due to usage of outdated values. This would result in the protcol using seniorProportionBase() to calculate the senior's yield instead of seniorProportionShortfall(). Finally, since at each of these function calls an outdated eSTT is passed as a param, the value returned would be more/less than what it should be, thus causing gain/loss of yield for both the tranches (juniorProportion() calculation has the same problem). used are from 60 days ago instead of 30 days as can be seen inside unlock(), further increasing the margin of error. The 60 day gap has initially been provided by the protocol to allow for more time to bring in initial yield.

## Recommendation
Update the ema values before calling earningsTrancheuse():
```solidity
// Update ema-based supply values.
(uint256 aSTT, uint256 aJTT) = IZivoeGlobals_YDL(GBL).adjustedSupplies();
emaSTT = MATH.ema(emaSTT, aSTT, retrospectiveDistributions.min(distributionCounter));
emaJTT = MATH.ema(emaJTT, aJTT, retrospectiveDistributions.min(distributionCounter));
// Calculate yield distribution (trancheuse = "slicer" in French).
(
    uint256[] memory _protocol, uint256 _seniorTranche, uint256 _juniorTranche, uint256[] memory _residual
) = earningsTrancheuse(protocolEarnings, postFeeYield);
emit YieldDistributed(_protocol, _seniorTranche, _juniorTranche, _residual);
```
