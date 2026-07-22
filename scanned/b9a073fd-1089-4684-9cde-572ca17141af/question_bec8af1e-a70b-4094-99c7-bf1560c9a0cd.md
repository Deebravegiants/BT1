[File: 'smart-contracts-poc/contracts/oracles/utils/LazerConsumer.sol -> Scope: Critical. Rounding, scaling, or bin-position math breaks pool solvency or lets repeated trades/LP operations extract value from standard ERC20 pools.'] [Symbol: LazerConsumer._normalize / conf=0] Can a valid Pyth Lazer payload with conf=0 (zero confidence interval) cause spreadU = Math.ceilDiv(10000 * 0, pU) = 0, storing spread0=0 in OracleData, reaching AnchoredPriceProvider._computeBidAsk with spreadBps=0, computing half = 0 + minMargin = minMargin, and if minMargin=0 then half=0, refBid = _bandEdge(mid, BPS_

### Citations

**File:** smart-contracts-poc/contracts/oracles/utils/LazerConsumer.sol (L1-50)
```text
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import {PythLazer} from
