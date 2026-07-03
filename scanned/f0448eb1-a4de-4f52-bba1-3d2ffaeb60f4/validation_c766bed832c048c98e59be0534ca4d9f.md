### Title
Stale Inflated rsETH Rate Broadcastable Cross-Chain During Oracle Auto-Pause — (`contracts/cross-chain/RSETHRateProvider.sol` / `contracts/cross-chain/CrossChainRateProvider.sol`)

---

### Summary

When `LRTOracle` auto-pauses due to a downside price breach, `rsETHPrice` is frozen at its pre-pause (inflated) value. Because `CrossChainRateProvider.updateRate()` has no access control and no oracle-pause guard, anyone can immediately broadcast this stale inflated rate to L2 receivers. L2 pools then misprice rsETH until an admin manually unpauses the oracle and re-broadcasts the correct rate.

---

### Finding Description

**Root cause 1 — `_updateRsETHPrice()` returns early without updating `rsETHPrice`:**

When the price drop exceeds `pricePercentageLimit`, the function pauses the protocol and returns immediately: [1](#0-0) 

`rsETHPrice` is only written at line 313. Because the early `return` at line 281 skips that write, `rsETHPrice` retains the last valid (higher) pre-pause value — it is **not** the new lower price, and it is **not** zeroed.

**Root cause 2 — `RSETHRateProvider.getLatestRate()` reads `rsETHPrice` blindly:** [2](#0-1) 

There is no call to `ILRTOracle.paused()` before returning the value.

**Root cause 3 — `updateRate()` is permissionless and has no pause guard:** [3](#0-2) 

Any EOA or contract can call `updateRate()` at any time. The function reads `getLatestRate()`, stores it as `rate`, and fires it cross-chain via LayerZero — all without checking whether the source oracle is in an emergency-paused state.

**Root cause 4 — `unpause()` is gated to `onlyLRTAdmin`:** [4](#0-3) 

Recovery requires a privileged admin transaction. Until that happens, every call to `updateRate()` propagates the same stale inflated value.

---

### Impact Explanation

The stale rate broadcast to L2 is **higher** than the true current price (the pre-pause peak is retained while the actual price has dropped). L2 pools that consume this rate will:

- Allow users to redeem rsETH at an inflated ETH value, draining L2 liquidity.
- Reject or misprice deposits/swaps that depend on the correct rate.

This constitutes **Medium — Temporary freezing of funds** (L2 pool operations are mispriced/disrupted) with a secondary risk of **theft from L2 liquidity pools** depending on how the receiver contract is consumed. The window persists from the moment of auto-pause until an admin unpauses `LRTOracle` and a correct rate is re-broadcast.

---

### Likelihood Explanation

- The trigger (a price drop beyond `pricePercentageLimit`) is a normal market event, not an attack.
- `updateRate()` requires no role, no signature, and only ETH for LayerZero gas — any actor can call it immediately after the auto-pause fires.
- The stale rate is already stored in `rsETHPrice`; no manipulation is needed.

---

### Recommendation

1. **Add an oracle-pause check inside `getLatestRate()` (or `updateRate()`):**

```solidity
function getLatestRate() public view override returns (uint256) {
    require(!ILRTOracle(rsETHPriceOracle).paused(), "Oracle paused");
    return ILRTOracle(rsETHPriceOracle).rsETHPrice();
}
```

2. **Restrict `updateRate()` to a trusted keeper role** so that stale rates cannot be broadcast by arbitrary callers during an emergency window.

3. **Emit a cross-chain "pause" message** when `LRTOracle._pause()` fires, so L2 receivers can halt rate-dependent operations autonomously without waiting for admin re-broadcast.

---

### Proof of Concept

```solidity
// Fork test outline (Foundry)
function test_staleRateBroadcastAfterAutoPause() public {
    // 1. Simulate a price drop beyond pricePercentageLimit
    //    (e.g., manipulate underlying asset oracle to drop >limit%)
    vm.mockCall(/* asset oracle */, abi.encodeWithSelector(...), abi.encode(lowPrice));

    // 2. Call updateRSETHPrice() — triggers auto-pause, rsETHPrice NOT updated
    lrtOracle.updateRSETHPrice();
    assertTrue(lrtOracle.paused());

    uint256 stalePre = lrtOracle.rsETHPrice(); // still the pre-pause inflated value

    // 3. Anyone broadcasts the stale rate cross-chain
    vm.deal(attacker, 1 ether);
    vm.prank(attacker);
    rsethRateProvider.updateRate{value: 0.1 ether}();

    // 4. Assert: rate stored in provider equals stale pre-pause value
    assertEq(rsethRateProvider.rate(), stalePre);

    // 5. Assert: stale rate != true current price (which is lower)
    uint256 truePrice = /* compute from current TVL / supply */;
    assertGt(rsethRateProvider.rate(), truePrice);
    // L2 receiver now holds an inflated rate until admin unpauses + re-broadcasts
}
```

### Citations

**File:** contracts/LRTOracle.sol (L143-146)
```text
    function unpause() external whenPaused onlyLRTAdmin {
        paused = false;
        emit Unpaused(msg.sender);
    }
```

**File:** contracts/LRTOracle.sol (L277-282)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/cross-chain/RSETHRateProvider.sol (L27-29)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

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
