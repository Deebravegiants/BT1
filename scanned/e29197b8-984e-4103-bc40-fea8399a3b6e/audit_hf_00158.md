# [M] `.latestRoundData`

## Summary
Severity: Medium
Contest weight: 0.1361
Dataset id: 801
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The method `.latestRoundData()` on an oracle returns the latest updated price from the oracle, but this is not the current price of an asset. To get an accurate current price you need to query it by calling the oracle and waiting for a callback to fulfill the request.

Inaccurate price data could quickly lead to a large loss of funds. Suppose the price of an asset changes downward 5% but your oracle is not updated. A user could deposit funds (credited with an extra 5% since the oracle isn’t updated), wait until `.latestRoundData()` updates (or update it himself) and becomes accurate. He then withdraws to the same asset he put in for an extra 5%. [`ExchangeRate.sol` L84](https://github.com/code-423n4/2021-08-notional/blob/4b51b0de2b448e4d36809781c097c7bc373312e9/contracts/internal/valuation/ExchangeRate.sol#L84)

Recommend not fetching the latest price (having to call the oracle to update the price instead), and then waiting for the callback.

## Recommendation
No recommendation
