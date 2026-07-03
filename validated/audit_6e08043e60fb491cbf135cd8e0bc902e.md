### Title
Stale rsETHPrice Propagated to All L2 Chains When LRTOracle Auto-Pauses on Price Drop — (`contracts/cross-chain/RSETHMultiChainRateProvider.sol`)

---

### Summary

When `LRTOracle._updateRsETHPrice()` detects a price drop beyond `pricePercentageLimit`, it calls `_pause()` and returns early **without updating `rsETHPrice`**. The stored `rsETHPrice` is frozen at the last pre-pause value. Because `RSETHMultiChainRateProvider.getLatestRate()` reads `rsETHPrice` directly with no oracle-liveness check, anyone can call `updateRate()` to broadcast the frozen stale rate to every registered `RSETHRateReceiver` on every L2 chain. Yield that accrues after the pause is never reflected in the L2 rate until an admin manually unpauses the oracle.

---

### Finding Description

**Step 1 — Oracle auto-pause freezes `rsETHPrice`.**

In `LRTOracle._updateRsETHPrice()`, when the computed `newRsETHPrice` drops more than `pricePercentageLimit` below `highestRsethPrice`:

```solidity
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;          // ← early return; rsETHPrice is NOT updated
}
``` [1](#0-0) 

`rsETHPrice` (line 313) is never reached, so it stays at the last pre-pause value. [2](#0-1) 

**Step 2 — `updateRSETHPrice()` is now blocked by `whenNotPaused`.**

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [3](#0-2) 

No further price updates can occur through the normal path. `rsETHPrice` is permanently frozen until an admin calls `unpause()`.

**Step 3 — `getLatestRate()` reads the frozen value with no liveness check.**

```solidity
function getLatestRate() public view override returns (uint256) {
    return ILRTOracle(rsETHPriceOracle).rsETHPrice();
}
``` [4](#0-3) 

`rsETHPrice()` is a plain public state variable getter — it does not check `paused`.

**Step 4 — `updateRate()` is callable by anyone with no pause guard.**

```solidity
function updateRate() external payable nonReentrant {
    uint256 latestRate = getLatestRate();   // reads frozen rsETHPrice
    rate = latestRate;
    ...
    ILayerZeroEndpoint(layerZeroEndpoint).send{...}(dstChainId, ...);
}
``` [5](#0-4) 

Any caller can invoke this and push the frozen pre-pause rate to every registered receiver.

**Step 5 — `lzReceive` stores whatever rate it receives.**

```solidity
uint256 _rate = abi.decode(_payload, (uint256));
rate = _rate;
lastUpdated = block.timestamp;
``` [6](#0-5) 

No staleness or validity check. The frozen rate is accepted and stored as current.

---

### Impact Explanation

All L2 pools and wrsETH wrapper contracts that consume the rate from `RSETHRateReceiver` will price rsETH at the frozen pre-pause value indefinitely. Any yield that accrues on L1 after the pause (staking rewards, EigenLayer rewards, etc.) is not reflected in the L2 rate. wrsETH holders on L2 cannot realize this yield until the oracle is manually unpaused and `updateRate()` is called again. Because there is no automatic unpause mechanism, the freeze is effectively permanent until admin intervention.

This matches the allowed impact: **Medium — Permanent freezing of unclaimed yield**.

---

### Likelihood Explanation

- `pricePercentageLimit` is a standard operational parameter set by admin; it is expected to be configured in production.
- A price drop event (e.g., slashing, depeg of a collateral asset) is a realistic market event.
- `updateRate()` is a permissionless `external payable` function — any caller (including a keeper bot or a well-meaning user) can trigger the stale propagation.
- No attacker capability beyond calling a public function is required.

---

### Recommendation

Add an oracle-liveness guard in `RSETHMultiChainRateProvider.getLatestRate()` (or in `MultiChainRateProvider.updateRate()`):

```solidity
function getLatestRate() public view override returns (uint256) {
    require(!ILRTOracle(rsETHPriceOracle).paused(), "Oracle paused: rate stale");
    return ILRTOracle(rsETHPriceOracle).rsETHPrice();
}
```

Alternatively, expose a `paused()` view on `ILRTOracle` and revert in `updateRate()` when the oracle is paused, preventing stale rates from being broadcast to L2 chains.

---

### Proof of Concept

```solidity
// Fork test outline (Foundry)
function test_stalePropagationAfterOraclePause() public {
    // 1. Set pricePercentageLimit to e.g. 1% (1e16)
    lrtOracle.setPricePercentageLimit(1e16);

    // 2. Simulate a price drop beyond the limit by manipulating
    //    underlying asset prices (e.g. mock oracle returns lower value)
    mockAssetOracle.setPrice(assetAddr, currentPrice * 98 / 100);

    // 3. Call updateRSETHPrice() — triggers _pause() + early return
    lrtOracle.updateRSETHPrice();
    assertEq(lrtOracle.paused(), true);

    uint256 frozenRate = lrtOracle.rsETHPrice(); // pre-pause value

    // 4. Time passes, real price recovers (simulate by unpausing + updating
    //    in a separate oracle instance, but the deployed oracle stays paused)

    // 5. Anyone calls updateRate() on the multi-chain provider
    vm.deal(address(this), 1 ether);
    rsETHMultiChainRateProvider.updateRate{value: 0.1 ether}();

    // 6. Simulate lzReceive delivery on L2 receiver
    vm.prank(layerZeroEndpoint);
    rsETHRateReceiver.lzReceive(
        srcChainId,
        abi.encodePacked(address(rsETHMultiChainRateProvider), address(rsETHRateReceiver)),
        0,
        abi.encode(frozenRate)
    );

    // 7. Assert L2 rate == frozen pre-pause value, not current true value
    assertEq(rsETHRateReceiver.rate(), frozenRate);
    // yield delta is inaccessible to wrsETH holders on L2
}
```

### Citations

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

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-97)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;
```
