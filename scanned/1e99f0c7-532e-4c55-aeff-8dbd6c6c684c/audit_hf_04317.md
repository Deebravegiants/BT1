# [M] M-02 | Floor Reserves Decrease After Sweep

## Summary
Severity: Medium
Contest weight: 0.1124
Dataset id: 21468
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the sweep function the liquidity for the anchor position is maintained, however the anchor position moves higher. Therefore more reserves will be required to maintain the same liquidity for the anchor position.
Therefore if there is not enough profit from the discovery position to overshadow this discrepancy, reserves will be taken from the floor to sustain the anchor liquidity while moving the anchor up.
This may be unexpected as it can unnecessarily reduce capacity by moving reserves up from the floor position to the anchor.

## Recommendation
Consider implementing the sweep function such that it maintains the reserves of the anchor position rather than the liquidity of the anchor position with the implementation listed below.
However if using this implementation be aware that this has a trade off, where the liquidity of the anchor position can now reduce upon sweeping, though by a trivial amount.
It may ultimately be fine to acknowledge this issue and keep the existing implementation as a scenario which causes more than a 10,000 wei liquidity difference has not been identified.
