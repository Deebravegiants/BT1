# [M] Oracle freshness check is not constraint enough

## Summary
Severity: Medium
Reporter: twicek
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L580
Type: audit-issue

## Details
# Oracle freshness check is not constraint enough

## Summary
`ORACLE_FRESHNESS_THRESHOLD` is not contraint enough, which could lead to a stale price for almost a day.

## Vulnerability Detail
`ORACLE_FRESHNESS_THRESHOLD` is set to 24 hours while most oracle heartbeat is 1h. For these oracles, the price risk to be stale for 23 hours before being flagged as stale.

[Vault.vy#L580](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L580)
```solidity
    assert (block.timestamp - updated_at) < ORACLE_FRESHNESS_THRESHOLD, "oracle not fresh"
```

## Impact
Oracle freshness check is not constraint enough, potentially leading to the price being stale for almost a day.

## Code Snippet
See above.

## Tool used

Manual Review

## Recommendation
Add a custom freshness check for each price oracle closer or equal to the heartbeat of the oracle.
