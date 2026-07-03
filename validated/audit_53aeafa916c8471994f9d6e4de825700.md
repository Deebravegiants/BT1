### Title
Missing L2 Sequencer Uptime and Time-Based Staleness Check Allows Stale Price Exploitation After Sequencer Recovery - (File: contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol)

### Summary
`ChainlinkOracleForRSETHPoolCollateral.getRate()` contains no L2 sequencer uptime feed check and no time-based heartbeat staleness check. After an L2 sequencer outage, stale pre-outage collateral token prices are accepted as valid, allowing depositors to mint wrsETH at incorrect rates and diluting existing rsETH holders.

### Finding Description
`ChainlinkOracleForRSETHPoolCollateral` is the Chainlink wrapper oracle used by L2 pool contracts (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) to price supported collateral tokens (e.g., wstETH) during deposits. [1](#0-0) 

The `getRate()` function calls `latestRoundData()` and performs only two checks:
- `answeredInRound < roundID` — detects an incomplete round
- `timestamp == 0` — detects a missing timestamp

It performs **no check** against a Chainlink L2 sequencer uptime feed, and **no time-based staleness check** (i.e., no comparison of `updatedAt` against a heartbeat threshold). This means a price that was last updated hours before the sequencer went down is accepted as fresh. [2](#0-1) 

This oracle is wired into the L2 pool deposit path: [3](#0-2) 

`viewSwapRsETHAmountAndFee` uses `tokenToETHRate` from this oracle to compute how many wrsETH tokens to mint: [4](#0-3) 

The same pattern exists in `RSETHPoolV3ExternalBridge` and `RSETHPoolV3WithNativeChainBridge`: [5](#0-4) 

### Impact Explanation
When the L2 sequencer (e.g., Arbitrum) recovers from downtime, Chainlink price updates that accumulated during the outage are applied rapidly. However, `latestRoundData()` may still return the pre-outage price for a brief window. Because `getRate()` has no sequencer uptime check and no heartbeat staleness check, this stale price is accepted.

If a collateral token's price dropped during the outage (e.g., wstETH fell 5%), a depositor calling `deposit(token, amount, referralId)` immediately after sequencer recovery receives wrsETH calculated at the old (higher) `tokenToETHRate`. This results in over-minting of wrsETH relative to the actual collateral value, diluting all existing rsETH/wrsETH holders. This constitutes **theft of unclaimed yield** from existing holders (High impact).

### Likelihood Explanation
Arbitrum sequencer outages have occurred historically. The protocol explicitly deploys on Arbitrum and other L2s. Any sequencer downtime event during which collateral token prices move meaningfully creates this window. No special permissions or attacker setup are required — any user calling `deposit()` immediately after sequencer recovery triggers the issue.

### Recommendation
Add a Chainlink L2 sequencer uptime feed check and a time-based staleness check to `ChainlinkOracleForRSETHPoolCollateral.getRate()`:

```solidity
// Add sequencer uptime feed address as immutable
address public immutable sequencerUptimeFeed;
uint256 public constant GRACE_PERIOD = 3600; // 1 hour
uint256 public constant HEARTBEAT = 3600;    // configure per feed

function getRate() public view returns (uint256) {
    // 1. Sequencer uptime check
    if (sequencerUptimeFeed != address(0)) {
        (, int256 seqAnswer, uint256 startedAt,,) =
            AggregatorV3Interface(sequencerUptimeFeed).latestRoundData();
        if (seqAnswer != 0) revert SequencerDown();
        if (block.timestamp - startedAt <= GRACE_PERIOD) revert GracePeriodNotOver();
    }

    (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();

    if (answeredInRound < roundID) revert StalePrice();
    if (timestamp == 0) revert IncompleteRound();
    if (ethPrice <= 0) revert InvalidPrice();
    // 2. Time-based staleness check
    if (block.timestamp - timestamp > HEARTBEAT) revert StalePrice();

    return uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
}
```

### Proof of Concept
1. Arbitrum sequencer goes offline. wstETH price is 1.2 ETH at time of outage.
2. During outage, wstETH price drops to 1.1 ETH on mainnet.
3. Sequencer recovers. Chainlink has not yet pushed the updated price to Arbitrum.
4. Attacker calls `RSETHPoolV3.deposit(wstETH, 100e18, "")`.
5. `ChainlinkOracleForRSETHPoolCollateral.getRate()` returns the stale 1.2 ETH rate (passes both existing checks since `answeredInRound == roundID` and `timestamp != 0`).
6. `viewSwapRsETHAmountAndFee` computes `rsETHAmount = 100e18 * 1.2e18 / rsETHToETHrate` — attacker receives wrsETH valued at 1.2 ETH/wstETH instead of 1.1 ETH/wstETH.
7. Attacker has extracted ~9% excess wrsETH relative to actual collateral value, diluting all existing holders. [1](#0-0) [6](#0-5)

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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L442-453)
```text
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
