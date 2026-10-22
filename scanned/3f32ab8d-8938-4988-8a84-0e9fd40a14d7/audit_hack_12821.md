# [M] Insufficient Oracle `Validation`

## Summary
Severity: Medium
Reporter: shealtielanz
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L243C1-L247C31
Type: audit-issue

## Details
# Insufficient Oracle `Validation`

## Summary
There is no `freshness` check on the timestamp of the prices fetched from the `Chainlink` oracle, so old prices may be used if [`OCR`](https://docs.chain.link/architecture-overview/off-chain-reporting) was unable to push an update in time. Add a `staleness threshold` number of the second's configuration parameter, and ensure that the price fetched is from within that `time range`.
## Vulnerability Detail
- In the `_get_latest_oracle_price` function in TrailingStopDex.vy 
```vyper
    answer: int256 = ChainlinkOracle(_oracle_address).latestRoundData()[1]
```

It doesn't check the time range or the roundness.
- In the `_get_price_at_round` function of TrailingStopDex.vy
```vyper
  answer: int256 = ChainlinkOracle(_oracle_address).getRoundData(_round_id)[1]
 updated_at: uint256 = ChainlinkOracle(_oracle_address).getRoundData(_round_id)[3]
```
It also doesn't check the time range or the roundness.
- In the `_to_usd_oracle_price` function in Vault.vy
```vyper
def _to_usd_oracle_price(_token: address) -> uint256:

    round_id: uint80 = 0
    answer: int256 = 0
    started_at: uint256 = 0
    updated_at: uint256 = 0
    answered_in_round: uint80 = 0
    round_id, answer, started_at, updated_at, answered_in_round = ChainlinkOracle(
        self.to_usd_oracle[_token]
    ).latestRoundData()

    assert (block.timestamp - updated_at) < ORACLE_FRESHNESS_THRESHOLD, "oracle not fresh"
```
Here it does a check for the time range but non for the answer, where the price could return zero.

## Impact

## Code Snippet
- The `_get_price_at_round` Function  ~ [Click here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L243C1-L247C31)
- The  `_get_latest_oracle_price` Function  ~ [Click here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L237C1-L240C17)
- The `_to_usd_oracle_price` Function ~ [Click here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L562C1-L583C21)
## Tool used

`Manual Review`

## Recommendation
Check for the `timestamp` and also for `roundness`.
