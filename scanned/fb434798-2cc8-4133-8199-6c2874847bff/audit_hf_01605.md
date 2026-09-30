# [M] TRS-2 | Centralization Risk

## Summary
Severity: Medium
Contest weight: 0.0868
Dataset id: 8631
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The operator address is not a multi-sig and has potentially dangerous permissions for hamsterWheelSetOperator, hamsterWheelAllocateSeigniorage, hamsterWheelSetLockUp, setBondDepletionFloorPercent, setBootstrap, setDiscountPercent, setExtraFunds, setHamsterOracle, setHamsterPriceCeiling, setHamsterWheel, setMaxDebtRatioPercent, setMaxExpansionTiersEntry, setMaxPremiumRate, setMaxSupplyContractionPercent, setMaxSupplyExpansionPercents, setMintingFactorForPayingDebt, setPremiumPercent, setPremiumThreshold, setSupplyTiersEntry

## Recommendation
Make the operator a multi-sig and/or introduce a timelock for the community to monitor events.
