Audit Report

## Title
Stale Oracle Rate in `CrossChainRateReceiver` Enables Over-Minting of wrsETH, Causing Protocol Insolvency — (`contracts/pools/RSETHPoolV2ExternalBridge.sol`)

## Summary

`CrossChainRateReceiver.getRate()` returns the stored `rate` with no staleness check despite `lastUpdated` being recorded on every update. `RSETHPoolV2ExternalBridge.deposit()` uses this rate to compute wrsETH minted per ETH deposited. When the rate is stale and below the true rsETH/ETH exchange rate, every depositor receives more wrsETH than the deposited ETH can back on L1, accumulating a structural shortfall that constitutes protocol insolvency.

## Finding Description

**Root cause — no freshness enforcement in `getRate()`.**

`CrossChainRateReceiver` records `lastUpdated` on every `lzReceive` call but never reads it in `getRate()`: [1](#0-0) 

`getRate()` unconditionally returns the last stored value: [2](#0-1) 

**Minting math divides by the stale rate.**

`viewSwapRsETHAmountAndFee` calls `getRate()` and computes `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate`. When `rsETHToETHrate` is lower than the true rate, the quotient is inflated: [3](#0-2) 

**`deposit()` mints the inflated amount unconditionally.** [4](#0-3) 

**`limitDailyMint` does not prevent the invariant break.**

The daily cap is computed in rsETH units via the same stale `viewSwapRsETHAmountAndFee` call, so the cap itself is inflated proportionally. It limits the scale of over-minting within one window but resets every 24 hours and does not prevent per-deposit undercollateralization: [5](#0-4) 

**Exploit path:**
1. LayerZero message is delayed (network congestion, rate provider offline) — no privileged compromise required.
2. `rate` in `CrossChainRateReceiver` is lower than the true rsETH/ETH exchange rate.
3. Any user calls `deposit{value: X}()`.
4. `viewSwapRsETHAmountAndFee` returns an inflated `rsETHAmount`.
5. `wrsETH.mint(msg.sender, rsETHAmount)` mints excess wrsETH.
6. Only `X` ETH is bridged to L1; the L1 vault cannot mint enough rsETH to redeem all outstanding wrsETH.
7. Repeated across depositors and daily windows, the shortfall compounds into insolvency.

## Impact Explanation

**Critical — Protocol insolvency.** rsETH is a monotonically appreciating yield-bearing token. Any staleness window (staleRate < trueRate) causes every deposit to mint `(trueRate/staleRate − 1) × depositAmount` excess wrsETH. The pool bridges only the deposited ETH; the L1 vault cannot cover redemptions. Concrete example (no fees, staleRate = 1e18, trueRate = 1.05e18): 100 depositors × 1 ETH → 100 ETH bridged, 100 wrsETH outstanding worth 105 ETH at true rate — a 5% structural shortfall per staleness window, compounding across resets.

## Likelihood Explanation

No attacker action is required. The condition arises from normal operational variance: LayerZero message delays, network congestion, or the rate provider simply not calling `updateRate()` on schedule. The presence of `lastUpdated` in the contract confirms the developers anticipated freshness tracking but omitted enforcement. Any depositor calling `deposit()` during a staleness window passively triggers the impact.

## Recommendation

Add a staleness threshold check in `CrossChainRateReceiver.getRate()`:

```solidity
uint256 public constant MAX_RATE_AGE = 24 hours;

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= MAX_RATE_AGE, "Rate is stale");
    return rate;
}
```

Alternatively, enforce the check inside `RSETHPoolV2ExternalBridge.getRate()` before consuming the oracle value. The threshold should be calibrated to the expected update frequency of the rate provider.

## Proof of Concept

```solidity
function testStaleOracleOverMint() public {
    // Deploy mock oracle returning stale rate (e.g., 1e18 instead of true 1.05e18)
    MockOracle staleOracle = new MockOracle(1e18);
    // Admin sets oracle (requires TIMELOCK_ROLE in production; use fork + prank in test)
    vm.prank(timelockAdmin);
    pool.setRSETHOracle(address(staleOracle));

    uint256 trueRate    = 1.05e18;
    uint256 depositAmt  = 1 ether;

    uint256 before = wrsETH.balanceOf(alice);
    vm.prank(alice);
    pool.deposit{value: depositAmt}("ref");
    uint256 minted = wrsETH.balanceOf(alice) - before;

    uint256 correct = depositAmt * 1e18 / trueRate; // ~0.952e18
    assertGt(minted, correct, "over-minted wrsETH exceeds ETH backing at true rate");

    // Invariant: repeat for N depositors, assert
    // wrsETH.totalSupply() * trueRate / 1e18 > address(pool).balance
}
```

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L95-105)
```text
        rate = _rate;

        lastUpdated = block.timestamp;

        emit RateUpdated(_rate);
    }

    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L104-126)
```text
    modifier limitDailyMint(uint256 amount) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        // Calculate the amount of rsETH that will be minted
        (uint256 rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
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

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L289-301)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L307-316)
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
