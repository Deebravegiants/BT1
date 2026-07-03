### Title
Missing L2 Sequencer Uptime Check in Chainlink Oracle Allows Stale-Price Deposits - (`contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol`)

---

### Summary

`ChainlinkOracleForRSETHPoolCollateral.getRate()` calls Chainlink's `latestRoundData()` on L2 without verifying that the L2 sequencer is live. When the sequencer goes offline and resumes, the feed can return the last pre-outage price for a grace period. Any depositor who calls `RSETHPoolV3.deposit()` during this window receives `wrsETH` minted at a stale collateral rate, diluting existing holders.

---

### Finding Description

`ChainlinkOracleForRSETHPoolCollateral` is the oracle adapter used by `RSETHPoolV3` (an L2 pool) to price collateral tokens (e.g., wstETH) against ETH. Its `getRate()` function performs three checks — `answeredInRound < roundID`, `timestamp == 0`, and `ethPrice <= 0` — but none of these detect a sequencer outage:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol
function getRate() public view returns (uint256) {
    (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();

    if (answeredInRound < roundID) revert StalePrice();   // round-completeness only
    if (timestamp == 0) revert IncompleteRound();          // zero-timestamp only
    if (ethPrice <= 0) revert InvalidPrice();

    uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
    return normalizedPrice;
}
```

On L2 networks (Arbitrum, Optimism, Base), Chainlink feeds are updated by the sequencer. When the sequencer is down, the feed freezes at its last value. When the sequencer resumes, there is a grace period before the feed is updated. During this window, `answeredInRound == roundID` (the round is technically complete), `timestamp != 0`, and `ethPrice > 0` — all three checks pass — yet the price is stale.

`RSETHPoolV3.deposit(token, amount, referralId)` calls `viewSwapRsETHAmountAndFee(amount, token)`, which calls `IOracle(supportedTokenOracle[token]).getRate()` to obtain `tokenToETHRate`, then computes:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

A stale `tokenToETHRate` directly controls how many `wrsETH` tokens are minted to the depositor.

---

### Impact Explanation

If the collateral token's real price dropped during the outage (e.g., wstETH/ETH fell), the stale feed still reports the pre-outage higher price. A depositor calling `deposit()` immediately after the sequencer resumes receives more `wrsETH` than the deposited collateral is worth. This over-minting dilutes all existing `wrsETH` holders, constituting theft of yield from existing holders. The inverse (stale price lower than real) causes the depositor to receive fewer tokens, harming the depositor but not the protocol.

**Impact**: Theft of unclaimed yield / share dilution for existing `wrsETH` holders (High).

---

### Likelihood Explanation

L2 sequencer outages are documented and recurring. Arbitrum suffered an hour-long outage in December 2023. The protocol explicitly targets Arbitrum, Optimism, and Base deployments. The attack requires no special privileges — any depositor can call `deposit()` immediately after the sequencer resumes. The attacker can monitor the sequencer status and front-run the oracle update.

**Likelihood**: Medium — outages are infrequent but historically confirmed on the exact chains this protocol targets.

---

### Recommendation

Integrate Chainlink's L2 Sequencer Uptime Feed in `ChainlinkOracleForRSETHPoolCollateral.getRate()`. Revert if the sequencer is down or if the sequencer has been back online for less than a grace period (e.g., 3600 seconds):

```solidity
// Add sequencer feed check
(, int256 answer, uint256 startedAt,,) = sequencerUptimeFeed.latestRoundData();
bool isSequencerDown = answer == 1;
bool isGracePeriodNotOver = block.timestamp - startedAt < GRACE_PERIOD;
if (isSequencerDown || isGracePeriodNotOver) revert SequencerDown();
```

Reference: [Chainlink L2 Sequencer Feeds](https://docs.chain.link/data-feeds/l2-sequencer-feeds).

---

### Proof of Concept

1. `RSETHPoolV3` is deployed on Arbitrum with wstETH as a supported collateral token.
2. `supportedTokenOracle[wstETH]` is set to a `ChainlinkOracleForRSETHPoolCollateral` instance wrapping the wstETH/ETH Chainlink feed.
3. The Arbitrum sequencer goes offline. The wstETH/ETH feed freezes at `1.15e18` (pre-outage value).
4. During the outage, wstETH/ETH real price drops to `1.10e18`.
5. The sequencer resumes. The Chainlink feed still reports `1.15e18` (not yet updated).
6. An attacker calls `RSETHPoolV3.deposit(wstETH, 100e18, "")`.
7. `ChainlinkOracleForRSETHPoolCollateral.getRate()` returns `1.15e18` — all three checks pass.
8. `rsETHAmount = 100e18 * 1.15e18 / rsETHToETHrate` — attacker receives ~4.5% more `wrsETH` than the deposited collateral is worth at current market price.
9. Existing `wrsETH` holders are diluted by the over-minted supply.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2)

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
