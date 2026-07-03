Audit Report

## Title
Stale Cross-Chain rsETH/ETH Rate Used in L2 Pool Deposit Calculations Without Staleness Validation — (File: `contracts/cross-chain/CrossChainRateReceiver.sol`)

## Summary
`CrossChainRateReceiver.getRate()` returns the stored `rate` unconditionally without checking `lastUpdated`, meaning the L2 deposit pools (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolNoWrapper`) can mint wrsETH/rsETH using a stale exchange rate during LayerZero message delivery lag. When the L2 oracle lags behind the true L1 rsETH price, depositors receive more wrsETH than their ETH is worth, and existing wrsETH holders absorb the resulting rsETH shortfall when the pool's ETH is bridged to L1.

## Finding Description
`CrossChainRateReceiver` stores the rsETH/ETH rate and a `lastUpdated` timestamp when a LayerZero message arrives: [1](#0-0) [2](#0-1) 

`getRate()` returns `rate` with no staleness check: [3](#0-2) 

All three L2 pool variants call `IOracle(rsETHOracle).getRate()` to compute the wrsETH mint amount: [4](#0-3) [5](#0-4) [6](#0-5) 

The formula `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate` means a stale-low rate (rsETH price has risen on L1 but L2 oracle not yet updated) produces a smaller divisor, minting more wrsETH than the deposited ETH is worth.

By contrast, the collateral token oracle enforces staleness: [7](#0-6) 

No equivalent guard exists for the rsETH oracle path. The L1 `updateRSETHPrice()` is permissionlessly callable, meaning any actor can trigger a price update on L1 that creates a discrepancy with the stale L2 rate: [8](#0-7) 

## Impact Explanation
**High — Theft of unclaimed yield.** When the L2 oracle rate lags behind the true L1 rsETH price (stale-low), a depositor receives more wrsETH than their ETH is worth. When the bridger later sends the pooled ETH to L1, the L1 mints rsETH at the true (higher) rate, yielding fewer rsETH tokens than the total wrsETH outstanding. The pool is structurally short rsETH, and existing wrsETH holders absorb the shortfall — their proportional claim on the underlying rsETH is diluted. This constitutes theft of unclaimed yield from existing holders.

## Likelihood Explanation
LayerZero cross-chain message delivery introduces real-world latency (minutes to hours). An attacker who monitors both the L1 `rsETHPrice` storage slot and the L2 `CrossChainRateReceiver.rate` can identify any discrepancy and deposit during the lag window. No privileged access is required — `deposit()` is a public payable function. The attack is repeatable every time a rate update is in-flight, and `updateRSETHPrice()` being permissionlessly callable means an attacker can even trigger a fresh L1 price update to widen the gap before exploiting the L2 lag.

## Recommendation
Add a configurable `maxStaleness` parameter to `CrossChainRateReceiver` and revert in `getRate()` if `block.timestamp - lastUpdated > maxStaleness`:

```solidity
uint256 public maxStaleness; // e.g. 24 hours

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= maxStaleness, "Rate is stale");
    return rate;
}
```

This mirrors the staleness guard already present in `ChainlinkOracleForRSETHPoolCollateral` and ensures deposits are rejected when the cross-chain rate has not been refreshed within an acceptable window.

## Proof of Concept
1. L1 `LRTOracle.rsETHPrice` increases from `1.05e18` to `1.10e18` (e.g., due to EigenLayer rewards accrual or a permissionless call to `updateRSETHPrice()`).
2. The LayerZero message carrying the new rate is in-flight; L2 `CrossChainRateReceiver.rate` still reads `1.05e18`.
3. Attacker calls `RSETHPoolV3.deposit{value: 1 ether}("")`.
4. `viewSwapRsETHAmountAndFee(1e18)` computes: `rsETHAmount = 1e18 * 1e18 / 1.05e18 ≈ 0.952e18` wrsETH minted.
5. Correct amount at true rate: `1e18 * 1e18 / 1.10e18 ≈ 0.909e18` wrsETH.
6. Attacker receives `≈ 0.043e18` excess wrsETH.
7. Bridger sends the pooled 1 ETH to L1; L1 mints `≈ 0.909e18` rsETH for the pool.
8. Pool is short `≈ 0.043e18` rsETH relative to outstanding wrsETH supply; existing holders bear the loss.

**Foundry fork test plan:** Fork an L2 deployment, set `CrossChainRateReceiver.rate` to a stale-low value (simulating in-flight update), call `RSETHPoolV3.deposit` as an unprivileged address, assert that the minted wrsETH amount exceeds what would be minted at the current L1 rate, and assert the resulting rsETH-per-wrsETH ratio is less than 1:1 after simulating the L1 bridge mint.

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L12-16)
```text
    /// @notice Last rate updated on the receiver
    uint256 public rate;

    /// @notice Last time rate was updated
    uint256 public lastUpdated;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L95-97)
```text
        rate = _rate;

        lastUpdated = block.timestamp;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L103-105)
```text
    function getRate() external view returns (uint256) {
        return rate;
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L277-286)
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

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L27-31)
```text
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```
