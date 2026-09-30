# [M] M-4 Insufficient quality of the _collateralERC20 check in BAMM

## Summary
Severity: Medium
Contest weight: 0.0533
Dataset id: 16000
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is possible to provide the wrong address in the _collateralERC20 parameter's value to the BAMM constructor:  
• value that is different from StabilityPool,  
• value that is not an ERC20 token,  
• address of a token with the wrong decimals value (not 18)

## Recommendation
We recommend adding a check of the _collateralAddress address parameter or removing this parameter from the constructor and getting it from the StabilityPool contract.  
2.4 Low
