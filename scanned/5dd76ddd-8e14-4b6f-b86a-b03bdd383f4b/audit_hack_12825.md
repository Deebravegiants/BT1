# [M] Results Of Oracle Price Feed Is Not Validated (Absence of check of price, Freshness, Sequencer down check)

## Summary
Severity: Medium
Reporter: 0xhacksmithh
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L237-L240
Type: audit-issue

## Details
# Results Of Oracle Price Feed Is Not Validated (Absence of check of price, Freshness, Sequencer down check)

## Summary
Absence of checks of price, freshness and Sequencer down check on return value from Oracle.
## Vulnerability Detail
Absence of proper checks for below returning results from Oracle.
```solidity
def _get_latest_oracle_price(_oracle_address: address) -> uint256:
    answer: int256 = ChainlinkOracle(_oracle_address).latestRoundData()[1]
    price: uint256 = convert(answer, uint256) # 6 dec
    return price

@internal
def _get_price_at_round(_oracle_address: address, _round_id: uint80) -> (uint256, uint256):
    answer: int256 = ChainlinkOracle(_oracle_address).getRoundData(_round_id)[1]  
    updated_at: uint256 = ChainlinkOracle(_oracle_address).getRoundData(_round_id)[3]
    price: uint256 = convert(answer, uint256) # 6 dec
    return (price, updated_at)
```

## Impact
Oracle will give `Stale Price`

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L237-L240
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L243-L247
## Tool used

Manual Review

## Recommendation
Should apply checks for those.
