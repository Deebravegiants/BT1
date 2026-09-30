# [M] BalancedVault may unable to rebalance when makerLimit was decreased

## Summary
Severity: Medium
Contest weight: 0.1042
Dataset id: 19696
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In _adjustPosition(), it is expected that makerLimit will always be greater than currentMaker. That should be the case in normal circumstances. However, the makerLimit can be changed by the productOwner at anytime. When the makerLimit is changed to a lower value, _adjustPosition will revert at L298 due to underflow.
https://github.com/equilibria-xyz/perennial-mono/blob/3d2c5f16fb4f65f25ecf1f2cb2a5f89448415beb/packages/perennial-vaults/contracts/BalancedVault.sol#L291-L299
The makerLimit can be changed by the productOwner at anytime:
https://github.com/equilibria-xyz/perennial-mono/blob/3d2c5f16fb4f65f25ecf1f2cb2a5f89448415beb/packages/perennial/contracts/product/UParamProvider.sol#L236-L23

## Recommendation
No recommendation available
