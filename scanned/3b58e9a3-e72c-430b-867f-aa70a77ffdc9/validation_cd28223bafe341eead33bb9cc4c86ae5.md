### Title
Stale Inflated Rate Permanently Broadcast to L2 Receivers After Oracle Auto-Pause on Price Drop — (`contracts/cross-chain/RSETHMultiChainRateProvider.sol`)

---

### Summary

When `LRTOracle._updateRsETHPrice()` detects a price drop exceeding `pricePercentageLimit`, it calls `_pause()` and returns early **without updating `rsETHPrice`**. This freezes `rsETHPrice` at the pre-drop (inflated) value. Because `MultiChainRateProvider.updateRate()` has no access control, any unprivileged caller can broadcast this stale inflated rate to all registered L2 `RSETHRateReceiver` contracts indefinitely, causing incorrect yield accrual for L2 wrsETH/rsETH pool users.

---

### Finding Description

**Step 1 — Auto-pause freezes `rsETHPrice` at inflated value.**

When a TVL drop exceeds the configured threshold, `_updateRsETHPrice()` executes the downside-protection branch: [1](#0-0) 

The critical detail is the `return` on line 281: the function exits **before** reaching `rsETHPrice = newRsETHPrice` on line 313. `rsETHPrice` is therefore frozen at the last known (higher) value. [2](#0-1) 

**Step 2 — `whenNotPaused` blocks all future public price updates.**

`updateRSETHPrice()` is gated by `whenNotPaused`: [3](#0-2) 

Once `paused = true`, no public caller can refresh `rsETHPrice`. The only bypass is `updateRSETHPriceAsManager()`, which requires `MANAGER` role. [4](#0-3) 

**Step 3 — `getLatestRate()` reads the stale storage variable directly.**

`RSETHMultiChainRateProvider.getLatestRate()` reads `rsETHPrice` from storage with no freshness check: [5](#0-4) 

**Step 4 — `updateRate()` is permissionless.**

`MultiChainRateProvider.updateRate()` has no role check — any address can call it: [6](#0-5) 

It calls `getLatestRate()`, stores the result in `rate`, and broadcasts it via LayerZero to every registered `RSETHRateReceiver`. There is no guard preventing a broadcast of a stale rate.

---

### Impact Explanation

L2 `RSETHRateReceiver` contracts receive and store the inflated stale rate. Any L2 yield-bearing pool (wrsETH/rsETH) that uses this rate for yield accrual will compute yield against an inflated exchange rate that no longer reflects actual protocol backing. Users in these pools cannot claim correct yield: the rate they see is higher than reality, and the discrepancy persists until the oracle is manually unpaused and the price is updated by a manager. If TVL does not recover above the threshold, `updateRSETHPriceAsManager()` would trigger the pause again, making the freeze indefinite.

**Impact:** Medium — Permanent freezing of unclaimed yield for L2 pool users.

---

### Likelihood Explanation

- `pricePercentageLimit` is an admin-configured parameter explicitly designed to be set (e.g., 1% = `1e16`). Its presence in the codebase implies it is expected to be non-zero in production.
- A 2%+ TVL drop is realistic: EigenLayer slashing events, a depegged LST, or a large coordinated withdrawal can all cause this.
- `updateRate()` requires only ETH for LayerZero fees — any actor (including a griefing bot) can call it.
- No privileged access is required to trigger the broadcast of the stale rate.

---

### Recommendation

1. **Add a staleness guard in `updateRate()`**: revert if `LRTOracle.paused == true`, preventing broadcast of a rate that cannot be refreshed.
2. **Alternatively**, add a `lastUpdated` timestamp to `LRTOracle` and reject broadcasts if the rate is older than a configurable threshold (e.g., 24 hours).
3. **Or**, restrict `updateRate()` to an authorized role (operator/manager) so that stale-rate broadcasts require deliberate action.

---

### Proof of Concept

```solidity
// Fork test outline (Foundry)
function test_staleCrossChainRateAfterAutoPause() public {
    // 1. Set pricePercentageLimit to 1% (1e16)
    vm.prank(admin);
    lrtOracle.setPricePercentageLimit(1e16);

    // 2. Record current rsETHPrice (pre-drop)
    uint256 preDropPrice = lrtOracle.rsETHPrice();

    // 3. Simulate 2% TVL drop by mocking asset oracle to return lower price
    mockAssetOracle.setPrice(currentPrice * 98 / 100);

    // 4. Anyone calls updateRSETHPrice() — triggers auto-pause, returns early
    lrtOracle.updateRSETHPrice();

    // 5. Assert oracle is paused and rsETHPrice is unchanged
    assertTrue(lrtOracle.paused());
    assertEq(lrtOracle.rsETHPrice(), preDropPrice);

    // 6. Unprivileged caller broadcasts stale rate to L2
    vm.deal(attacker, 1 ether);
    vm.prank(attacker);
    rateProvider.updateRate{value: 0.1 ether}();

    // 7. Assert broadcast rate equals stale pre-drop price
    assertEq(rateProvider.rate(), preDropPrice);

    // 8. Warp 7 days — rate is still stale
    vm.warp(block.timestamp + 7 days);
    assertEq(lrtOracle.rsETHPrice(), preDropPrice); // frozen
    assertEq(rateProvider.rate(), preDropPrice);    // L2 still sees inflated rate
}
```

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-137)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);

        uint256 rateReceiversLength = rateReceivers.length;

        for (uint256 i; i < rateReceiversLength;) {
            uint16 dstChainId = uint16(rateReceivers[i]._chainId);

            bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceivers[i]._contract, address(this));

            (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
                .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

            ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
                dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
            );

            unchecked {
                ++i;
            }
        }

        emit RateUpdated(rate);
    }
```
