# [M] Vault.vy: Potential Risk of Stale Data from Oracle due to Extended Freshness Threshold

## Summary
Severity: Medium
Reporter: pengun
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L55
Type: audit-issue

## Details
# Vault.vy: Potential Risk of Stale Data from Oracle due to Extended Freshness Threshold

## Summary
A potential issue in the smart contract code could result in receiving stale price data from the oracle. The `ORACLE_FRESHNESS_THRESHOLD` has been set to 24 hours, allowing outdated data to be accepted.

## Vulnerability Detail
The smart contract uses `ORACLE_FRESHNESS_THRESHOLD` to ensure it receives fresh data from the oracle. However, the threshold has been set to 24 hours, which is a considerable duration in the context of rapidly changing market conditions. Consequently, there's a risk of the contract operating based on stale price data.

```solidity
round_id: uint80 = 0
answer: int256 = 0
started_at: uint256 = 0
updated_at: uint256 = 0
answered_in_round: uint80 = 0
round_id, answer, started_at, updated_at, answered_in_round = ChainlinkOracle(
    self.to_usd_oracle[_token]
).latestRoundData()

assert (block.timestamp - updated_at) < ORACLE_FRESHNESS_THRESHOLD, "oracle not fresh"

usd_price: uint256 = convert(answer, uint256)  # 8 dec
```
## Impact
The impact of this issue is the potential for the contract to perform calculations based on outdated market price data, which could result in mispriced transactions or incorrect contract state.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L55
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L562-L583

## Tool used

Manual Review

## Recommendation
It is recommended to adjust the `ORACLE_FRESHNESS_THRESHOLD` to a more appropriate value that suits the volatility and liquidity of the asset in question, ensuring more up-to-date price information is used in contract operations.
