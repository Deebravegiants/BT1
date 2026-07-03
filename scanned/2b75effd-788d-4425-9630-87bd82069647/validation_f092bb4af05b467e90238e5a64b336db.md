### Title
Missing L2 Sequencer Uptime Check in Chainlink Oracle Allows Stale Price Exploitation on Arbitrum - (File: contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol)

### Summary
`ChainlinkOracleForRSETHPoolCollateral` is deployed on Arbitrum and used to price collateral tokens (e.g., wstETH) in `RSETHPool`. It calls `latestRoundData()` without verifying that the Arbitrum sequencer is live. If the sequencer goes down, the oracle silently returns stale prices, enabling users to deposit collateral at an incorrect rate and receive a miscalculated amount of rsETH.

### Finding Description
`ChainlinkOracleForRSETHPoolCollateral.getRate()` calls `AggregatorV3Interface(oracle).latestRoundData()` and performs three sanity checks: `answeredInRound < roundID` (stale round), `timestamp == 0` (incomplete round), and `ethPrice <= 0` (invalid price). None of these checks detect sequencer downtime. [1](#0-0) 

When the Arbitrum sequencer is down, L2-submitted oracle update transactions are not processed. The last committed price remains valid from the contract's perspective — `answeredInRound >= roundID`, `timestamp != 0`, and `ethPrice > 0` — so all three guards pass and the stale price is returned as if it were current.

This oracle is wired into `RSETHPool` (explicitly the Arbitrum pool) as the collateral token oracle via `supportedTokenOracle[token]`: [2](#0-1) 

The stale rate flows directly into the rsETH minting calculation: [3](#0-2) 

```
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`tokenToETHRate` is sourced from `ChainlinkOracleForRSETHPoolCollateral.getRate()`. If the stale price is higher than the actual market price (e.g., wstETH dropped during downtime), the numerator is inflated and the user receives more rsETH than the deposited collateral is worth.

`ChainlinkPriceOracle.getAssetPrice()` has the same gap — it discards all five return values except `price` with no sequencer check at all: [4](#0-3) 

### Impact Explanation
During Arbitrum sequencer downtime, a user can deposit collateral tokens at a stale (pre-downtime) price that is higher than the actual post-downtime market price. The formula `rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate` over-mints rsETH relative to the real value deposited. The pool's rsETH inventory is drained at a rate exceeding the real collateral value, constituting theft of funds held in the pool. This maps to **Medium — Temporary freezing of funds** (the pool's rsETH reserve is depleted at an incorrect rate during the sequencer outage window) and potentially **High — Theft of unclaimed yield** if the over-minted rsETH is redeemed.

### Likelihood Explanation
Arbitrum sequencer outages have occurred historically (e.g., December 2022). The attack requires no special privilege — any user can call `deposit(token, amount, referralId)` on `RSETHPool`. The only precondition is that the sequencer is down and the collateral token's price has moved unfavorably since the last committed oracle update. This is a realistic, externally triggerable condition.

### Recommendation
Add a sequencer uptime check in `ChainlinkOracleForRSETHPoolCollateral.getRate()` following Chainlink's documented pattern:

```solidity
// Chainlink Sequencer Uptime Feed address for Arbitrum
AggregatorV3Interface internal sequencerUptimeFeed;

function getRate() public view returns (uint256) {
    (, int256 answer, uint256 startedAt,,) = sequencerUptimeFeed.latestRoundData();
    // answer == 0: sequencer is up; answer == 1: sequencer is down
    if (answer != 0) revert SequencerDown();
    // Enforce a grace period after sequencer comes back up
    if (block.timestamp - startedAt < GRACE_PERIOD) revert GracePeriodNotOver();

    (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();
    // ... existing checks ...
}
```

Apply the same fix to `ChainlinkPriceOracle.getAssetPrice()`.

### Proof of Concept
1. Arbitrum sequencer goes offline. The last committed wstETH/ETH Chainlink price is `1.15e18` (wstETH = 1.15 ETH).
2. Real market price of wstETH drops to `1.05e18` during the outage.
3. Attacker calls `RSETHPool.deposit(wstETH, 100e18, "")` on Arbitrum.
4. `viewSwapRsETHAmountAndFee(100e18, wstETH)` calls `ChainlinkOracleForRSETHPoolCollateral.getRate()`.
5. `latestRoundData()` returns the stale `1.15e18` price; all three guards (`answeredInRound`, `timestamp`, `ethPrice`) pass.
6. `rsETHAmount = 100e18 * 1.15e18 / rsETHToETHrate` — attacker receives rsETH worth ~1.15 ETH per wstETH deposited, while each wstETH is actually worth only ~1.05 ETH.
7. Attacker gains ~9.5% excess rsETH per deposit, draining the pool's rsETH reserve at the expense of other liquidity providers. [1](#0-0) [5](#0-4)

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

**File:** contracts/pools/RSETHPool.sol (L30-35)
```text
/// @title RSETHPool
/// @notice This contract is the pool contract for the rsETH pool on *Arbitrum*
/// @dev it differs from other RSETHPool contracts in other chains as it uses LZ_RSETH as the canonical rsETH token of
/// the chain.
/// @dev it was the first RSETHPool contract to be deployed in an L2 hence the legacy variables
contract RSETHPool is ERC20Upgradeable, AccessControlUpgradeable, ReentrancyGuardUpgradeable {
```

**File:** contracts/pools/RSETHPool.sol (L326-347)
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
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
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
