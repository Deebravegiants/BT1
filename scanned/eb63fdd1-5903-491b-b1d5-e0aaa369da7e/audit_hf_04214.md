# [C] C-03 | reportedDebt Incorrectly Calculates Funding

## Summary
Severity: Critical
Contest weight: 0.2244
Dataset id: 21108
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The reportedDebt function aims to report the net funding fees which have yet to be paid to or from
traders, among other things.
Following from the documentation in PerpMarket.sol:
/// debtCorrection = positions.sum(p.collateralUsd - p.size * (p.entryPrice + p.entryFunding))
/// marketDebt = market.skew * (price + nextFundingEntry) + debtCorrection
reportedDebt aims to compute the outstanding funding amount via market.skew * nextFundingEntry
- positions.sum(p.size * p.entryFunding)
However in the implementation of the reportedDebt function, the unrecordedFunding is used as the
nextFundingEntry in the equation above. Instead the currentFundingAccruedComputed +
unrecordedFunding ought to be used as the nextFundingEntry. This clearly invalidates the
computation of the outstanding funding amount as often the individual p.entryFunding values will be
larger than the unrecordedFunding portion.

## Recommendation
Use currentFundingAccruedComputed + unrecordedFunding instead of just unrecordedFunding
when computing the outstanding funding fees of the market.
