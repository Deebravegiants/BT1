# [M] M-03 | Possible DOS In _getTotalOpenDisputes

## Summary
Severity: Medium
Contest weight: 0.1157
Dataset id: 2295
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _getTotalOpenDisputes function is used by the addOracleCouncilMember and
removeOracleCouncilMember functions in the OracleCouncil contract.
This function calculates the total open disputes by looping through all active markets and checking
if each market is in the DisputeRaised status and has any open disputes. The issue is that
_activeMarkets does not have a cap, meaning it could grow indefinitely.
As a result, the gas costs for calling _getTotalOpenDisputes can become excessively high,
potentially exceeding the block gas limit and causing the transaction to fail.
This could effectively lock the addOracleCouncilMember and removeOracleCouncilMember
functions, preventing them from being executed.

## Recommendation
Introduce a cap on the size of _activeMarkets or consider optimizing the function to avoid iterating
through markets that are in a finalized state, as they cannot return to the disputed state.
