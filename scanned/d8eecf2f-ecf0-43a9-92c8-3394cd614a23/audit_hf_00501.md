# [M] M-04 | Rightful Disputer Might Lose Bonds

## Summary
Severity: Medium
Contest weight: 0.0850
Dataset id: 1959
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, there is no mechanism that checks whether there is already an ongoing dispute or not while submitting a price. Asserter can submit a new price after an initial incorrect submission without waiting a dispute to resolve in 48-96 hours. This would cause disputer to lose their bonds since the settlement will fail at [this line](https://github.com/GuardianAudits/foil-1/blob/50373325e4ad7bb98382b5b4adce241a1ac1e770/packages/protocol/src/market/modules/UMASettlementModule.sol#L156) as the assertionIds won't match.

## Recommendation
Do not allow submitting new price if there is already an ongoing dispute.
