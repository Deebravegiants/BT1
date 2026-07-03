### Title
Chainlink Oracle Missing L2 Sequencer Uptime Check Allows Stale Price Exploitation During Sequencer Downtime - (File: contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol)

---

### Summary

`ChainlinkOracleForRSETHPoolCollateral.getRate()` calls Chainlink's `latestRoundData()` without verifying whether the L2 sequencer is operational. When the sequencer is down, Chainlink feeds on L2 return stale prices that pass all existing validity checks. This allows a depositor to interact with `RSETHPoolV3` (and related pool contracts) using incorrect token-to-ETH rates, resulting in over-minting of `wrsETH` at the expense of other pool participants.

---

### Finding Description

`ChainlinkOracleForRSETHPoolCollateral.getRate()` fetches the price from a Chainlink aggregator: [1](#0-0) 

The function performs three validity checks — `answeredInRound < roundID`, `timestamp == 0`, and `ethPrice <= 0` — but **none of these detect a sequencer outage**. When an L2 sequencer (Arbitrum, Base, Optimism, Scroll, Linea, zkSync) goes offline, Chainlink's L2 data feeds stop updating but continue to serve the last known price. That price satisfies `answeredInRound == roundID`, `timestamp != 0`, and `ethPrice > 0`, so all three guards pass silently.

No sequencer uptime feed is consulted anywhere in the codebase: [2](#0-1) 

This oracle is wired into `RSETHPoolV3` as the per-token collateral rate source: [3](#0-2) 

The stale `tokenToETHRate` is then used directly to compute how many `wrsETH` tokens to mint for a depositor: [4](#0-3) 

---

### Impact Explanation

**Impact: Critical — Direct theft of user funds.**

If the sequencer goes down while a supported collateral token's market price drops significantly, the oracle continues to report the pre-outage (inflated) price. A depositor who calls `deposit(token, amount, referralId)` during or immediately after the outage (before the feed updates) receives `wrsETH` calculated against the stale high price, obtaining more `wrsETH` than the deposited tokens are actually worth. The excess `wrsETH` is redeemable against the pool's real ETH/token reserves, effectively draining value from other depositors. [5](#0-4) 

---

### Likelihood Explanation

**Likelihood: Medium.**

L2 sequencer outages are documented historical events on Arbitrum, Optimism, and Base. The protocol explicitly deploys pool contracts on these chains (Arbitrum, Base, Scroll, Optimism, Linea, zkSync per the README). An attacker monitoring sequencer status can time a deposit to exploit the stale feed window. No privileged access is required; the `deposit` function is fully public. [5](#0-4) 

---

### Recommendation

Follow Chainlink's official L2 sequencer uptime pattern inside `ChainlinkOracleForRSETHPoolCollateral.getRate()`:

```solidity
// Add sequencer uptime feed check
AggregatorV3Interface sequencerUptimeFeed = AggregatorV3Interface(SEQUENCER_UPTIME_FEED);
(, int256 answer, uint256 startedAt,,) = sequencerUptimeFeed.latestRoundData();
if (answer != 0) revert SequencerDown();
if (block.timestamp - startedAt < GRACE_PERIOD) revert GracePeriodNotOver();
```

The sequencer uptime feed address and grace period (typically 3600 seconds) should be set per-chain at deployment time. [1](#0-0) 

---

### Proof of Concept

1. Sequencer on Arbitrum goes offline. The Chainlink ETH/USD (or WBTC/ETH, etc.) feed freezes at the last reported price, e.g., `tokenPrice = 3000e8` (USD).
2. Market price of the collateral token drops to `2000e8` during the outage.
3. Sequencer comes back online. For a brief window, `latestRoundData()` still returns `3000e8` (stale).
4. Attacker calls `RSETHPoolV3.deposit(token, 1e18, "")`.
5. `viewSwapRsETHAmountAndFee(1e18, token)` fetches `tokenToETHRate` via `ChainlinkOracleForRSETHPoolCollateral.getRate()` → returns stale `3000e8`-equivalent rate.
6. `rsETHAmount = amountAfterFee * 3000_rate / rsETHToETHrate` — attacker receives ~50% more `wrsETH` than fair value.
7. Attacker redeems `wrsETH` via `swapAssetToPremintedRsETH` or bridges back, extracting real ETH/tokens from the pool at the expense of honest depositors. [1](#0-0) [4](#0-3)

### Citations

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L1-42)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.27;

interface AggregatorV3Interface {
    function decimals() external view returns (uint8);

    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

/// @title ChainlinkOracleForRSETHPoolCollateral Contract
/// @notice Wrapper contract for Chainlink oracles
contract ChainlinkOracleForRSETHPoolCollateral {
    address public immutable oracle;

    error StalePrice();
    error IncompleteRound();
    error InvalidPrice();

    constructor(address _oracle) {
        oracle = _oracle;
    }

    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
    }

    function rate() external view returns (uint256) {
        return getRate();
    }
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
