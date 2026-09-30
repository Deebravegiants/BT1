# [M] Arcadia Finance incident: Arcadia Finance has been attacked on Ethereum and Optimism, with total profits of $400K. The root cause is that in function vaultM

## Summary
Severity: Medium
Target: Arcadia Finance
Loss: $ 455,000
Attack method: Contract Vulnerability
Published: 2023-07-10
Source: https://twitter.com/Phalcon_xyz/status/1678270672911605760
Type: slowmist-incident

## Details
Arcadia Finance has been attacked on Ethereum and Optimism, with total profits of $400K. The root cause is that in function vaultManagementAction, the attacker can first transfer all the asset to his own controlled contract and re-entry the function liquidateVault to liquidiate the vault. In this case, the global variable "isTrustedCreditorSet" will be set as false and the Collateral check can be bypassed.
