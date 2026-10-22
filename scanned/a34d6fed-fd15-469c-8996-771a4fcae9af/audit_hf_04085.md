# [H] GMXL-1 | Withdrawals Apply _minOutputAmount To One Side

## Summary
Severity: High
Contest weight: 0.2715
Dataset id: 20539
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the executeInitiateUnwrapping function the withdrawalParams are created with a
_minOutputAmount that can only apply to either the shortToken output or the longToken output.
However withdrawals in GMX remove a split of the shortToken and longToken. The resulting
shortToken and longToken are then subjected to the longTokenSwapPath and shortTokenSwapPath,
the outputs of which are validated against the minLongTokenAmount and minShortTokenAmount
respectively.
Therefore even though the outputs are swapped to the same token, take for example the short token,
the short token that is directly removed from GMX will be validated against the entire
_minOutputAmount and the short token that is received from the portion that was removed as the
longToken and swapped to the shortToken will be validated against a minShortTokenAmount of 0.
This results in the withdrawal likely failing the minimum output validation as the portion of short
token that is directly removed from GMX is unlikely to solely pass the _minOutputAmount validation.
Additionally, there can be no minimum output that applies to the portion of funds that are swapped
which is exactly the portion that ought to be validated.

## Recommendation
Refactor the _minOutputAmount logic such that the minimum output can be split amongst the
minLongTokenAmount and minShortTokenAmount.
