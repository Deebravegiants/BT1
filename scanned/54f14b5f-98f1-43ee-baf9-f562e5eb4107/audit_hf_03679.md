# [M] VoltGNSPriceSource does not consider with-

## Summary
Severity: Medium
Contest weight: 0.0798
Dataset id: 19772
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
VoltGNS can have a withdraw fee that is taken when it is withdrawn. If this is the case then the value of VoltGNS should take this withdraw fee into consideration to properly value the collateral.
/VoltGNSPriceSource.sol#L23-L25
Here the exchange ratio of the vault and GNS price are used directly without considering the withdraw fee to remove the GNS from the vault.
Collateral will be valued incorrectly when there is a fee, leading to potentially bad loans

## Recommendation
Query the vault to see if there is a withdraw fee. If there is then remove the corresponding amount of value from the collateral price.
