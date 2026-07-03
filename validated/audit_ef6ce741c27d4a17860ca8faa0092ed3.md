Audit Report

## Title
Missing Chainlink heartbeat staleness check enables deposits at stale collateral prices — (File: `contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol`)

## Summary
`ChainlinkOracleForRSETHPoolCollateral.getRate()` validates only round-completeness and sign of the price, but omits a `block.timestamp - updatedAt > heartbeat` guard. When a Chainlink collateral feed goes stale within its heartbeat window (e.g., 24 h for LST/ETH feeds), any unprivileged caller can deposit the overvalued collateral token into `RSETHPoolV3`, `RSETHPool`, or `RSETHPoolNoWrapper` and receive more rsETH/wrsETH than the collateral is worth, extracting value from existing rsETH holders.

## Finding Description
`getRate()` calls `latestRoundData()` and applies three guards:

```solidity
if (answeredInRound < roundID) revert StalePrice();   // round-based only
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [1](#0-0) 

There is no check of the form `block.timestamp - timestamp > heartbeat`. Chainlink feeds update on either a price-deviation threshold or a heartbeat interval. If the real price has not moved enough to trigger a deviation update, the feed can remain at an old value for the full heartbeat window while `answeredInRound == roundID`, so the round-based check passes silently.

The stale rate is consumed directly in all three pool deposit paths:

```solidity
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate(); // stale
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [2](#0-1) [3](#0-2) [4](#0-3) 

In `RSETHPoolV3`, the inflated `rsETHAmount` is passed directly to `wrsETH.mint()`, creating unbacked wrsETH: [5](#0-4) 

In `RSETHPool` and `RSETHPoolNoWrapper`, the pool transfers pre-minted rsETH from its own inventory at the inflated rate, depleting the pool faster than the ETH value received: [6](#0-5) [7](#0-6) 

## Impact Explanation
**High — Theft of unclaimed yield / dilution of existing rsETH holders.**

In `RSETHPoolV3`, newly minted wrsETH is not fully backed by the deposited collateral, diluting all existing rsETH/wrsETH holders proportionally. In `RSETHPool` and `RSETHPoolNoWrapper`, the pool's pre-minted rsETH inventory is depleted faster than the ETH value received, creating a shortfall that must be covered by the protocol. Both outcomes match the allowed impact "High — Theft of unclaimed yield." No privileged access is required; the `deposit(address,uint256,string)` function is public and callable by any address. [8](#0-7) 

## Likelihood Explanation
**Medium.** Chainlink heartbeats for LST/ETH feeds are commonly 24 hours. During periods of market stress — exactly when prices move most — network congestion can delay oracle updates. An attacker monitoring the feed can identify the staleness window and act within it. No privileged access, governance action, or victim mistake is required; any EOA can call `deposit()` on any of the three L2 pools.

## Recommendation
Add a configurable per-feed heartbeat parameter to `ChainlinkOracleForRSETHPoolCollateral` and enforce it in `getRate()`:

```solidity
uint256 public immutable heartbeat; // e.g. 86400 for 24 h

constructor(address _oracle, uint256 _heartbeat) {
    oracle = _oracle;
    heartbeat = _heartbeat;
}

function getRate() public view returns (uint256) {
    (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();

    if (answeredInRound < roundID) revert StalePrice();
    if (timestamp == 0) revert IncompleteRound();
    if (block.timestamp - timestamp > heartbeat) revert StalePrice(); // ADD
    if (ethPrice <= 0) revert InvalidPrice();

    return uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
}
``` [9](#0-8) 

## Proof of Concept
1. `ChainlinkOracleForRSETHPoolCollateral` is deployed for a wstETH/ETH feed with a 24-hour heartbeat.
2. At `T = 0` the feed records `wstETH/ETH = 1.10`; `answeredInRound == roundID`.
3. At `T = 20 h` the real market price drops to `wstETH/ETH = 1.00` (depeg event), but the price deviation is below the Chainlink threshold so no new round is published. The round-based check still passes.
4. Attacker calls `RSETHPoolV3.deposit(wstETH, 1000e18, "")`.
5. `viewSwapRsETHAmountAndFee` computes `tokenToETHRate = 1.10e18` (stale), `rsETHToETHrate = 1.05e18` (current rsETH price).
6. Attacker receives `1000 × 1.10 / 1.05 ≈ 1047 wrsETH` instead of the fair `1000 × 1.00 / 1.05 ≈ 952 wrsETH`.
7. Attacker redeems wrsETH for ~1047 ETH worth of value having deposited only ~1000 ETH worth of wstETH — approximately 47 ETH extracted from existing rsETH holders with no privileged access required.

**Foundry fork test plan:** Fork the target L2 at a block where the wstETH/ETH Chainlink feed's `updatedAt` is within the heartbeat but the real price has moved. Call `deposit(wstETH, amount, "")` and assert that the returned `rsETHAmount` exceeds `amount * realPrice / rsETHToETHrate`, confirming the over-issuance. [1](#0-0)

### Citations

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L22-37)
```text
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

**File:** contracts/pools/RSETHPoolV3.sol (L331-334)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPool.sol (L296-302)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPool.sol (L343-346)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L260-268)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L308-311)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```
