# [M] Some ERC20 can revert on a zero value transfer

## Summary
Severity: Medium
Contest weight: 0.2061
Dataset id: 20994
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Note: This finding was reported via the winning [Automated Findings report](https://github.com/code-423n4/2024-03-revert-lend/blob/main/bot-report.md). It was declared out of scope for the audit, but is being included here for completeness.

[728](https://github.com/code-423n4/2024-03-revert-lend/blob/ac520c5fedf4e1654c597a46efaf5a7c27295de1/src/V3Vault.sol#L728), [946](https://github.com/code-423n4/2024-03-revert-lend/blob/ac520c5fedf4e1654c597a46efaf5a7c27295de1/src/V3Vault.sol#L946), [226](https://github.com/code-423n4/2024-03-revert-lend/blob/ac520c5fedf4e1654c597a46efaf5a7c27295de1/src/automators/Automator.sol#L226), [272](https://github.com/code-423n4/2024-03-revert-lend/blob/ac520c5fedf4e1654c597a46efaf5a7c27295de1/src/transformers/AutoCompound.sol#L272), [88](https://github.com/code-423n4/2024-03-revert-lend/blob/ac520c5fedf4e1654c597a46efaf5a7c27295de1/src/transformers/LeverageTransformer.sol#L88), [91](https://github.com/code-423n4/2024-03-revert-lend/blob/ac520c5fedf4e1654c597a46efaf5a7c27295de1/src/transformers/LeverageTransformer.sol#L91), [872](https://github.com/code-423n4/2024-03-revert-lend/blob/ac520c5fedf4e1654c597a46efaf5a7c27295de1/src/transformers/V3Utils.sol#L872), [85](https://github.com/code-423n4/2024-03-revert-lend/blob/ac520c5fedf4e1654c597a46efaf5a7c27295de1/src/utils/FlashloanLiquidator.sol#L85), [98](https://github.com/code-423n4/2024-03-revert-lend/blob/ac520c5fedf4e1654c597a46efaf5a7c27295de1/src/utils/Swapper.sol#L98), [167](https://github.com/code-423n4/2024-03-revert-lend/blob/ac520c5fedf4e1654c597a46efaf5a7c27295de1/src/utils/Swapper.sol#L167)

## Recommendation
No recommendation
