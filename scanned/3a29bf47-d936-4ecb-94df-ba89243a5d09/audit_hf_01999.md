# [C] C-1 Rewards can be accounted as collateral

## Summary
Severity: Critical
Contest weight: 0.1510
Dataset id: 11268
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the sum of the execution layer and consensus layer rewards reaches 32 ether, the rewards will be accounted as collateral, and the service will not collect some fees ContractWcFeeDistributor.sol#L114-L135. The main problem here is that there is no check that collateralsCountToReturn <= (svalidatorData.exitedCount - svalidatorData.collateralReturnedCount). A malicious client can always front-run the withdraw() call and transfer additional eth to the contract, so EL + CL rewards always will be divisible by 32 eth.

## Recommendation
We recommend adding the following check:
collateralsCountToReturn <= (s_validatorData.exitedCount - s_validatorData.collateralReturnedCount).
