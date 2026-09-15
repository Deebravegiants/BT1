# [M] `Asset.lotPrice` only uses `oracleTimeout` to determine if the price is stale.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-03
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/17
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/Asset.sol#L140
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/NonFiatCollateral.sol#L52
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/Asset.sol#L61
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/curve/CurveStableCollateral.sol#L57
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/curve/PoolTokens.sol#L287
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/curve/PoolTokens.sol#L235


# Vulnerability details

## Impact

`OracleTimeout` is the number of seconds until an oracle value becomes invalid. It is set in the constructor of `Asset`. And `Asset.lotPrice` uses `OracleTimeout` to determine if the saved price is stale. However, `OracleTimeout` may not be the correct source to determine if the price is stale. `Asset.lotPrice` may return the incorrect price.

## Proof of Concept

`OracleTimeout` is set in the constructor of `Asset`.
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/Asset.sol#L61
```solidity
    constructor(
        uint48 priceTimeout_,
        AggregatorV3Interface chainlinkFeed_,
        uint192 oracleError_,
        IERC20Metadata erc20_,
        uint192 maxTradeVolume_,
        uint48 oracleTimeout_
    ) {
        …
        oracleTimeout = oracleTimeout_;
    }
```

`Asset.lotPrice` use `oracleTimeout` to determine if the saved price is in good standing.
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/Asset.sol#L140
```solidity
    function lotPrice() external view virtual returns (uint192 lotLow, uint192 lotHigh) {
        try this.tryPrice() returns (uint192 low, uint192 high, uint192) {
            // if the price feed is still functioning, use that
            lotLow = low;
            lotHigh = high;
        } catch (bytes memory errData) {
            // see: docs/solidity-style.md#Catching-Empty-Data
            if (errData.length == 0) revert(); // solhint-disable-line reason-string

            // if the price feed is broken, use a decayed historical value

            uint48 delta = uint48(block.timestamp) - lastSave; // {s}
            if (delta <= oracleTimeout) {
                lotLow = savedLowPrice;
                lotHigh = savedHighPrice;
            } else if (delta >= oracleTimeout + priceTimeout) {
                return (0, 0); // no price after full timeout
            } else {
                // oracleTimeout <= delta <= oracleTimeout + priceTimeout

                // {1} = {s} / {s}
                uint192 lotMultiplier = divuu(oracleTimeout + priceTimeout - delta, priceTimeout);

                // {UoA/tok} = {UoA/tok} * {1}
                lotLow = savedLowPrice.mul(lotMultiplier);
                lotHigh = savedHighPrice.mul(lotMultiplier);
            }
        }
        assert(lotLow <= lotHigh);
    }
```

However, `oracleTimeout` may not be the accurate source to determine if the saved price is stale. The following examples shows that using only `oracleTimeout` is vulnerable.

1. `NonFiatCollateral.tryPrice` leverages two price feeds to calculate the price. These two feeds have different timeouts. 
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/NonFiatCollateral.sol#L52
```
    function tryPrice()
        external
        view
        override
        returns (
            uint192 low,
            uint192 high,
            uint192 pegPrice
        )
    {
        pegPrice = chainlinkFeed.price(oracleTimeout); // {target/ref}

        // Assumption: {ref/tok} = 1; inherit from `AppreciatingFiatCollateral` if need appreciation
        // {UoA/tok} = {UoA/target} * {target/ref} * {ref/tok} (1)
        uint192 p = targetUnitChainlinkFeed.price(targetUnitOracleTimeout).mul(pegPrice);

        // this oracleError is already the combined total oracle error
        uint192 err = p.mul(oracleError, CEIL);

        low = p - err;
        high = p + err;
        // assert(low <= high); obviously true just by inspection
    }
```
If `targetUnitChainlinkFeed` is malfunctioning and `targetUnitOracleTimeout` is smaller than `oracleTimeout`, `lotPrice()` should not return saved price when `delta > targetUnitOracleTimeout`. However, `lotPrice()` only considers `oracleTimeout`. It could return the incorrect price when `targetUnitChainlinkFeed` is malfunctioning.

2. To calculate the price, `CurveStableCollateral.tryPrice` calls `PoolToken.totalBalancesValue`. And `PoolToken.totalBalancesValue` calls `PoolToken.tokenPrice`. `PoolToken.tokenPrice` uses multiple feeds to calculate the price. And they could have different timeouts. None of them are used in `lotPrice()`.
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/curve/CurveStableCollateral.sol#L57
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/curve/PoolTokens.sol#L287
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/curve/PoolTokens.sol#L235
```solidity
    function tryPrice()
        external
        view
        virtual
        override
        returns (
            uint192 low,
            uint192 high,
            uint192
        )
    {
        // {UoA}
        (uint192 aumLow, uint192 aumHigh) = totalBalancesValue();

        // {tok}
        uint192 supply = shiftl_toFix(lpToken.totalSupply(), -int8(lpToken.decimals()));
        // We can always assume that the total supply is non-zero

        // {UoA/tok} = {UoA} / {tok}
        low = aumLow.div(supply, FLOOR);
        high = aumHigh.div(supply, CEIL);
        assert(low <= high); // not obviously true just by inspection

        return (low, high, 0);
    }


    function totalBalancesValue() internal view returns (uint192 low, uint192 high) {
        for (uint8 i = 0; i < nTokens; ++i) {
            IERC20Metadata token = getToken(i);
            uint192 balance = shiftl_toFix(curvePool.balances(i), -int8(token.decimals()));
            (uint192 lowP, uint192 highP) = tokenPrice(i);

            low += balance.mul(lowP, FLOOR);
            high += balance.mul(highP, CEIL);
        }
    }

    function tokenPrice(uint8 index) public view returns (uint192 low, uint192 high) {
        ...

        if (index == 0) {
            x = _t0feed0.price(_t0timeout0);
            xErr = _t0error0;
            if (address(_t0feed1) != address(0)) {
                y = _t0feed1.price(_t0timeout1);
                yErr = _t0error1;
            }
        ...

        return toRange(x, y, xErr, yErr);
    }
```
We can also find out that `oracleTimeout` is unused. But `lotPrice()` still uses it to determine if the saved price is valid. This case is worse than the first case.
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/curve/CurveStableCollateral.sol#L28
```solidity
    /// @dev config Unused members: chainlinkFeed, oracleError, oracleTimeout
    /// @dev config.erc20 should be a RewardableERC20
    constructor(
        CollateralConfig memory config,
        uint192 revenueHiding,
        PTConfiguration memory ptConfig
    ) AppreciatingFiatCollateral(config, revenueHiding) PoolTokens(ptConfig) {
        require(config.defaultThreshold > 0, "defaultThreshold zero");
    }
```

## Tools Used

Manual Review

## Recommended Mitigation Steps

Since collaterals have various implementations of price feed. `Asset.lotPrice` could be modified like:
```diff
    function lotPrice() external view virtual returns (uint192 lotLow, uint192 lotHigh) {
        …
-           if (delta <= oracleTimeout) {
+           if (delta <= actualOracleTimeout()) {
                lotLow = savedLowPrice;
                lotHigh = savedHighPrice;
        …
    }

+   function actualOracleTimeout() public view virtual returns (uint192) {
+       return oracleTimeout;
+   }
```

Then, collaterals can override `actualOracleTimeout` to reflect the correct oracle timeout.




## Assessed type

Error
