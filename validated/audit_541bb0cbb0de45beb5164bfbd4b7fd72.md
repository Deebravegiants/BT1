Audit Report

## Title
Missing Chainlink Heartbeat Staleness Check Enables Stale-Price Over-Minting of wrsETH — (`contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol`)

## Summary

`ChainlinkOracleForRSETHPoolCollateral.getRate()` validates Chainlink data with only a round-completeness check, a zero-timestamp guard, and a non-negative price check. It never compares `block.timestamp - updatedAt` against the feed's heartbeat. When a collateral feed goes silent beyond its heartbeat window, the contract continues returning the last stale price without reverting, allowing any depositor to call `RSETHPoolV3.deposit(token, amount, referralId)` with a stale (potentially inflated) `tokenToETHRate` and receive more `wrsETH` than the deposited collateral is worth at the true market price, extracting value from the protocol's backing.

## Finding Description

**Root cause — `ChainlinkOracleForRSETHPoolCollateral.getRate()` (lines 26–37)** [1](#0-0) 

The function applies three guards:

| Check | What it catches |
|---|---|
| `answeredInRound < roundID` | Round started but not yet answered |
| `timestamp == 0` | Incomplete round |
| `ethPrice <= 0` | Negative/zero price |

**Not present**: `block.timestamp - timestamp > HEARTBEAT` — the guard that detects a feed that has stopped updating. A Chainlink feed satisfies all three existing checks while being hours or days stale: `answeredInRound == roundID`, `timestamp != 0`, and `ethPrice > 0` are all true for the last valid round even if that round closed 30+ hours ago.

**Exploit path through `RSETHPoolV3.deposit(token, amount, referralId)`** [2](#0-1) 

`deposit()` calls `viewSwapRsETHAmountAndFee(amount, token)`: [3](#0-2) 

The minted amount is computed as:

```
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate
```

`tokenToETHRate` is read directly from `IOracle(supportedTokenOracle[token]).getRate()`, which resolves to `ChainlinkOracleForRSETHPoolCollateral.getRate()`. [4](#0-3) 

If the collateral token's market price has fallen since the last oracle update (e.g., stETH drops 2% during a 26-hour feed silence), the stale `tokenToETHRate` is inflated relative to reality. The attacker deposits collateral worth `X` ETH and receives `wrsETH` worth `X + ΔX` ETH. The surplus `ΔX` is extracted from the protocol's backing, diluting all existing `wrsETH` holders. The `limitDailyMint` modifier bounds per-day loss but does not prevent the attack. [5](#0-4) 

## Impact Explanation

An unprivileged attacker mints `wrsETH` tokens whose ETH face value exceeds the ETH-equivalent of the collateral deposited. The shortfall is borne by the protocol's collateral backing, reducing the redemption value for all other `wrsETH` holders. This constitutes **direct theft of funds in-motion** — a Critical impact under the allowed scope. The `dailyMintLimit` caps per-epoch magnitude but does not prevent the attack from being repeated across epochs or across multiple supported tokens sharing the same oracle wrapper pattern.

## Likelihood Explanation

Chainlink feeds occasionally miss their heartbeat during network congestion or keeper outages. The stale window for ETH/USD is 24 h; for LST/ETH feeds it can be 24 h or longer. An attacker monitoring `latestRoundData().updatedAt` on-chain can detect the condition permissionlessly and act within the same block. No privileged role, governance capture, or oracle operator compromise is required — only observation of publicly available on-chain state. The attacker does not need to cause the staleness; they only need to observe it and call `deposit()` during the window.

## Recommendation

Add a configurable `heartbeat` immutable per oracle instance and enforce it in `getRate()`:

```solidity
uint256 public immutable heartbeat; // e.g. 86400 for a 24 h feed

constructor(address _oracle, uint256 _heartbeat) {
    oracle = _oracle;
    heartbeat = _heartbeat;
}

function getRate() public view returns (uint256) {
    (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();

    if (answeredInRound < roundID) revert StalePrice();
    if (timestamp == 0) revert IncompleteRound();
    if (block.timestamp - timestamp > heartbeat) revert StalePrice(); // ← add this
    if (ethPrice <= 0) revert InvalidPrice();

    return uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
}
```

Set `heartbeat` per-feed at construction time (e.g., `86400` for a 24 h feed, `3600` for a 1 h feed).

## Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Fork mainnet at a recent block.
// 1. Deploy MockAggregator returning stalePrice = 1.02e18, staleTs = block.timestamp - 25 hours.
// 2. Deploy ChainlinkOracleForRSETHPoolCollateral pointing at the mock.
// 3. Register it as supportedTokenOracle[stETH] in RSETHPoolV3.
// 4. Call oracle.getRate() — all three existing guards pass, returns 1.02e18.
// 5. Call deposit(stETH, 1e18, "") — observe rsETHAmount_stale.
// 6. Update mock to freshPrice = 1.00e18, ts = block.timestamp.
// 7. Call deposit(stETH, 1e18, "") — observe rsETHAmount_fresh.
// 8. Assert rsETHAmount_stale > rsETHAmount_fresh.
//    Δ ≈ 0.019 rsETH per 1 stETH deposited — extractable value per deposit.

function testStalePriceMint() external {
    uint256 stalePrice = 1.02e18;
    uint256 freshPrice = 1.00e18;
    uint256 staleTs    = block.timestamp - 25 hours;

    MockAggregator agg = new MockAggregator(stalePrice, staleTs);
    ChainlinkOracleForRSETHPoolCollateral oracleContract =
        new ChainlinkOracleForRSETHPoolCollateral(address(agg));

    uint256 rateStale = oracleContract.getRate(); // succeeds — no heartbeat check

    agg.setPrice(freshPrice, block.timestamp);
    uint256 rateFresh = oracleContract.getRate();

    // With rsETHToETHrate = 1.05e18, feeBps = 0:
    uint256 rsETHStale = 1e18 * rateStale / 1.05e18; // ~0.9714 rsETH
    uint256 rsETHFresh = 1e18 * rateFresh / 1.05e18; // ~0.9524 rsETH

    assert(rsETHStale > rsETHFresh); // Δ ≈ 0.019 rsETH extractable per 1 stETH
}
```

The `getRate()` call passes all three existing guards with a 25-hour-old timestamp, confirming the missing heartbeat check is the sole gate that would have blocked the exploit. [6](#0-5)

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
