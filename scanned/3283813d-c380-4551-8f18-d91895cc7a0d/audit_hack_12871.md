# [M] Vault: 24h ORACLE_FRESHNESS_THRESHOLD is too long for oracle price freshness check

## Summary
Severity: Medium
Reporter: n33k
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L55
Type: audit-issue

## Details
# Vault: 24h ORACLE_FRESHNESS_THRESHOLD is too long for oracle price freshness check

## Summary

In Vault.vy, latestRoundData() is called to query prices from chainlink. The price is freshness is checked, but the freshness threshold is set to 24h which is too large.

## Vulnerability Detail

latestRoundData() call and freshness check.

```python
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

`ORACLE_FRESHNESS_THRESHOLD` is hardcode code to 24h.

## Impact

A stale price could be used.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L55

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L580

## Tool used

Manual Review

## Recommendation

Set `ORACLE_FRESHNESS_THRESHOLD` to a smaller value such as 3 minutes.
