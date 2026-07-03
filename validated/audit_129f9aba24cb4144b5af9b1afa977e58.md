Audit Report

## Title
Missing Chainlink Staleness Threshold Enables wrsETH Over-Issuance — (`contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol`)

## Summary
`ChainlinkOracleForRSETHPoolCollateral.getRate()` performs no wall-clock staleness check on the Chainlink response. When the feed stops updating (keeper failure, L2 sequencer downtime, network congestion), the frozen, lower-than-current rsETH/ETH rate is accepted as valid, causing `RSETHPoolV2NBA.deposit()` to mint more wrsETH than the deposited ETH is worth. Because there is no mint cap, the insolvency gap scales unboundedly with deposit volume during the stale window.

## Finding Description
`getRate()` in `ChainlinkOracleForRSETHPoolCollateral.sol` (L26–37) calls `latestRoundData()` and applies only two guards:

```solidity
if (answeredInRound < roundID) revert StalePrice();   // round completeness only
if (timestamp == 0) revert IncompleteRound();          // non-zero timestamp only
```

Neither guard bounds how old `updatedAt` may be relative to `block.timestamp`. A feed that last updated 48 hours ago passes both checks as long as `answeredInRound >= roundID` and `timestamp != 0`.

`RSETHPoolV2NBA.deposit()` (L106–118) calls `viewSwapRsETHAmountAndFee()` (L124–133), which calls `getRate()` and uses the result directly:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

Then immediately mints with no supply ceiling:

```solidity
wrsETH.mint(msg.sender, rsETHAmount);
```

rsETH accrues staking rewards monotonically, so its ETH-denominated rate rises over time. A stale oracle frozen at a lower rate (e.g., 1.00 ETH/rsETH when the true rate is 1.05 ETH/rsETH) causes the division to yield a larger `rsETHAmount` than is backed by the deposited ETH. Every depositor during the stale window receives surplus, unbacked wrsETH. [1](#0-0) [2](#0-1) [3](#0-2) 

## Impact Explanation
**Critical — Protocol insolvency.** Over-issued wrsETH tokens represent claims on rsETH that the pool cannot satisfy on redemption. The gap is proportional to both the rate drift and the deposit volume during the stale window, and is unbounded because `wrsETH.mint` has no supply ceiling. This directly matches the allowed Critical impact class "Protocol insolvency."

## Likelihood Explanation
Chainlink feed staleness is a documented, non-adversarial operational risk (keeper failures, L2 sequencer downtime, network congestion). It does not require oracle operator compromise or any privileged action. Any unprivileged depositor calling `deposit()` during a stale window triggers the over-issuance automatically. The condition is repeatable across all depositors for the entire duration of the stale period.

## Recommendation
Add a configurable `MAX_STALENESS` constant and enforce it in `getRate()`:

```solidity
uint256 public constant MAX_STALENESS = 3600; // adjust per feed heartbeat

function getRate() public view returns (uint256) {
    (uint80 roundID, int256 ethPrice,, uint256 updatedAt, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();

    if (answeredInRound < roundID) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();
    if (ethPrice <= 0) revert InvalidPrice();

    return uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
}
``` [4](#0-3) 

## Proof of Concept
```solidity
// Fork mainnet at block B where rsETH oracle updatedAt == block.timestamp, rate = 1.00e18
vm.warp(block.timestamp + 48 hours);
// Feed is stale: answeredInRound >= roundID and timestamp != 0 still hold
// True rsETH rate is now ~1.04e18 (2 days of ~2% APY)

uint256 deposit = 100 ether;
pool.deposit{value: deposit}("");

// Minted:  100e18 * 1e18 / 1.00e18 = 100 wrsETH
// Correct: 100e18 * 1e18 / 1.04e18 ≈ 96.15 wrsETH
// Insolvency gap: ~3.85 wrsETH per 100 ETH, unbounded across all depositors
assertGt(wrsETH.balanceOf(address(this)), 96.15 ether);
``` [5](#0-4)

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

**File:** contracts/pools/RSETHPoolV2NBA.sol (L106-118)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L124-133)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```
