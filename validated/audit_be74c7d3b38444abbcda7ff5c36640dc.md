Audit Report

## Title
Missing Chainlink Heartbeat Staleness Check Enables Excess wrsETH Minting — (`contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol`)

## Summary

`ChainlinkOracleForRSETHPoolCollateral.getRate()` performs only three validity checks on Chainlink round data and omits the standard `block.timestamp - updatedAt > heartbeat` guard. A feed that has not been updated beyond its heartbeat window but still satisfies all three existing checks will return a stale price. When this oracle is assigned as `supportedTokenOracle[token]` in either pool contract, any unprivileged caller can deposit collateral and receive excess wrsETH, which can be unwrapped to extract rsETH backed by yield accrued by existing holders.

## Finding Description

`getRate()` in `ChainlinkOracleForRSETHPoolCollateral` performs exactly three checks:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0)            revert IncompleteRound();
if (ethPrice <= 0)             revert InvalidPrice();
``` [1](#0-0) 

None of these verify `block.timestamp - updatedAt <= heartbeat`. A feed last updated 25+ hours ago (past a 24 h heartbeat) will pass all three conditions and return the stale price. [2](#0-1) 

This oracle is consumed by `RSETHPoolV3.viewSwapRsETHAmountAndFee(amount, token)`:

```solidity
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [3](#0-2) 

The identical pattern exists in `RSETHPoolV3WithNativeChainBridge.viewSwapRsETHAmountAndFee`: [4](#0-3) 

If `tokenToETHRate` is stale and inflated relative to the true current price, `rsETHAmount` is over-computed and `wrsETH.mint(msg.sender, rsETHAmount)` mints excess tokens: [5](#0-4) 

The `limitDailyMint` modifier calls the same `viewSwapRsETHAmountAndFee` with the same stale oracle, so it only caps the total inflated amount — it does not prevent the over-mint per unit of collateral: [6](#0-5) 

## Impact Explanation

The excess wrsETH minted represents a claim on more rsETH than the deposited collateral is worth at the true current price. When the attacker unwraps wrsETH → rsETH, they extract rsETH that was backed by restaking yield accrued by existing holders, diluting the rsETH/ETH rate for all existing wrsETH/rsETH holders. This constitutes **theft of unclaimed yield** (High severity), a concrete allowed impact in the program scope.

## Likelihood Explanation

Chainlink feeds go stale in practice during periods of low price volatility combined with network congestion or node issues that delay the heartbeat update. The stETH/ETH feed has a 24 h heartbeat and a 0.5% deviation threshold; during stable periods it can approach the heartbeat boundary without triggering a deviation update. No privileged access is required — any EOA can call `deposit(token, amount, referralId)` on a non-paused pool with a supported token. The attack is repeatable every time the feed is stale and the stale price is inflated relative to the true current price.

## Recommendation

Add a `heartbeat` immutable to `ChainlinkOracleForRSETHPoolCollateral` and enforce it in `getRate()`:

```solidity
uint256 public immutable heartbeat;

constructor(address _oracle, uint256 _heartbeat) {
    oracle    = _oracle;
    heartbeat = _heartbeat;
}

function getRate() public view returns (uint256) {
    (uint80 roundID, int256 ethPrice,, uint256 updatedAt, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();

    if (answeredInRound < roundID)               revert StalePrice();
    if (updatedAt == 0)                          revert IncompleteRound();
    if (block.timestamp - updatedAt > heartbeat) revert StalePrice();   // ← add this
    if (ethPrice <= 0)                           revert InvalidPrice();

    return uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
}
```

## Proof of Concept

Deploy `ChainlinkOracleForRSETHPoolCollateral` against a mock aggregator that returns `updatedAt = block.timestamp - 25 hours` with `answeredInRound == roundID` and `answer = 0.9999e18`. Call `getRate()` — it returns the 25-hour-old price without reverting, confirming the missing guard.

```solidity
contract MockStaleAggregator {
    function decimals() external pure returns (uint8) { return 18; }
    function latestRoundData() external view
        returns (uint80 roundId, int256 answer, uint256 startedAt,
                 uint256 updatedAt, uint80 answeredInRound)
    {
        roundId         = 1;
        answeredInRound = 1;
        answer          = 0.9999e18;
        updatedAt       = block.timestamp - 25 hours;
        startedAt       = updatedAt;
    }
}

function test_staleOracleAccepted() public {
    MockStaleAggregator agg = new MockStaleAggregator();
    ChainlinkOracleForRSETHPoolCollateral oracle =
        new ChainlinkOracleForRSETHPoolCollateral(address(agg));
    uint256 rate = oracle.getRate(); // succeeds — no revert
    assertEq(rate, 0.9999e18);
}
```

In a full fork test, assigning this oracle as `supportedTokenOracle[stETH]` and calling `RSETHPoolV3.deposit(stETH, largeAmount, "")` would mint measurably more wrsETH than the fair-value baseline computed against the live price.

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

**File:** contracts/pools/RSETHPoolV3.sol (L96-125)
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
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L286-290)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolV3.sol (L331-334)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L367-370)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```
