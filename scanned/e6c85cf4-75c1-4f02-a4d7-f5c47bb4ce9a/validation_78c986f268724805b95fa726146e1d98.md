### Title
Stale Cross-Chain Rate Used Without Staleness Validation Allows Over-Minting of wrsETH - (File: contracts/cross-chain/CrossChainRateReceiver.sol)

### Summary
`CrossChainRateReceiver.getRate()` returns the stored `rate` with no check against `lastUpdated`, despite the contract explicitly tracking when the rate was last received. If LayerZero message delivery is delayed or halted, the stale (lower) rsETH/ETH rate continues to be used by L2 deposit pools to price mints, allowing depositors to receive more wrsETH than the current rate entitles them to, at the expense of existing rsETH holders.

### Finding Description
`CrossChainRateReceiver` receives the rsETH/ETH exchange rate from L1 via LayerZero and stores it alongside a `lastUpdated` timestamp. However, `getRate()` returns the stored `rate` unconditionally — the `lastUpdated` field is written on receipt but is never read or validated when the rate is consumed. [1](#0-0) 

The `lzReceive` function updates both `rate` and `lastUpdated`: [2](#0-1) 

But `getRate()` ignores `lastUpdated` entirely: [3](#0-2) 

`RSETHRateReceiver` and `AGETHRateReceiver` both extend this base contract and expose the same unchecked `getRate()`. L2 deposit pools (`RSETHPool`, `RSETHPoolV2`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolNoWrapper`) all call `getRate()` on their configured oracle to compute how many wrsETH tokens to mint per unit of deposited ETH or collateral: [4](#0-3) 

The analog to the CRL report is exact: the PCCS contract returns CRL bytes and only validates non-emptiness; here the receiver stores a rate and only validates non-zero at oracle registration time (`if (IOracle(oracle).getRate() == 0) revert UnsupportedOracle()`), but never validates freshness at read time. [5](#0-4) 

### Impact Explanation
rsETH is a yield-bearing token whose ETH value increases monotonically over time. If the cross-chain rate update is delayed (e.g., LayerZero congestion, provider downtime), the stored rate is lower than the true current rate. Because minting uses `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate`, a stale lower rate produces a larger `rsETHAmount`. Depositors receive more wrsETH than the current backing entitles them to, diluting all existing rsETH holders. This constitutes **theft of unclaimed yield** (High impact).

### Likelihood Explanation
LayerZero message delivery is not guaranteed to be instantaneous or uninterrupted. Network congestion, relayer downtime, or a gap between rate-provider updates can leave `lastUpdated` hours or days in the past. Because rsETH accrues yield continuously, even a modest delay creates a profitable arbitrage window that any unprivileged depositor can exploit by simply calling `deposit()` on any active L2 pool.

### Recommendation
Add a configurable maximum staleness threshold (e.g., `maxStaleness`) to `CrossChainRateReceiver`. In `getRate()`, revert if `block.timestamp - lastUpdated > maxStaleness`:

```solidity
function getRate() external view returns (uint256) {
    if (block.timestamp - lastUpdated > maxStaleness) revert StaleRate();
    return rate;
}
```

Document the expected update frequency for each deployed receiver and ensure the threshold is set conservatively relative to the LayerZero send cadence.

### Proof of Concept
1. The rsETH/ETH rate on L1 is 1.05e18. A LayerZero message delivers this to `RSETHRateReceiver` on Arbitrum; `rate = 1.05e18`, `lastUpdated = T`.
2. 48 hours pass. rsETH accrues yield; the true rate is now 1.06e18. No new LayerZero message arrives (relayer downtime).
3. Alice calls `RSETHPool.deposit{value: 1 ether}("ref")` on Arbitrum.
4. `viewSwapRsETHAmountAndFee(1 ether)` calls `getRate()` → returns stale `1.05e18`.
5. `rsETHAmount = 1e18 * 1e18 / 1.05e18 ≈ 0.952 wrsETH` instead of the correct `≈ 0.943 wrsETH`.
6. Alice receives ~0.009 extra wrsETH per ETH deposited, extracted from existing holders' yield, with no special privilege required beyond being a normal depositor. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-16)
```text
    uint256 public rate;

    /// @notice Last time rate was updated
    uint256 public lastUpdated;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-105)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;

        emit RateUpdated(_rate);
    }

    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPool.sol (L311-320)
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

**File:** contracts/pools/RSETHPool.sol (L648-650)
```text
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
```

**File:** contracts/cross-chain/RSETHRateReceiver.sol (L1-10)
```text
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import { CrossChainRateReceiver } from "contracts/cross-chain/CrossChainRateReceiver.sol";

/// @title rsETH cross chain rate receiver
/// @notice Receives the rsETH rate from a provider contract on a different chain than the one this contract is deployed
/// on
contract RSETHRateReceiver is CrossChainRateReceiver {
    constructor(uint16 _srcChainId, address _rateProvider, address _layerZeroEndpoint) {
```
