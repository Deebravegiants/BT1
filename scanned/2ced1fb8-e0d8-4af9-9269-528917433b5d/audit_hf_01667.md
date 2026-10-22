# [M] IDOPoolAbstract::withdrawSpareIDO() does not take into account that several rounds may use the same IdoToken

## Summary
Severity: Medium
Contest weight: 0.0512
Dataset id: 9018
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
IDOPoolAbstract::withdrawSpareIDO() checks if contractBal >= ido.idoSize, where contractBal = IERC20(ido.idoToken).balanceOf(address(this)). When several rounds use the same ido.idoToken, this check is incomplete as ido.idoSize only tracks the tokens of one round.

## Recommendation
The correct check is withdrawing contractBal - globalTokenAllocPerIDORound[idoConfig.idoToken], correctly tracking excess tokens.
