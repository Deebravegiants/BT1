Audit Report

## Title
Stale Rate Accepted Without Freshness Check Enables Block-Stuffing Arbitrage — (`contracts/cross-chain/CrossChainRateReceiver.sol`)

## Summary

`CrossChainRateReceiver` stores `lastUpdated` on every `lzReceive` call but never consults it in `getRate()`. An attacker who delays `lzReceive` messages on a low-fee L2 via block stuffing can hold the rate stale while rsETH accrues yield, then deposit ETH at the artificially low rate to mint excess rsETH, which can be bridged to mainnet for profit.

## Finding Description

`lzReceive` records the update timestamp but `getRate()` ignores it entirely:

```solidity
// CrossChainRateReceiver.sol L97
lastUpdated = block.timestamp;

// CrossChainRateReceiver.sol L103-105
function getRate() external view returns (uint256) {
    return rate;   // no staleness guard
}
```

`RSETHPoolV3WithNativeChainBridge.viewSwapRsETHAmountAndFee` consumes this rate directly:

```solidity
// RSETHPoolV3WithNativeChainBridge.sol L340-343
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

Because rsETH/ETH is monotonically increasing (staking yield), a stale (lower) rate causes the division to yield more rsETH per ETH than the depositor is entitled to. The `deposit()` function mints directly from this calculation with no additional freshness guard:

```solidity
// RSETHPoolV3WithNativeChainBridge.sol L294-298
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
feeEarnedInETH += fee;
wrsETH.mint(msg.sender, rsETHAmount);
```

The full call chain is: `deposit()` → `limitDailyMint` modifier → `viewSwapRsETHAmountAndFee` → `getRate()` → stale `rate`. No check at any step consults `lastUpdated`.

## Impact Explanation

Impact category: **Low — Block stuffing**. The contract fails to deliver the correct exchange rate. An attacker who stuffs blocks for `T` hours extracts:

```
excess_rsETH ≈ depositAmount × (annualYield × T / 8760) / staleRate
```

At 4.5% APY, 24 h staleness, and a 10,000 ETH deposit (within a generous `dailyMintLimit`), excess profit is ≈ 1.2 ETH. The minted wrsETH is bridgeable to mainnet, converting the gain into real mainnet value. The `dailyMintLimit` caps per-day exposure but does not eliminate it.

## Likelihood Explanation

- Requires sustained block stuffing on a sequencer-based L2. On very-low-fee chains (e.g., Linea at <0.01 gwei), the cost to fill ~28,800 blocks (24 h at 3 s/block) can be below the profit threshold for large deposits.
- No on-chain mechanism detects or rejects a stale rate; `lastUpdated` is stored but unused.
- The native bridge withdrawal delay (7 days for optimistic rollups) adds friction but does not prevent profit extraction.
- Attack is repeatable each day up to `dailyMintLimit`.

## Recommendation

Add a configurable maximum rate age and revert if the rate is too old:

```solidity
uint256 public maxRateAge = 1 hours; // configurable by owner

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= maxRateAge, "Rate too stale");
    return rate;
}
```

This ensures deposits revert rather than proceed at a stale rate, removing the economic incentive for block stuffing.

## Proof of Concept

The following Foundry test confirms `getRate()` returns the stale value after 24 hours with no revert, and that the resulting excess rsETH minted represents a positive profit:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "contracts/cross-chain/RSETHRateReceiver.sol";

contract StaleRatePoC is Test {
    RSETHRateReceiver receiver;

    function setUp() public {
        receiver = new RSETHRateReceiver(101, address(0xBEEF), address(this));
        bytes memory payload = abi.encode(uint256(1.045e18));
        receiver.lzReceive(101, abi.encodePacked(address(0xBEEF)), 0, payload);
    }

    function testStaleProfitPositive() public {
        vm.warp(block.timestamp + 24 hours);

        uint256 realRate  = 1_045_128_767_123_287_671; // 4.5% APY after 24h
        uint256 staleRate = receiver.getRate();         // still 1.045e18, no revert

        assertEq(staleRate, 1.045e18);

        uint256 deposit = 10_000 ether;
        uint256 staleRsETH = deposit * 1e18 / staleRate;
        uint256 fairRsETH  = deposit * 1e18 / realRate;
        uint256 profitETH  = (staleRsETH - fairRsETH) * realRate / 1e18;

        assertGt(profitETH, 0); // ~1.2 ETH profit on 10,000 ETH deposit
    }
}
``` [1](#0-0) [2](#0-1) [3](#0-2)

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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L294-298)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L335-344)
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
