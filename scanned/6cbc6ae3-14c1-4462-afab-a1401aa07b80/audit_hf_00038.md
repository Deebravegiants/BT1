# [M] DIEMT-4 | Alpha Calculation Unused

## Summary
Severity: Medium
Contest weight: 0.1009
Dataset id: 114
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The expiry of an option cannot exceed the end of a queue epoch: //if option expiry bigger than the lp queue next epoch, dont allow creation if (_option.expiry > IIVXQueue(LP.queueContract()).nextEpochStartTimestamp()) { revert CannotCreateOptionWithExpiryAfterNextEpoch(); } Because of this coupling, the expiry of an option is currently limited to 1 day after creation time. This renders any alpha calculation and price blending mechanism useless, as the cutoff of 4 days is never reached. If the blending mechanism were to be used, depositors and withdrawers would have to wait 4 days before depositing/withdrawing funds from the LP.

## Recommendation
Consider adjusting the price blending formula and modify the epoch duration appropriately.
