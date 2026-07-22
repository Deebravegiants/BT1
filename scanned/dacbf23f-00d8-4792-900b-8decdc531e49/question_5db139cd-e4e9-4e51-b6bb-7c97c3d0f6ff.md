[File: 'smart-contracts-poc/contracts/PriceProvider.sol -> Scope: Critical. Rounding, scaling, or bin-position math breaks pool solvency or lets repeated trades/LP operations extract value from standard ERC20 pools.'] [Symbol: AnchoredPriceProvider._shapedQuote] Can attacker-controlled marginStep=BPS_BASE-1 (stepBidFactor=1) under a customizable AnchoredPriceProvider with any valid oracle mid price reach AnchoredPriceProvider._shapedQuote -> _bandEdge(bid8, 1, Floor) = Math.mulDiv(bid8, Q64, STEP_DENOM, Floor) = 0 for

### Citations

**File:** smart-contracts-poc/contracts/PriceProvider.sol (L1-50)
```text
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import {IOffchainOracle} from
