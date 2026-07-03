### Title
Missing Sequencer Uptime and Price Staleness Checks Allow Stale-Rate Deposits During L2 Sequencer Downtime - (File: contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol)

---

### Summary

`ChainlinkOracleForRSETHPoolCollateral.getRate()` is used by all L2 pool contracts to price collateral tokens. It calls Chainlink's `latestRoundData()` but performs no sequencer uptime feed check and no `updatedAt` heartbeat staleness check. During L2 sequencer downtime, Chainlink oracles freeze at their last reported price. When the sequencer recovers, the oracle still returns the pre-downtime stale price until a new round is pushed. A user can then deposit collateral at the stale (inflated) rate and receive more rsETH/wrsETH than the token is currently worth, draining the pool's pre-minted rsETH reserves.

---

### Finding Description

`ChainlinkOracleForRSETHPoolCollateral` is the oracle wrapper used as `supportedTokenOracle[token]` in every L2 pool variant (`RSETHPool`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`). Its `getRate()` function:

```solidity
function getRate() public view returns (uint256) {
    (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();

    if (answeredInRound < roundID) revert StalePrice();
    if (timestamp == 0) revert IncompleteRound();
    if (ethPrice <= 0) revert InvalidPrice();
    ...
}
```

Two critical protections are absent:

1. **No Chainlink sequencer uptime feed check.** Chainlink's own documentation requires L2 deployments to check the sequencer uptime feed (e.g., `ArbitrumSequencerUptimeFeed`) before trusting `latestRoundData()`. When the sequencer is down, Chainlink oracles on L2 stop updating but continue returning the last known answer without reverting.

2. **No `updatedAt` heartbeat staleness check.** The only staleness guard is `answeredInRound < roundID`, which Chainlink has deprecated. This check passes for the last valid round (`answeredInRound == roundID`) even if that round is hours or days old. The correct check is `block.timestamp - updatedAt > heartbeat`.

The stale rate flows directly into the deposit swap calculation in every L2 pool:

```solidity
// RSETHPool.viewSwapRsETHAmountAndFee (token path)
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate(); // stale rate
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

The pool transfers pre-minted rsETH/wrsETH to the depositor at this stale rate, then bridges the received token to L1. If the token's true market price has fallen below the stale price, the pool has given out more rsETH than the deposited token is worth.

---

### Impact Explanation

**High — Theft of unclaimed yield / direct loss to pool reserves.**

If a collateral token (e.g., wstETH) drops in price during sequencer downtime, an attacker who deposits immediately after sequencer recovery receives rsETH calculated at the pre-drop (stale) price. The pool bridges the undervalued token to L1 but has already disbursed excess rsETH. The pool's pre-minted rsETH reserves are depleted faster than they are replenished, causing a direct loss to the protocol and honest depositors. The magnitude scales with the price drop and the amount deposited.

---

### Likelihood Explanation

**Low.** L2 sequencer downtime is rare but has occurred historically on Arbitrum and Optimism. The attack requires the sequencer to be down long enough for a meaningful price move in a supported collateral token, and the attacker must act quickly after recovery before the oracle updates. The window is narrow but exploitable by a prepared attacker monitoring the sequencer status feed.

---

### Recommendation

1. **Add a sequencer uptime check** using the appropriate Chainlink sequencer uptime feed for each L2 (e.g., `0xFdB631F5EE196F0ed6FAa767959853A9F217697D` on Arbitrum). Revert if the sequencer is down or was recently restarted (grace period of ~60 seconds after recovery).

2. **Add a heartbeat staleness check**: `if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();` where `MAX_STALENESS` is set per feed (e.g., 3600 seconds for a 1-hour heartbeat feed).

---

### Proof of Concept

1. wstETH/ETH Chainlink price on Arbitrum is `1.20e18` (last updated at T=0).
2. L2 sequencer goes offline at T=100.
3. wstETH/ETH price drops to `1.00e18` on L1 at T=200 (Chainlink L2 oracle freezes at `1.20e18`).
4. Sequencer recovers at T=3600. Chainlink L2 oracle still returns `1.20e18` (`answeredInRound == roundID`, `timestamp != 0` — both checks pass).
5. Attacker calls `deposit(wstETH, 100e18, "")` on `RSETHPool` (or any L2 pool variant).
6. `viewSwapRsETHAmountAndFee(100e18, wstETH)` calls `IOracle(supportedTokenOracle[wstETH]).getRate()` → returns `1.20e18` (stale).
7. `rsETHAmount = 100e18 * 1.20e18 / rsETHToETHrate` — attacker receives rsETH valued at 120 ETH worth of wstETH, but only deposited 100 ETH worth.
8. Pool bridges 100 wstETH (worth 100 ETH) to L1 but has disbursed rsETH worth 120 ETH.
9. Pool incurs a 20 ETH loss per 100 wstETH deposited.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/pools/RSETHPool.sol (L340-347)
```text
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L315-332)
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

```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L433-453)
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
