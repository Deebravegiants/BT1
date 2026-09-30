# [M] If a token's oracle goes down, liquidations and market orders will be frozen

## Summary
Severity: Medium
Reporter: Dug
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L560-L583
Type: audit-issue

## Details
# If a token's oracle goes down, liquidations and market orders will be frozen

## Summary

In some extreme cases, oracles can be taken offline. In these cases, liquidations and market orders will be frozen (all calls will revert).

## Vulnerability Detail

Chainlink has taken oracles offline in extreme cases. For example, during the UST collapse, Chainlink paused the UST/ETH price oracle, to ensure that it wasn't providing inaccurate data to protocols.

In such a situation, all liquidations and market orders for users holding the frozen asset would revert, as the attempted `latestRoundData` calls to the Chainlink oracle would revert.

The code that would revert it is called from the `_to_usd_oracle_price` function in the `Vault` contract. 

```vyper
    round_id, answer, started_at, updated_at, answered_in_round = ChainlinkOracle(
        self.to_usd_oracle[_token]
    ).latestRoundData()
```

If the oracle price lookup reverts, liquidations and market orders will be frozen.

## Impact

Liquidations and market orders may not be possible at a time when the protocol needs them most. As a result, the value of user's asset may fall below their debts, turning off any liquidation incentive and pushing the protocol into insolvency.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L560-L583

## Tool used

Manual Review

## Recommendation

Use try/catch block. The logic for getting the token's price from the Chainlink data feed should be placed in the try block, while some fallback logic when the access to the Chainlink oracle data feed is denied should be placed in the catch block. E.g:

```vyper
    try:
        round_id, answer, started_at, updated_at, answered_in_round = ChainlinkOracle(
            self.to_usd_oracle[_token]
        ).latestRoundData()
    except:
        # handle failure here:
        # revert, call propietary fallback oracle, fetch from another 3rd-party oracle, etc.
```
