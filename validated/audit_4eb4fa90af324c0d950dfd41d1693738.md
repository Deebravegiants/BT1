### Title
Missing L2 Sequencer Uptime Check in Chainlink Oracle Allows Stale Price Exploitation During Sequencer Downtime - (File: contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol)

---

### Summary

`ChainlinkOracleForRSETHPoolCollateral.getRate()` calls Chainlink's `latestRoundData()` on L2-deployed pool contracts without validating whether the L2 sequencer is operational. When the sequencer is down, Chainlink feeds on L2 return stale prices that appear fresh, allowing an attacker to deposit supported collateral tokens into `RSETHPoolV3` at a manipulated rate and receive more `wrsETH` than the current fair value.

---

### Finding Description

`ChainlinkOracleForRSETHPoolCollateral.getRate()` performs three validity checks on the Chainlink response — `answeredInRound < roundID`, `timestamp == 0`, and `ethPrice <= 0` — but performs **no check against a Chainlink L2 Sequencer Uptime Feed**. [1](#0-0) 

On L2 chains (Arbitrum, Optimism, Base, Scroll, etc.), when the sequencer goes offline, Chainlink oracles continue to serve the last known price. The `answeredInRound >= roundID` check still passes because no new round has been opened — the data simply has not been updated. The `timestamp != 0` check also passes for the same reason. The price therefore appears valid to the contract while being arbitrarily stale.

`RSETHPoolV3` uses this oracle as `supportedTokenOracle[token]` to compute `tokenToETHRate` in `viewSwapRsETHAmountAndFee`: [2](#0-1) 

The minted `wrsETH` amount is:

```
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate
```

If `tokenToETHRate` is stale-high (the collateral token's ETH price was higher before the sequencer went down), the depositor receives more `wrsETH` than the current fair value of their deposit.

`ChainlinkPriceOracle.sol` (mainnet) also calls `latestRoundData()` ignoring all return values except `price`, but it is deployed only on Ethereum mainnet where no sequencer feed is needed. [3](#0-2) 

---

### Impact Explanation

An attacker who deposits a supported collateral token (e.g., WETH) into `RSETHPoolV3` on an L2 chain during sequencer downtime receives excess `wrsETH` minted against a stale inflated price. The pool's ETH/token reserves are drained relative to the `wrsETH` supply, constituting direct theft of value from the pool and its liquidity. This maps to **Critical — direct theft of user funds** if the price deviation is large, or at minimum **Medium — temporary freezing/theft of unclaimed yield** for smaller deviations.

---

### Likelihood Explanation

L2 sequencer outages are documented historical events (Arbitrum and Optimism have both experienced downtime). The pool contracts are explicitly deployed on multiple L2 chains. The `deposit(address token, uint256 amount, string referralId)` entry point is publicly callable by any address with no access restriction beyond `whenNotPaused`. [4](#0-3) 

---

### Recommendation

Add a sequencer uptime check in `ChainlinkOracleForRSETHPoolCollateral.getRate()` using the Chainlink L2 Sequencer Uptime Feed before consuming `latestRoundData()`. The standard pattern is:

```solidity
(, int256 sequencerAnswer, uint256 startedAt,,) = sequencerUptimeFeed.latestRoundData();
if (sequencerAnswer != 0) revert SequencerDown();
if (block.timestamp - startedAt < GRACE_PERIOD) revert GracePeriodNotOver();
```

A grace period (e.g., 3600 seconds) should be enforced after sequencer recovery to allow prices to normalize before accepting deposits.

---

### Proof of Concept

1. L2 sequencer goes offline. At the time of outage, WETH/ETH price reported by Chainlink is `1.05e18` (stale-high).
2. True market price of WETH/ETH has since dropped to `1.00e18`, but the sequencer is down so no new round is posted.
3. Attacker calls `RSETHPoolV3.deposit(WETH, 100e18, "")` on Arbitrum.
4. `ChainlinkOracleForRSETHPoolCollateral.getRate()` returns `1.05e18` — passes all three checks (`answeredInRound >= roundID`, `timestamp != 0`, `ethPrice > 0`).
5. `viewSwapRsETHAmountAndFee` computes `rsETHAmount = 100e18 * 1.05e18 / rsETHToETHrate`, yielding ~5% more `wrsETH` than the fair amount.
6. Attacker receives excess `wrsETH`, redeemable for ETH once the sequencer recovers, extracting value from the pool. [1](#0-0) [5](#0-4)

### Citations

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-37)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L271-293)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L315-335)
```text
    function viewSwapRsETHAmountAndFee(
        uint256 amount,
        address token
    )
        public
        view
        onlySupportedToken(token)
        returns (uint256 rsETHAmount, uint256 fee)
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```
