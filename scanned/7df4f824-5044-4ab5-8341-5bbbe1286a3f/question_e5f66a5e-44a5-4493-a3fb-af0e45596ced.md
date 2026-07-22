[File: 'metric-core/contracts/MetricOmmPool.sol -> Scope: Medium. EXTSLOAD/state-view mismatch makes integrators or pool logic rely on wrong packed slot, bin, fee, or provider state with fund-impacting consequences.'] [Symbol: PoolStateLibrary._slot0 / MetricOmmPool.swap / _beforeSwap packedSlot0Initial] Can an integrator-controlled extension that reads packedSlot0Initial (passed to _beforeSwap) and decodes it with a wrong bit layout reach the extension's beforeSwap hook and violate the invariant that the extension's decoded spreadFeeE6 equals the pool's actual spreadFeeE6, corrupting the exact spreadFeeE6 value seen by the extension (if the extension reads bits 144-167 as notionalFeeE8 and bits 168-191 as spreadFeeE6, it gets swapped values) with scoped impact that the extension makes a wrong fee-based decision (e.g., a stop-loss extension that gates on fee level allows or blocks a swap incorrectly, causing a trader to execute at a wrong price)? Proof idea: deploy an extension that decodes packedSlot0Initial with swapped fee offsets and gates on spreadFeeE6 > threshold; set spreadFee

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L68-98)
```text
  // Slot 0 ordering (from left to right):
  //   [3 bytes notionalFeeE8] [3 bytes spreadFeeE6] [3 bytes curBinDistFromProvidedPriceE6]
  //   [13 bytes curPosInBin] [1 byte curBinIdx] [ 1byte pauseLevel]
  /// @dev 0 = active, 1 = paused by admin, 2 = paused by protocol. Transitions enforced by factory.
  uint8 internal pauseLevel;
  int8 internal curBinIdx;
  uint104 internal curPosInBin;
  int24 internal curBinDistFromProvidedPriceE6;
  uint24 internal spreadFeeE6;
  uint24 internal notionalFeeE8;

  // Slot 1 ordering (from left to right):
  //   [16bytes binTotals.scaledToken1] [16bytes binTotals.scaledToken0]
  BinTotals internal binTotals;

  // Slot 2 ordering (from left to right):
  //   [16bytes notionalFeeToken1Scaled] [16bytes notionalFeeToken0Scaled]
  uint128 internal notionalFeeToken0Scaled;
  uint128 internal notionalFeeToken1Scaled;

  // Slot 3 ordering (from left to right):
  //   [16bytes unused] [20 bytes priceProvider]
  /// @dev The price provider address - only used when `IMMUTABLE_PRICE_PROVIDER == address(0)`
  address internal priceProvider;

  mapping(int256 => BinState) internal _binStates;

  // ++++++++++ Unused when swapping ++++++++
  mapping(int256 => uint256) internal _binTotalShares;
  /// @dev Per-bin position shares keyed by `_positionBinKey`.
  mapping(bytes32 => uint256) internal _positionBinShares;
```

**File:** metric-core/contracts/libraries/PoolStateLibrary.sol (L1-40)
```text
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

import {SafeCast} from
