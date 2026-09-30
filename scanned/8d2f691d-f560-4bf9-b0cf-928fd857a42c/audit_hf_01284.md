# [M] AccessHub missing functionality

## Summary
Severity: Medium
Contest weight: 0.1681
Dataset id: 6052
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the current codebase, many functions are decorated with the onlyGovernance modifier, indicating they are intended to be called by the AccessHub contract. However, the AccessHub contract does not implement the necessary external calls to invoke these functions. To address this, the following functions should have corresponding implementations within the AccessHub contract:
1. Voter.createArbitraryGauge.
2. Voter.setMainTickSpacing.
3. Voter.stuckEmissionsRecovery.
4. LauncherPlugin.label.
5. XShadow.migrateOperator.
6. XShadow.rescueTrappedTokens.
7. XShadow.operatorRedeem.
8. XShadow.unpause.
9. XShadow.pause.
10. PairFactory.setSkimEnabled.
11. PairFactory.setFeeSplit.
12. PairFactory.setFeeSplitWhenNoGauge.
13. PairFactory.setTreasury.
14. PairFactory.setFee.
15. RamsesV3Factory.setFeeProtocol.
16. RamsesV3Factory.setFeeCollector.
17. x33.transferOperator.

## Recommendation
In the current codebase, many functions are decorated with the onlyGovernance modifier, indicating they are intended to be called by the AccessHub contract. However, the AccessHub contract does not implement the necessary external calls to invoke these functions. To address this, the following functions should have corresponding implementations within the AccessHub contract:
1. Voter.createArbitraryGauge.
2. Voter.setMainTickSpacing.
3. Voter.stuckEmissionsRecovery.
4. LauncherPlugin.label.
5. XShadow.migrateOperator.
6. XShadow.rescueTrappedTokens.
7. XShadow.operatorRedeem.
8. XShadow.unpause.
9. XShadow.pause.
10. PairFactory.setSkimEnabled.
11. PairFactory.setFeeSplit.
12. PairFactory.setFeeSplitWhenNoGauge.
13. PairFactory.setTreasury.
14. PairFactory.setFee.
15. RamsesV3Factory.setFeeProtocol.
16. RamsesV3Factory.setFeeCollector.
17. x33.transferOperator.
