# [M] Missing sanity checks on Chainlink oracle data retrieval

## Summary
Severity: Medium
Reporter: 0x4non
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L562-L580
Type: audit-issue

## Details
# Missing sanity checks on Chainlink oracle data retrieval

# Missing Sanity Check in Chainlink Oracle Data Retrieval

## Summary

The `_to_usd_oracle_price(_token: address)` function retrieves the latest Chainlink oracle price for a specified token. While it checks for oracle freshness and sequencer availability, it lacks some essential sanity checks on the returned oracle data, potentially leading to erroneous price information.

## Vulnerability Detail

The Chainlink Oracle's `latestRoundData()` returns several pieces of data including `round_id`, `answer`, `started_at`, `updated_at`, and `answered_in_round`. However, there are no sanity checks performed on these returned values, which could lead to potential issues if erroneous data is returned. Specifically, the following conditions should be met for valid oracle data: `round_id != 0`, `answer >= 0`, `updated_at != 0`, and `updated_at <= block.timestamp`.

You could read more about it in [here](https://0xmacro.com/blog/how-to-consume-chainlink-price-feeds-safely/)

## Impact

The lack of these checks could potentially lead to incorrect price data being used in the protocol. This could impact any operations dependent on the price data, such as token swaps, liquidity provision, and other financial transactions.

## Code Snippet

[Vault.vy#L562-L580](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L562-L580)

## Tool used

Manual Review

## Recommendation

Add sanity checks on the returned data from `latestRoundData()` call. Specifically, ensure the following conditions are met: `round_id != 0`, `answer >= 0`, `updated_at != 0`, and `updated_at <= block.timestamp`. Adding these checks will ensure that only valid oracle data is used by the protocol, improving the protocol's reliability and accuracy of operations.
