# [M] An inactive KNOT can successfully stake

## Summary
Severity: Medium
Contest weight: 0.1347
Dataset id: 17969
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An inactive KNOT can successfully stake.

Expected behaviour of the system: The stake function should revert if an inactive KNOT is trying to stake.

Actual behaviour of the system: The stake function succeeds and the inactive KNOT stakes.

Property Violated: `cannotStakeIfKnotIsInActive`

In this rule, the `isActive` state of the `blsPubKey` is set to `false`. The stake function is then called with this `blsPubKey` and the expected behaviour is that the function would revert because the KNOT is inactive. However, the stake function succeeds and an inactive KNOT can therefore successfully stake. The stake function checks if KNOT is not registered (`!isKNOTRegistered`) and if it is no longer part of the syndicate (`!isNoLongerPartOfSyndicate`) and reverts accordingly but does not check whether the KNOT is inactive.

Lines of code: <https://github.com/Certora/2023-01-blockswap-fv/blob/certora/contracts/syndicate/Syndicate.sol#L216>

## Recommendation
No recommendation
