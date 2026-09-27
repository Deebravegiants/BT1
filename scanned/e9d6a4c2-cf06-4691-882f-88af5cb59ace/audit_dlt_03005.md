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
166:	    tradeEnd[kind] = trade.endTime(); // {s}

168:	}
}
```

Now, let's consider a scenario where one of the `assets` in the `basket` temporarily falls into an `IFFY` status. 
At this point, the current status of the `basket` is also `IFFY` (`line 323~325`).
```
function status() public view returns (CollateralStatus status_) {
	uint256 size = basket.erc20s.length;
    if (disabled || size == 0) return CollateralStatus.DISABLED;
    
    for (uint256 i = 0; i < size; ++i) {
        CollateralStatus s = assetRegistry.toColl(basket.erc20s[i]).status();
323:        if (s.worseThan(status_)) {
324:            if (s == CollateralStatus.DISABLED) return CollateralStatus.DISABLED;
325:            status_ = s;
        }
    }
}
```
The `auction` is settled one day later, triggering the `rebalance` function (`line 92`).
```
function settleTrade(IERC20 sell) public override(ITrading, TradingP1) returns (ITrade trade) {
    delete tokensOut[sell];
    trade = super.settleTrade(sell); // nonReentrant

    if (_msgSender() == address(trade)) {        
92:        try this.rebalance(trade.KIND()) {} catch (bytes memory errData) {
        }
    }
}
```
The check at `line 116` passes because the caller is the `BackingManager` itself. 
However, the `BasketHandler` status is still `IFFY`, meaning it isn't ready for a new `auction`. 
As a result, the check at `line 121` prevents the next `auction` from being created.
```
function rebalance(TradeKind kind) external nonReentrant {
    requireNotTradingPausedOrFrozen();
    assetRegistry.refresh();

    require(
116:        _msgSender() == address(this) || tradeEnd[kind] < block.timestamp,
        "already rebalancing"
    );

    require(tradesOpen == 0, "trade open");
    
121:    require(basketHandler.isReady(), "basket not ready");
    
    require(block.timestamp >= basketHandler.timestamp() + tradingDelay, "trading delayed");
}
```
The `traceEnd` is still set to `T + 7 days` and the current time is now `T + 1 day`.

After another day, the `asset`'s status recovers to `SOUND`, and the `BasketHandler` status updates to `SOUND` as well. 
After the `warm-up period` (`1 minute` in our scenario), the `BasketHandler` is ready, and the time is now `T + 2 days + 1 minute`. 
At this point, we want to create a new `Dutch auction` for `rebalancing`. 
However, we can't create the next `Dutch auction` until `T + 7 days` due to the existing `traceEnd`.

This delay clearly poses an issue.
## Tools Used

## Recommended Mitigation Steps
```
function settleTrade(IERC20 sell) public override(ITrading, TradingP1) returns (ITrade trade) {
        delete tokensOut[sell];
        trade = super.settleTrade(sell); // nonReentrant

        if (_msgSender() == address(trade)) {
            try this.rebalance(trade.KIND()) {} catch (bytes memory errData) {
                if (errData.length == 0) revert(); // solhint-disable-line reason-string
            }

+			tradeEnd[kind] = uint48(block.timestamp);

        }
    }
}
```


## Assessed type

Invalid Validation
