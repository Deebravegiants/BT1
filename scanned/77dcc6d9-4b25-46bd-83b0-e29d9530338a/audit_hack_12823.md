# [M] _to_usd_oracle_price : oracle freshness check is not sufficient. Still stale data is possible

## Summary
Severity: Medium
Reporter: 0xpinky
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L562C5-L562C25
Type: audit-issue

## Details
# _to_usd_oracle_price : oracle freshness check is not sufficient. Still stale data is possible

## Summary

Contract has the  function [_to_usd_oracle_price](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L562C5-L562C25) to fetch the real time price value of the usd (from function name).

It checks for sequencer up and running and the calls the chainlink's `latestRoundData` to get the price, last updated and so.

It has check to validate the freshness of price value, but the threshold used to validate the price is too huge, so , still the stale price value is possible.

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


    usd_price: uint256 = convert(answer, uint256)  # 8 dec
    return usd_price

```

ORACLE_FRESHNESS_THRESHOLD value is 24 hours. But when we look at the chainink's feed, the price value would be updated, at the gap of 1 hour.

https://data.chain.link/ethereum/mainnet/crypto-usd/eth-usd - refer the trigger parameter option.

checking the price value which has less than 24 hours freshness could be still stale.

The price could be updated 23 hours before also.

## Impact

old price value could be used to decide the asset price value.
Either loss to the protocol or to the user.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L560-L583

## Tool used

Manual Review

## Recommendation

we suggest to use the ORACLE_FRESHNESS_THRESHOLD  as one hour.
