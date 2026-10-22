# [M] M-7 Callback verification

## Summary
Severity: Medium
Contest weight: 0.0576
Dataset id: 9535
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
By mistake a callback which has no implementation of the processLidoOracleReport() method can be added at the line: OrderedCallbacksArray.sol#L60 in case you set the IBeaconReportReceiver address, the execution of the following lines will be reverted. LidoOracle.sol#L644

## Recommendation
It is necessary to add verification of the existing processLidoOracleReport() method in callback or callbacks should be double-checked before adding. See this standard: https://eips.ethereum.org/EIPS/eip-165.
2.4 Low
