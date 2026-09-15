# [M] Missing checks for whether the `L2-Sequencer` is active & for Grace Periods.

## Summary
Severity: Medium
Reporter: shealtielanz
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L243C1-L247C31
Type: audit-issue

## Details
# Missing checks for whether the `L2-Sequencer` is active & for Grace Periods.

## Summary
Chainlink recommends that users using price oracles, check whether the Arbitrum Sequencer is [active](https://docs.chain.link/data-feeds/l2-sequencer-feeds#arbitrum). If the sequencer goes down, the Chainlink oracles will have stale prices from before the downtime, until a new L2 OCR transaction goes through. Users who submit their transactions via the [L1 Delayed Inbox](https://developer.arbitrum.io/tx-lifecycle#1b--or-from-l1-via-the-delayed-inbox) will be able to take advantage of these stale prices. Use a [Chainlink oracle](https://blog.chain.link/how-to-use-chainlink-price-feeds-on-arbitrum/#almost_done!_meet_the_l2_sequencer_health_flag) to determine whether the sequencer is offline or not, and don't allow operations to take place while the sequencer is offline.
## Vulnerability Detail
- In the `_get_latest_oracle_price` function in `TrailingStopDex.vy` 
```vyper
    answer: int256 = ChainlinkOracle(_oracle_address).latestRoundData()[1]
```
There is no check if the `sequencer` is `active`.
- In the `_get_price_at_round` function of `TrailingStopDex.vy`
```vyper
  answer: int256 = ChainlinkOracle(_oracle_address).getRoundData(_round_id)[1]
 updated_at: uint256 = ChainlinkOracle(_oracle_address).getRoundData(_round_id)[3]
```
There also is no check here if the `sequencer` is `active`.
## Impact

## Code Snippet
- The `_get_price_at_round` Function  ~ [Click here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L243C1-L247C31)
- The  `_get_latest_oracle_price` Function  ~ [Click here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L237C1-L240C17)
## Tool used

`Manual Review`

## Recommendation
`code example of Chainlink`:
https://docs.chain.link/data-feeds/l2-sequencer-feeds#example-code
