# [M] Unsafe Casting Chainlinks price might return an insane big price

## Summary
Severity: Medium
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L572-L582
Type: audit-issue

## Details
# Unsafe Casting Chainlinks price might return an insane big price

## Summary
Unsafe Casting Chainlinks price might return an insane big price

## Vulnerability Detail
Unstoppable are currently fetching price from chainlink in the following way:

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
    return usd_price
```

The problem with this implementation is that chainlink's `answer` parameter is returned as an `int` `answer: int256 ` because it can return negative in some cases.

The issue becomes when handling this `answer` after the call. As you can see `usd_price: uint256 = convert(answer, uint256)`  is directly casted from `int` to `uint` without even checking the value.
If chainlink returns a negative price, there will be an overflow and it will completely miss-price the asset.

## Impact
Loss of funds for the protocol if the `answer` overflows, allowing any MEV/user to take profit

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L572-L582

## Tool used

Manual Review

## Recommendation
Do not cast the answer to `uint` without checking that it is not > 0 first
