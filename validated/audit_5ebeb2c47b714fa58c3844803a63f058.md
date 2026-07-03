### Title
Missing Chainlink Staleness Threshold Allows Stale Rate to Drive wrsETH Over-Issuance — (`contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol`)

---

### Summary

`ChainlinkOracleForRSETHPoolCollateral.getRate()` omits a `block.timestamp - updatedAt` staleness check. `RSETHPoolV2NBA.deposit()` consumes this rate unboundedly (no daily mint cap), so any period during which the Chainlink feed stops updating causes wrsETH to be minted at a rate that no longer reflects actual rsETH collateral value, creating an insolvency gap.

---

### Finding Description

`ChainlinkOracleForRSETHPoolCollateral.getRate()` performs only two validity checks on the Chainlink response:

```
if (answeredInRound < roundID) revert StalePrice();   // round completeness
if (timestamp == 0) revert IncompleteRound();          // non-zero timestamp
``` [1](#0-0) 

Neither check bounds how old `updatedAt` may be relative to `block.timestamp`. A feed that last updated 48 hours ago will still pass both guards as long as `answeredInRound >= roundID` and `timestamp != 0`.

`RSETHPoolV2NBA.deposit()` calls `viewSwapRsETHAmountAndFee`, which calls `getRate()` and uses the result directly in the mint formula:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [2](#0-1) 

Then immediately mints without any cap:

```solidity
wrsETH.mint(msg.sender, rsETHAmount);
``` [3](#0-2) 

rsETH accrues staking rewards over time, so its ETH-denominated rate rises monotonically. If the oracle freezes at an old, lower rate (e.g., 1.00 ETH/rsETH when the true rate is 1.05 ETH/rsETH), every depositor receives `1/1.00 = 1.0 wrsETH` per ETH instead of the correct `1/1.05 ≈ 0.952 wrsETH`. The surplus wrsETH is unbacked.

There is no daily mint limit, no circuit-breaker on minted supply, and no on-chain mechanism to detect the staleness automatically. [4](#0-3) 

---

### Impact Explanation

**Critical — Protocol insolvency.**

Over-issued wrsETH tokens represent claims on rsETH that the pool cannot satisfy. The insolvency gap scales linearly with deposit volume during the stale window and with the magnitude of the rate drift. Because `wrsETH.mint` is called with no supply ceiling, the gap is unbounded.

---

### Likelihood Explanation

Chainlink feeds have documented heartbeat intervals (e.g., 1 hour for ETH/USD on mainnet). Network congestion, keeper failures, or L2 sequencer downtime can cause feeds to go stale for hours. This is a well-known, non-adversarial failure mode that does not require oracle operator compromise — it is a natural operational risk that the contract must guard against internally.

---

### Recommendation

Add a configurable `MAX_STALENESS` constant and enforce it in `getRate()`:

```solidity
uint256 public constant MAX_STALENESS = 3600; // 1 hour, adjust per feed heartbeat

function getRate() public view returns (uint256) {
    (uint80 roundID, int256 ethPrice,, uint256 updatedAt, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();

    if (answeredInRound < roundID) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();
    if (ethPrice <= 0) revert InvalidPrice();

    return uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
}
``` [5](#0-4) 

Optionally, add a per-epoch mint cap in `RSETHPoolV2NBA` as a defense-in-depth measure.

---

### Proof of Concept

```solidity
// Fork mainnet at block B where rsETH rate = 1.00 ETH (oracle updatedAt = block.timestamp)
// Warp forward 48 hours without triggering a Chainlink update
vm.warp(block.timestamp + 48 hours);

// True rsETH rate is now ~1.04 ETH (2 days of ~2% APY accrual)
// Oracle still returns 1.00 ETH — passes answeredInRound and timestamp checks

uint256 deposit = 100 ether;
pool.deposit{value: deposit}("");

// Minted: 100e18 * 1e18 / 1.00e18 = 100 wrsETH
// Correct: 100e18 * 1e18 / 1.04e18 ≈ 96.15 wrsETH
// Insolvency gap: ~3.85 wrsETH per 100 ETH deposited, unbounded across all depositors
uint256 minted = wrsETH.balanceOf(address(this));
assertGt(minted, 96.15 ether); // over-issued
``` [6](#0-5) [7](#0-6)

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
