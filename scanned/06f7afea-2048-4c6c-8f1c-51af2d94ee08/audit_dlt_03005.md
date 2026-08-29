# [M] The traceEnd in BackingManager isn't updating correctly

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-07-reserve
Published: 2024-08-15
Source: https://github.com/code-423n4/2024-07-reserve-findings/issues/6
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-07-reserve/blob/3f133997e186465f4904553b0f8e86ecb7bbacbf/contracts/p1/BackingManager.sol#L114
https://github.com/code-423n4/2024-07-reserve/blob/3f133997e186465f4904553b0f8e86ecb7bbacbf/contracts/p1/BackingManager.sol#L166


# Vulnerability details

## Impact
In the `BackingManager`, we use the `traceEnd` value for each type of `trade` to prevent next `auction` from occurring within the same block. 
We can find a comment in the code explaining this in `line 114`.
```
function rebalance(TradeKind kind) external nonReentrant {
    // DoS prevention:
114:    // unless caller is self, require that the next auction is not in same block
    require(
        _msgSender() == address(this) || tradeEnd[kind] < block.timestamp,
        "already rebalancing"
    );
```
This approach works correctly for `Batch auctions`. 
However, with `Dutch auctions`, the `traceEnd` value can inadvertently block the next `auction` from starting for a certain period.
## Proof of Concept
The `maximum auction length` can be up to `1 week`.
```
uint48 public constant MAX_AUCTION_LENGTH = 60 * 60 * 24 * 7; // {s} max valid duration, 1 week
```
And the `minimum warm-up period` in the `BasketHandler` is `1 minute`.
```
uint48 public constant MIN_WARMUP_PERIOD = 60; // {s} 1 minute
```
Suppose a `Dutch auction` is created in the `BackingManager` with a length of `1 week` (`7 days`), starting at timestamp `T`. 
The `traceEnd` for this `auction type` is set to `T + 7 days` in `line 166`.
```
function rebalance(TradeKind kind) external nonReentrant {
155:    if (doTrade) {

165:	    ITrade trade = tryTrade(kind, req, prices);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-07-reserve-findings/issues/6_
