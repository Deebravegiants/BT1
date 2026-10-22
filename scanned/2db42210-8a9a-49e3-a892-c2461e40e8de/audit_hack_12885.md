# [M] converting the negative price value as positive from chainlink's feed is dangerous.

## Summary
Severity: Medium
Reporter: 0xpinky
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L560-L583
Type: audit-issue

## Details
# converting the negative price value as positive from chainlink's feed is dangerous.

## Summary

when fetching the asset price using the function [_to_usd_oracle_price](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L560-L583) from chainlink's aggregator , the price value is directly type casted without checking whether it is positive or negative.

There are possibility that the chainlinks price value could be negative also. Thats the reason for using the int instead of uint.

typecasting the negative value as uint256 would overflow which would lead to high price value.

## Vulnerability Detail
```vyper
@view
@internal
def _to_usd_oracle_price(_token: address) -> uint256:
    """
    @notice
        Retrieves the latest Chainlink oracle price for _token.
        Ensures that the Arbitrum sequencer is up and running and
        that the Chainlink feed is fresh.
    """
    assert self._sequencer_up(), "sequencer down"


    round_id: uint80 = 0
    answer: int256 = 0
    started_at: uint256 = 0
    updated_at: uint256 = 0
    answered_in_round: uint80 = 0
    round_id, answer, started_at, updated_at, answered_in_round = ChainlinkOracle(
        self.to_usd_oracle[_token]
    ).latestRoundData()


    assert (block.timestamp - updated_at) < ORACLE_FRESHNESS_THRESHOLD, "oracle not fresh"


    usd_price: uint256 = convert(answer, uint256)  # 8 dec ------------------------------->>> audit find. int value is converted as uint
    return usd_price
```
## Impact

too large unrealistic price value if the fetched price is negative.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L560-L583

## Tool used

Manual Review

## Recommendation

check for negative price value. if so, revert.
