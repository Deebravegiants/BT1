# [M] OCL-1 | DoS Due To Crossed Markets

## Summary
Severity: Medium
Contest weight: 0.1032
Dataset id: 19221
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
GMX reverts when the bid price is greater than the ask price, otherwise known as a crossed market.
Crossed markets can typically happen in times of volatility, or when pricing is based on multiple
venues/data providers. For example, if the highest bid is from Coinbase but the lowest ask is from
Binance, the chance of a reported bid larger than the ask increases.
if (report.bid > report.ask) {
revert Errors.InvalidRealtimeBidAsk(token, report.bid, report.ask);
}
Internal feeds cannot be used to regain protocol functionality because internal feeds cannot be
enabled when a realtime feed is enabled for a particular token.

## Recommendation
Verify whether the realtime feeds report crossed markets, if so consider an alternative to the strict
validation or document and prepare for the risk of DoS.
