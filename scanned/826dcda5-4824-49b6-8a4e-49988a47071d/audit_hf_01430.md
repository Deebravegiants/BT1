# [M] rebaseMul() not working as intended

## Summary
Severity: Medium
Contest weight: 0.0770
Dataset id: 7433
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function rebaseMul() increases the balance per share value by a factor. The issue is that the code only accepts integer factors and it will not be possible to increase the balance per share by small percentages.
function rebaseMul(uint128 factor) external onlyRole(OPERATOR_ROLE) {
uint128 _balancePerShare = balancePerShare() * factor;
UsdPlusStorage storage $ = _getUsdPlusStorage();
$._balancePerShare = _balancePerShare;
emit BalancePerShareSet(_balancePerShare);
}

## Recommendation
Use the denominator and nominator to specify the increase factor.
