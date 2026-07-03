Audit Report

## Title
Stale Cross-Chain Rate Used Without Freshness Check Allows Over-Minting of wrsETH - (File: `contracts/cross-chain/CrossChainRateReceiver.sol`)

## Summary
`CrossChainRateReceiver.getRate()` returns the stored `rate` unconditionally despite tracking `lastUpdated`, providing no staleness protection. Both `RSETHPoolV3` and `RSETHPoolV3ExternalBridge` use this rate directly to compute wrsETH mint amounts. When the keeper fails to call `updateRate()` in a timely manner, depositors receive more wrsETH than their ETH warrants at the current true rate, diluting existing holders' yield.

## Finding Description
`CrossChainRateReceiver` stores both `rate` and `lastUpdated` on every `lzReceive()` call, but `getRate()` ignores `lastUpdated` entirely:

```solidity
// contracts/cross-chain/CrossChainRateReceiver.sol L102-105
function getRate() external view returns (uint256) {
    return rate;
}
```

`RSETHPoolV3.getRate()` delegates directly to this oracle:

```solidity
// contracts/pools/RSETHPoolV3.sol L235-237
function getRate() public view returns (uint256) {
    return IOracle(rsETHOracle).getRate();
}
```

Both `RSETHPoolV3.viewSwapRsETHAmountAndFee()` (L299-308) and `RSETHPoolV3ExternalBridge.viewSwapRsETHAmountAndFee()` (L418-427) compute mint amounts as `amountAfterFee * 1e18 / rsETHToETHrate`. Because rsETH is yield-bearing, its ETH-denominated rate increases monotonically. A stale (lower) rate produces a larger quotient, minting more wrsETH than the deposited ETH justifies.

`MultiChainRateProvider.updateRate()` is permissionless but requires the caller to supply ETH for LayerZero fees (L108). There is no on-chain enforcement of update frequency, no keeper incentive, and no fallback that forces a refresh before a deposit is processed. Any period of keeper downtime, gas price spike, or LayerZero congestion creates an exploitable staleness window.

No existing guard in either pool contract checks oracle freshness before minting.

## Impact Explanation
rsETH accrues staking yield continuously on L1. A stale L2 rate causes every deposit during the stale window to receive excess wrsETH. Once the oracle is refreshed, those tokens are immediately worth more ETH than was deposited, constituting direct theft of unclaimed yield from existing wrsETH holders whose proportional claim on the underlying pool is diluted. This matches the allowed impact: **High — Theft of unclaimed yield**.

## Likelihood Explanation
The attack requires no special privileges. Any depositor can monitor the L1 `LRTOracle.rsETHPrice()` against the L2 `CrossChainRateReceiver.rate` and deposit opportunistically whenever a gap exists. Keeper downtime, gas spikes, or LayerZero congestion are realistic and recurring conditions. The attack is repeatable across every deposit during a stale window and scales with the daily mint limit. **Likelihood: Medium.**

## Recommendation
1. Add a configurable `maxStaleness` threshold and revert in `getRate()` if exceeded:
```solidity
uint256 public maxStaleness = 24 hours;

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= maxStaleness, "Rate is stale");
    return rate;
}
```
2. Both pool contracts will automatically propagate the revert through `IOracle(rsETHOracle).getRate()`, blocking deposits when the oracle is stale.
3. Consider adding an on-chain incentive or keeper bond for `updateRate()` callers to ensure timely updates.

## Proof of Concept
1. At T=0: L1 rate = `1.050e18`, L2 `CrossChainRateReceiver.rate = 1.050e18`, `lastUpdated = T`.
2. Keeper goes offline for 30 days. L1 rate grows to `1.054e18` (~4.5% annualized yield).
3. Attacker calls `RSETHPoolV3.deposit{value: 10 ether}("")`.
4. `viewSwapRsETHAmountAndFee(10e18)` reads stale `rsETHToETHrate = 1.050e18`.
5. `rsETHAmount = 10e18 * 1e18 / 1.050e18 ≈ 9.5238 wrsETH`.
6. At true rate `1.054e18`, correct amount = `10e18 * 1e18 / 1.054e18 ≈ 9.4876 wrsETH`.
7. Attacker receives `≈ 0.0362 wrsETH` excess — immediately redeemable for more ETH than deposited once oracle refreshes.
8. Scaled to the daily mint limit across all depositors during the stale window, the cumulative over-mint is significant.

**Foundry fork test plan:** Fork the target L2, set `CrossChainRateReceiver.rate` to a value lower than the current L1 `LRTOracle.rsETHPrice()` (simulating staleness by skipping `lzReceive`), call `RSETHPoolV3.deposit{value: X}("")`, and assert that the minted wrsETH amount exceeds `X * 1e18 / trueL1Rate`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-16)
```text
    uint256 public rate;

    /// @notice Last time rate was updated
    uint256 public lastUpdated;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L102-105)
```text
    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L234-237)
```text
    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L418-427)
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

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-113)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        rate = latestRate;

        lastUpdated = block.timestamp;
```
