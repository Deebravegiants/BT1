# [M] An attacker can bypass the dynamic fees in `lovStEth` vault under certain depeg conditions, and extract value from honest depositors

## Summary
Severity: Medium
Chain: Smart contract
Component: Origami
Published: 2024-03-07
Source: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/62
Type: hats-finding

## Details
**Github username:** @JacoboLansac
**Twitter username:** jacolansac
**Submission hash (on-chain):** 0xf5535caf5ddd83dbf465671a07fdc09f5879bdfc060a9897aced7401978cd096
**Severity:** medium

**Description:**
Users deposit wstETH in the lovStEth vault in exchange for lovStEth tokens, which represent shares of that vault. When a deposit is made, the vault reads the SPOT price to determine the value of the reserves and calculate the exchange rate between the deposited wstETH and the shares the depositor will get. 

When the value of wstETH fluctuates upwards deviating from the historical value, a depositor would receive a favorable deal, i.e., more shares. Once the fluctuation is corrected and the rate goes back to normal, the depositor could redeem the shares and receive back more wstETH than invested. This *trade* would leech value from the vault, essentially stealing from other honest users of the vault. 

To protect honest users from this attack vector, the Origami team put in place a protection mechanism based on dynamic fees. From the [Design notes: defense-in-depth](https://github.com/TempleDAO/origami-public/blob/185a93e25071b6a110ca190e94a6a826e982b2d6/docs/contents/OrigamiHatsAuditComp.md#defense-in-depth) (docs provided as part of the contest description), we can read the following specifications about the Dynamic fees mechanism:

> - Economic guards are in place to dissuade leeching value from existing vault users when the Chainlink Oracle value varies from the expected historic 1:1 peg for DAI/USDC and stETH/ETH
> - When the underlying is trading below peg it charges a multiple of the difference between the oracle price and 1 for withdrawals and assumes the underlying is trading at peg for deposits.
> - When the underlying is trading above peg it charges a multiple of the difference between the oracle price and 1 for deposits and assumes the underlying is trading at peg for withdrawals

The implementation of the Dynamic fees consists of calculating the difference between the HISTORICAL and SPOT exchange rates, (called `delta`), and charging a proportional fee to that difference, but only if the difference goes in favor of the user. This `delta` is scaled by the `_feeLeverageFactor`. If the SPOT depegs upwards (higher value of the underlying), deposits are penalized. If the SPOT depegs downwards, withdrawals are penalized. 

Here is the call to the `DynamicFees` library that calculates the dynamic-deposit fees (a similar call is made for the exit fees). Note that as an input argument, we have to provide the debt-to-assets oracle, which in the case of the `lovStEth` vault, is the `OrigamiWstEthToEthOracle`, which returns the rate `ETH to wstETH` (how much wstETH per ETH):

*OrigamiLovTokenFlashAndBorrowManager.sol:*
```javascript
    function _dynamicDepositFeeBps() internal override view returns (uint256) {
        return DynamicFees.dynamicFeeBps(
            DynamicFees.FeeType.DEPOSIT_FEE,
@>          debtTokenToReserveTokenOracle, // OrigamiWstEthToEthOracle, (WETH for 1 wstETH)
            address(_reserveToken), // expected baseAsset (wstETH for lovStEth)
            _minDepositFeeBps,
            _feeLeverageFactor  // FROM TESTS: uint16 public constant LOV_ETH_FEE_LEVERAGE_FACTOR = 15;
        );
    }
```

The `DynamicFees::dynamicFeeBps()` calls `oracle.lastPrices()` which makes two calls to `oracle.latestPrice()`, one for SPOT and one for HISTORIC:

*DynamicFees.sol:*
```javascript
    /**
     * @notice The current deposit or exit fee based on market conditions.
     * Fees are applied to the portion of lovToken shares the depositor 
     * would have received. Instead that fee portion isn't minted (benefiting remaining users)
     */
    function dynamicFeeBps(
        FeeType feeType,
@>      IOrigamiOracle oracle,
        address expectedBaseAsset,
        uint64 minFeeBps,
        uint256 feeLeverageFactor
    ) internal view returns (uint256) {
@>      (uint256 _spotPrice, uint256 _histPrice, address _baseAsset, address _quoteAsset) = oracle.latestPrices(
@>          IOrigamiOracle.PriceType.SPOT_PRICE,
            OrigamiMath.Rounding.ROUND_UP,
@>          IOrigamiOracle.PriceType.HISTORIC_PRICE,
            OrigamiMath.Rounding.ROUND_DOWN
        );
        
        bool _inQuotedOrder;
        if (_baseAsset == expectedBaseAsset) {
            _inQuotedOrder = true;
        } else if (_quoteAsset == expectedBaseAsset) {
            _inQuotedOrder = false;
        } else {
            revert CommonEventsAndErrors.InvalidToken(expectedBaseAsset);
        }

        uint256 _delta;
        if (feeType == FeeType.DEPOSIT_FEE) {
            // If spot price is > than the expected historic, then they are exiting
            // at a price better than expected. The exit fee is based off the relative
            // difference of the expected spotPrice - historicPrice.
            // Or opposite if the oracle order is inverted
            unchecked {
                if (_inQuotedOrder && _spotPrice < _histPrice) {
                    _delta = _histPrice - _spotPrice;
                } else if (!_inQuotedOrder && _spotPrice > _histPrice) {
                    _delta = _spotPrice - _histPrice;
                }
            }
        } else {
            // If spot price is > than the expected historic, then they are exiting
            // at a price better than expected. The exit fee is based off the relative
            // difference of the expected spotPrice - historicPrice.
            // Or opposite if the oracle order is inverted
            unchecked {
                if (_inQuotedOrder && _spotPrice > _histPrice) {
                    _delta = _spotPrice - _histPrice;
                } else if (!_inQuotedOrder && _spotPrice < _histPrice) {
                    _delta = _histPrice - _spotPrice;
                }
            }
        }

        // If no delta, just return the min fee
        if (_delta == 0) {
            return minFeeBps;
        }

        // Relative diff multiply by a leverage factor to match the worst case lovToken
        // effective exposure
        uint256 _fee = _delta.mulDiv(
            feeLeverageFactor * OrigamiMath.BASIS_POINTS_DIVISOR,
            _histPrice,
            OrigamiMath.Rounding.ROUND_UP
        );

        // Use the maximum of the calculated fee and a pre-set minimum.
        return minFeeBps > _fee ? minFeeBps : _fee;
    }
```

```javascript
    /**
     * @notice Same as `latestPrice()` but for two separate prices from this oracle
     */
    function latestPrices(
        PriceType priceType1, 
        OrigamiMath.Rounding roundingMode1,
        PriceType priceType2, 
        OrigamiMath.Rounding roundingMode2
    ) external override view returns (
        uint256 /*price1*/, 
        uint256 /*price2*/, 
        address /*baseAsset*/,
        address /*quoteAsset*/
    ) {
        return (
@>          latestPrice(priceType1, roundingMode1),
@>          latestPrice(priceType2, roundingMode2),
            baseAsset,
            quoteAsset
        );
    }

```

The particular implementation of `OrigamiWstEthToEthOracle::latestPrice()` to return the `wstETH to ETH` rate is to multiply two other exchange rates, read from two other sources:
1. It reads the `wstETH to stETH` rate from Lido's `stEth` contract with a call to `stEth.getPooledEthByShares()`.
2. It reads the `stETH to ETH` rate from a Chainlink price feed.
3. It multiplies the previous two exchange rates to calculate `wstETH` to `ETH` rate.

*OrigamiWstEthToEthOracle.sol*:
```javascript
    /**
     * @notice Return the latest oracle price, to `decimals` precision
     * @param priceType What kind of price - Spot or Historic
     * @param roundingMode Round the price at each intermediate step such that the final price rounds in the specified direction.
     */
    function latestPrice(
        PriceType priceType, 
        OrigamiMath.Rounding roundingMode
    ) public override view returns (uint256 price) {
        // 1 wstETH to stETH
@>      price = stEth.getPooledEthByShares(precision);  // @audit-issue same price returned for SPOT and HISOTIRC

        // Convert wstETH to ETH using the stEth/ETH oracle price
@>      price = price.mulDiv(
@>          stEthToEthOracle.latestPrice(priceType, roundingMode),
            precision,
            roundingMode
        );
    }
```

*The Issue:*

The issue is that `stEth.getPooledEthByShares()` **always** returns SPOT values regardless if `PriceType` is HISTORIC or SPOT, because in both cases it makes the static call to the `stEth` contract, which provides the SPOT value. This has some implications for the calculated value of `delta` that are discussed below. For this discussion, I will use the non-conventional notation for the exchange rates. I will refer to `ETH/wstETH_spot` as *how much ETH per 1 wstETH in the SPOT rate*.

For the sake of simplicity, let's assume that `SPOT > HIST` in this example, has a positive value of `delta` in the calculations below:
    
    delta = SPOT - HIST

Following the implementation inside `OrigamiWstEthToEthOracle::latestPrice()` multiplying the two rates, the `ETH/wstETH` rate combining can be formulated as follows (for HISTORIC and SPOT):

    ETH/wstETH_spot = stETH/wstETH_spot * ETH/stETH_spot    // SPOT price
    ETH/wstETH_hist = stETH/wstETH_hist * ETH/stETH_hist    // HISTORIC price

Now we can rewrite delta as:

    delta = ETH/wstETH_spot - ETH/wstETH_hist
    delta = (stETH/wstETH_spot * ETH/stETH_spot) - (stETH/wstETH_hist * ETH/stETH_hist)

Given that `stETH.getPooledEthByShares()` returns the same rate for SPOT and HISTORIC (which is the SPOT rate), we can substitute `stETH/wstETH_hist = stETH/wstETH_spot` in the equation above:

    delta = (stETH/wstETH_spot * ETH/stETH_spot) - (stETH/wstETH_spot * ETH/stETH_hist)

Which can be rewritten as:

    delta = stETH/wstETH_spot * (ETH/stETH_spot - ETH/stETH_hist)

Hence, the value of `delta` is a multiplication of two factors:
- The `delta` between SPOT and HISTORIC for the `ETH/stETH` rate (both provided by Chainlink price feed).
- The **<ins>absolute</ins>** value of the `stETH/wstETH_spot` rate read from `stETH.getPooledEthByShares()`

This has the following implications (the 3rd one is the most important):

1. The protocol will charge a different amount of fees than intended on lovStEth deposits/exits.
2. The fees charged will increase monotonically over time, due to the increasing nature of `stETH/wstETH_spot` (which increases because of Lido's periodic rewards distributions).
3. When the `ETH/stETH` is very close to peg, the second term becomes 0, and the depegs on the `stETH/wstETH` rate will be ignored in the overall delta, and will also be 0. Hence, the Dynamic fees mechanism will be bypassed, and the depositor will be only charged the minimum fee. 

**Attack scenario: *deposits***

An attacker can exploit point above 3 with the following attack. The objective is simple: 

> Deposit some wstETH and exit receiving more wstETH than deposited. Also, do that in the shortest time span possible. 

The attacker wants to <ins>deposit</ins> when:
- `WETH/stETH` is as close to 1 as possible (perfect peg), to make the dynamic fees as small as possible.
- `stETH/wstETH` is higher than historical values (1.15 currently), making the overall rate `wstETH/WETH` higher than usual, therefore receiving more shares than usual.

Note that the `stETH/wstETH` rate can be predicted by monitoring the mempool, watching the transactions that will interact with the `stETH` contract, and predicting upwards fluctuations. When he predicts a fluctuation, he reads chainlinks price feed, and if the SPOT `ETH/stETH` rate is very close to the peg, he attacks:

- The attacker backruns the transactions that create the fluctuation, and deposits as much `wstETH` as he has. He will be charged the minimum fees because the delta will be close to 0 (thanks to the perfect peg), but he would get more lovTokens than he normally would, because of the upwards fluctuation read from `stETH` contract.
- Then he waits for a few transactions until the price fluctuation is gone, (the rate `stETH/wstETH` goes back to 1.15 ish), and exits the position. He receives more wstETH than deposited, making a profit at the expense of honest vault users, which could be considered as stealing funds.

Note that the size of the attack is limited to the capital at the disposal of the attacker. A flashloan is not possible because the attack spans more than one transaction.

**Attack scenario: *exits***

A similar attack can be performed on exits. However, this requires that the attacker starts from the opposite initial state: having already deposited, and holding lovStEth tokens. If the depeg occurs in the opposite direction making withdrawals more favorable, he would exit then. When the peg is back, he would deposit again, receiving more lovStEth tokens than he initially withdrew.


**Impact**

Under specific depeg conditions, an attacker can extract value from the vault that would have otherwise been accrued by honest users. This could classify as a *high* severity issue, according to:

> Theft or long-term freezing of unclaimed yield or other assets.

Alternatively, as the attack is only possible by bypassing the dynamic fees mechanism protection, it would classify at least as a **medium** according to:

> Attacks that make essential functionality of the contracts temporarily unusable or inaccessible.

**Recommendation**

In the `OrigamiWstEthToEthOracle`, read HISTORIC `stETH/wstETH` rate from a Chainlink's price feed, if possible. For SPOT, it is fine to keep using `stETH.getPooledEthByShares()`, as it is the most accurate spot rate possible.


**Alternative recommendation**

I wanted to discuss an alternative implementation of the dynamic fees, that does not require calls to oracles when calculating the delta. The ultimate rate that needs to be compared when charging an extra fee is the rate between the deposited asset (wstETH) and the shares received (lovStEth tokens). 

This alternative implementation is to have a state variable in the lovStEth vault, with the HISTORIC rate. The interesting part is that the HISTORIC can be calculated using the *the moving average of the rates given in previous deposits/exits*. 

For calculating the Moving Average in an efficient matter, I recommend using a recursive formulation for Moving averages, that only requires the last Moving Average value and the new information to update the state. This is therefore very efficient, and very affordable in terms of gas to be included in deposits/exits.

When a new deposit arrives, the vault calculates the shares that will be given based on the SPOT prices with the current implementation (no changes here). Then this SPOT is compared with the HISTORICAL to calculate the delta and the dynamic fees. Right after, the HISTORICAL state variable is updated with the recursive formulation for a Moving Average.

Remarkably, this type of Moving Average will not be *time*-based but *count*-based. This is that, at any time, the moving average is not an average of the past *period* (a week for instance), but of the past N points, because it is updated with each new transaction, regardless of how long time passed since the last one. The length of the window can be controlled with something called the *forgetting factor*, which is something like "how many points do you want to remember for computing the average at any point*. An attacker could influence the value of the Moving Average by sending multiple small deposits/exits in a single block before performing another attack. To defend against this, the Moving Average should be only updated once per block.

There are probably many more nuances to the problem, but I would be happy to discuss further with the team if needed.
