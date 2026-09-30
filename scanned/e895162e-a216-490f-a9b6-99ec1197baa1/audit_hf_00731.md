# [M] M-17 | Setting SkewScale Disrupts Markets

## Summary
Severity: Medium
Contest weight: 0.0701
Dataset id: 2282
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Setting the skewSkale with setMarketConfigurationById will cause unexpected results the next time recomputeFunding is called. The logic in recomputeFunding expects that the skew has not changed since the last time it was called which is respected in the current codebase.
However, it is also assumed that the skewScale has not been changed and therefore setting it in between will result in inaccurate funding numbers.

## Recommendation
Call recomputeFunding at the beginning of setMarketConfigurationById.
