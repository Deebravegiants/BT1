### Title
Stale Rate Broadcast During L1 Oracle Pause Enables Destination Chain Pool Exploitation — (`contracts/cross-chain/CrossChainRateProvider.sol`)

---

### Summary

`CrossChainRateProvider.updateRate()` and `MultiChainRateProvider.updateRate()` are permissionless functions with no check on `LRTOracle.paused`. When the L1 oracle auto-pauses due to a price-drop event, `rsETHPrice` storage retains the pre-drop (inflated) value. Any caller can immediately broadcast this stale inflated rate to all destination chains, allowing destination chain pool participants to trade rsETH at a rate that no longer reflects actual backing.

---

### Finding Description

**Root cause — no pause gate on `updateRate()`:**

`CrossChainRateProvider.updateRate()` is `external payable nonReentrant` with no access control and no oracle-pause check: [1](#0-0) 

`RSETHRateProvider.getLatestRate()` is a plain storage read — it reads `rsETHPrice` directly with no pause check: [2](#0-1) 

The same pattern applies to `RSETHMultiChainRateProvider.getLatestRate()`: [3](#0-2) 

**How the stale value is created:**

`LRTOracle._updateRsETHPrice()` auto-pauses and **returns early** when a price drop exceeds `pricePercentageLimit`, without writing the new (lower) price to `rsETHPrice`: [4](#0-3) 

After this early return, `rsETHPrice` still holds the pre-drop value. `updateRSETHPrice()` is blocked by `whenNotPaused`: [5](#0-4) 

But `rsETHPrice` is a public storage variable — readable by anyone, including `getLatestRate()`: [6](#0-5) 

**Exploit sequence:**

1. A slashing or depeg event causes `_updateRsETHPrice()` to detect a price drop beyond `pricePercentageLimit`.
2. The oracle auto-pauses and returns early; `rsETHPrice = X` (inflated pre-drop value) remains in storage.
3. Attacker calls `CrossChainRateProvider.updateRate()` (or `MultiChainRateProvider.updateRate()`) with enough ETH for LayerZero fees.
4. `getLatestRate()` reads `rsETHPrice = X` — no revert, no pause check.
5. The stale inflated rate `X` is broadcast via LayerZero to all registered destination chain receivers.
6. `CrossChainRateReceiver.lzReceive()` accepts the message (it only validates source chain/address, not rate freshness) and updates `rate = X`: [7](#0-6) 
7. Destination chain pools continue pricing rsETH at `X` while actual backing is lower.

---

### Impact Explanation

Destination chain liquidity pools use the broadcast rate to price rsETH. With an inflated stale rate active:

- Users can acquire rsETH on destination chains at a price that exceeds actual L1 backing, extracting value from LP providers.
- LP providers on destination chains suffer direct fund losses proportional to the rate discrepancy and available liquidity.
- The window remains open until the L1 oracle is unpaused and a corrected rate is broadcast — during which the attacker (or any arbitrageur) can drain destination chain pools.

This constitutes direct theft of user funds (LP providers) on destination chains. The impact maps to **Critical: Direct theft of any user funds**.

---

### Likelihood Explanation

- The auto-pause trigger in `_updateRsETHPrice()` requires no admin action — it fires automatically on any price drop exceeding `pricePercentageLimit`.
- `updateRate()` requires only ETH for LayerZero fees, callable by any EOA.
- The stale rate window is deterministic and immediately exploitable after the auto-pause fires.
- No privileged role, leaked key, or governance capture is required.

---

### Recommendation

Add an oracle-pause check inside `updateRate()` in both `CrossChainRateProvider` and `MultiChainRateProvider`. The simplest fix is to expose a `paused()` getter on `LRTOracle` (it already has `bool public paused`) and revert if the oracle is paused:

```solidity
// In RSETHRateProvider / RSETHMultiChainRateProvider, or in the base updateRate():
function updateRate() external payable nonReentrant {
    require(!IPausable(rsETHPriceOracle).paused(), "Oracle paused: rate update suppressed");
    uint256 latestRate = getLatestRate();
    // ... rest of function
}
```

Alternatively, override `getLatestRate()` in `RSETHRateProvider` and `RSETHMultiChainRateProvider` to revert when the oracle is paused, so the check is co-located with the rate source.

---

### Proof of Concept

```solidity
// Fork test (Foundry) — unmodified production contracts
function test_staleRateBroadcastDuringPause() public {
    // 1. Simulate a price drop that triggers auto-pause in LRTOracle
    //    (e.g., manipulate underlying asset price oracle to drop > pricePercentageLimit)
    uint256 prePauseRate = lrtOracle.rsETHPrice();
    _triggerAutoPause(); // drives _updateRsETHPrice() to pause+return early

    assertTrue(lrtOracle.paused(), "Oracle should be paused");
    assertEq(lrtOracle.rsETHPrice(), prePauseRate, "rsETHPrice unchanged (stale)");

    // 2. Attacker broadcasts stale rate — no revert
    vm.deal(attacker, 1 ether);
    vm.prank(attacker);
    rsETHRateProvider.updateRate{value: 0.1 ether}();

    // 3. Assert: rate provider now holds the stale inflated rate
    assertEq(rsETHRateProvider.rate(), prePauseRate);

    // 4. Assert: destination chain receiver would be updated to stale rate
    //    (verify via LayerZero mock that lzReceive is called with prePauseRate)
    // This proves the invariant is broken: cross-chain rate updated during L1 pause
}
```

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

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
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

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-97)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;
```
