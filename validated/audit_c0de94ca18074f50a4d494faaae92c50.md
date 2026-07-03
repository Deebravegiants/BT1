### Title
Missing Time-Based Staleness Check in ChainlinkOracleForRSETHPoolCollateral Enables Over-Minting and Daily Limit DoS - (File: contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol)

### Summary

`ChainlinkOracleForRSETHPoolCollateral.getRate()` performs only a round-completeness staleness check (`answeredInRound < roundID`) but omits a time-based heartbeat check (`block.timestamp - updatedAt > MAX_STALENESS`). When the Chainlink feed goes stale at a previously-high price, any caller depositing a supported collateral token receives rsETH computed against the inflated rate, simultaneously exhausting the `dailyMintLimit` and extracting excess rsETH from the protocol.

### Finding Description

`ChainlinkOracleForRSETHPoolCollateral.getRate()` reads `latestRoundData` and validates:

```
if (answeredInRound < roundID) revert StalePrice();   // round-based only
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [1](#0-0) 

The `updatedAt` field is captured but never compared against `block.timestamp`. If the Chainlink node stops publishing (network congestion, downtime, or a price that hasn't moved enough to trigger a deviation update), the same round remains open (`answeredInRound == roundID`), so the round-based check passes, and the stale price is returned as valid.

This oracle is used as the `tokenToETHRate` in `viewSwapRsETHAmountAndFee(amount, token)`:

```solidity
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [2](#0-1) 

The same `rsETHAmount` is computed inside `limitDailyMint` before the deposit executes:

```solidity
(rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
...
if (dailyMintAmount + rsETHAmount > dailyMintLimit) revert DailyMintLimitExceeded();
dailyMintAmount += rsETHAmount;
``` [3](#0-2) 

And then again inside the deposit body:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
...
wrsETH.mint(msg.sender, rsETHAmount);
``` [4](#0-3) 

Because both the limit check and the actual mint use the same inflated `tokenToETHRate`, the attacker receives the excess rsETH and simultaneously burns through the daily cap.

The same pattern is present in every pool variant that accepts collateral tokens: `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPool`, and `RSETHPoolNoWrapper`. [5](#0-4) 

### Impact Explanation

**Direct theft (Critical):** The attacker deposits tokens whose true ETH value is X but whose stale oracle value is 2X. The pool mints rsETH worth 2X ETH against collateral worth only X ETH. The attacker can redeem or sell the excess rsETH, extracting real value from the protocol's backing. Existing rsETH holders are diluted; the protocol becomes undercollateralised by the difference.

**Temporary DoS (Medium, secondary):** The inflated `rsETHAmount` counted against `dailyMintAmount` exhausts `dailyMintLimit` in a single deposit, blocking all other users from depositing for the remainder of the day.

### Likelihood Explanation

Chainlink feeds can go stale without oracle-operator compromise: network congestion, L2 sequencer issues, or a price that has not moved beyond the deviation threshold can all leave `updatedAt` hours behind `block.timestamp` while `answeredInRound == roundID`. This is a well-documented failure mode. The attacker needs only to monitor the feed's `updatedAt` lag and submit a deposit when the stale price is sufficiently above the true market price.

### Recommendation

Add a configurable heartbeat/staleness check in `getRate()`:

```solidity
uint256 public constant MAX_STALENESS = 3600; // set per feed

function getRate() public view returns (uint256) {
    (uint80 roundID, int256 ethPrice,, uint256 updatedAt, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();

    if (answeredInRound < roundID) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();
    if (ethPrice <= 0) revert InvalidPrice();

    return uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
}
``` [6](#0-5) 

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Setup (local fork or Foundry test):
// 1. Deploy a mock Chainlink aggregator that returns:
//    roundId=1, answer=2e18 (2 ETH per token), updatedAt=block.timestamp - 7200
//    answeredInRound=1  (so answeredInRound == roundID → passes stale check)
// 2. Deploy ChainlinkOracleForRSETHPoolCollateral pointing at mock aggregator.
// 3. Deploy RSETHPoolV3 with:
//    - rsETHOracle returning 1e18 (1:1 rsETH/ETH)
//    - collateral token oracle = ChainlinkOracleForRSETHPoolCollateral above
//    - dailyMintLimit = 1000e18
// 4. Attacker holds 500 collateral tokens (true value: 500 ETH, stale oracle: 1000 ETH).

// Attack:
// attacker.deposit(token, 500e18, "");
// → viewSwapRsETHAmountAndFee returns rsETHAmount ≈ 1000e18 (2x true)
// → limitDailyMint: dailyMintAmount += 1000e18 → equals dailyMintLimit → cap exhausted
// → wrsETH.mint(attacker, 1000e18)   ← attacker receives 2x expected rsETH

// Assertions:
// assert(pool.dailyMintAmount() == 1000e18);          // cap fully consumed
// assert(wrsETH.balanceOf(attacker) == 1000e18);      // 2x true value received
// assert(pool.remainingDailyMintLimit() == 0);        // all other users blocked
// Any subsequent deposit by another user → DailyMintLimitExceeded revert
```

The `answeredInRound < roundID` guard does not fire because the mock keeps `answeredInRound == roundID`. The missing `block.timestamp - updatedAt > heartbeat` check is the sole gate that would have rejected the stale price. [6](#0-5) [7](#0-6) [8](#0-7)

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

**File:** contracts/pools/RSETHPoolV3.sol (L96-124)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
```

**File:** contracts/pools/RSETHPoolV3.sol (L280-292)
```text
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
```

**File:** contracts/pools/RSETHPoolV3.sol (L331-334)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L448-452)
```text
        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```
