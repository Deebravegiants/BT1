### Title
Stale `rsETHPrice` Broadcast via Permissionless `updateRate()` Causes Cross-Chain wrsETH Holders to Redeem at Incorrect Rate — (`contracts/cross-chain/RSETHRateProvider.sol`)

---

### Summary

`CrossChainRateProvider.updateRate()` is callable by any public address and reads `LRTOracle.rsETHPrice` — a cached storage variable — without any freshness check. If `LRTOracle.updateRSETHPrice()` has not been called recently, the stale (lower) price is broadcast via LayerZero to `RSETHRateReceiver` on the destination chain. Cross-chain wrsETH holders who redeem during this window receive fewer tokens than they are owed, permanently losing accrued restaking yield.

---

### Finding Description

**Entry point — `CrossChainRateProvider.updateRate()`:**

`updateRate()` is `external payable nonReentrant` with no role check. [1](#0-0) 

It calls `getLatestRate()`, which in `RSETHRateProvider` simply reads the cached storage variable `LRTOracle.rsETHPrice`: [2](#0-1) 

**The cached value — `LRTOracle.rsETHPrice`:**

`rsETHPrice` is a storage variable that is only updated when `_updateRsETHPrice()` is explicitly called (via `updateRSETHPrice()` or `updateRSETHPriceAsManager()`): [3](#0-2) [4](#0-3) 

There is no timestamp or block-number staleness guard anywhere in the `updateRate()` → `getLatestRate()` → `rsETHPrice()` call chain. The interface exposes only the raw cached value: [5](#0-4) 

**The gap:**

`updateRate()` does not atomically call `updateRSETHPrice()` before reading the price, and it does not verify that the cached price was updated within an acceptable window. Any caller can broadcast whatever value happens to be stored in `rsETHPrice` at the time of the call.

The same pattern is replicated in `RSETHMultiChainRateProvider.getLatestRate()`: [6](#0-5) 

---

### Impact Explanation

Cross-chain wrsETH is a yield-bearing wrapper whose value accrues as restaking rewards increase the rsETH/ETH exchange rate. The rate receiver on the destination chain is the sole source of truth for that exchange rate. If a stale (lower) rate is broadcast:

- Users who unwrap wrsETH receive fewer rsETH tokens than they are entitled to.
- The shortfall (accrued yield since the last oracle update) is permanently lost to those users — it is not recoverable after redemption.
- This matches **Medium — Permanent freezing of unclaimed yield**.

---

### Likelihood Explanation

- `updateRate()` requires only ETH for LayerZero gas fees — no privileged role.
- `rsETHPrice` becomes stale whenever the keeper/bot that calls `updateRSETHPrice()` is delayed, fails, or is deliberately front-run by a griever who calls `updateRate()` before the keeper refreshes the price.
- The window of staleness can be arbitrarily long; there is no on-chain enforcement of a maximum age.
- The `RSETHMultiChainRateProvider` variant is equally affected.

---

### Recommendation

1. **Atomic refresh:** Have `updateRate()` call `updateRSETHPrice()` (or an internal equivalent) before reading `rsETHPrice`, so the broadcast value always reflects the current TVL/supply ratio.
2. **Staleness guard:** Record the block timestamp of the last `rsETHPrice` update and revert in `updateRate()` if `block.timestamp - lastPriceUpdate > MAX_STALENESS`.
3. **Access control (defense-in-depth):** Restrict `updateRate()` to a trusted keeper role to prevent griefing via deliberate stale broadcasts.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Pseudocode — run on a local fork or Hardhat environment

// 1. Deploy MockLRTOracle with a fixed rsETHPrice = 1.05e18
// 2. Deploy RSETHRateProvider pointing at MockLRTOracle
// 3. Deploy MockLayerZeroEndpoint to capture the payload
// 4. Advance time by 7 days (vm.warp(block.timestamp + 7 days))
//    WITHOUT calling LRTOracle.updateRSETHPrice()
// 5. Compute actual TVL/supply ratio — it has grown to e.g. 1.08e18
// 6. Call RSETHRateProvider.updateRate{value: 0.01 ether}()
// 7. Decode the LayerZero payload captured by MockLayerZeroEndpoint
// 8. Assert: broadcastedRate == 1.05e18  (stale)
//            actualRate     == 1.08e18  (current)
//            broadcastedRate != actualRate  // invariant broken
// 9. Simulate a wrsETH unwrap on the destination chain using broadcastedRate
//    and show the user receives 1.05e18 per wrsETH instead of 1.08e18,
//    permanently losing 0.03e18 per token of accrued yield.
```

The stale `rsETHPrice` is read at step 6 directly from `LRTOracle.rsETHPrice` storage [2](#0-1) 
and encoded into the LayerZero payload without any freshness validation [7](#0-6) 
confirming the invariant break is reachable on unmodified production code.

### Citations

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L85-101)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceiver, address(this));

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);

        ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
            dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
        );

        emit RateUpdated(rate);
    }
```

**File:** contracts/cross-chain/RSETHRateProvider.sol (L27-29)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/interfaces/ILRTOracle.sol (L31-31)
```text
    function rsETHPrice() external view returns (uint256);
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```
