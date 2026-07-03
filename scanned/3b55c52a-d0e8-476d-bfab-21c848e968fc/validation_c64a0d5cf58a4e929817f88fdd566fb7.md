The code confirms this is a real vulnerability. Let me trace each step precisely.

---

**Step 1 — Auto-pause leaves `rsETHPrice` stale**

In `_updateRsETHPrice()`, when a price drop exceeds `pricePercentageLimit`, the function pauses and returns early: [1](#0-0) 

```solidity
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;   // ← exits WITHOUT executing rsETHPrice = newRsETHPrice (line 313)
}
```

`rsETHPrice` is only written at line 313, which is never reached: [2](#0-1) 

**Step 2 — `updateRate()` has no access control and no pause check** [3](#0-2) 

`updateRate()` is `external payable nonReentrant` — no role check, no check that `LRTOracle` is paused, no staleness guard.

**Step 3 — `getLatestRate()` reads the stale storage slot directly** [4](#0-3) 

It reads `ILRTOracle(rsETHPriceOracle).rsETHPrice()` — the frozen pre-pause value — and that value is immediately encoded and sent via LayerZero.

---

### Title
Stale `rsETHPrice` Broadcast Cross-Chain After Auto-Pause Skips Price Update — (`contracts/cross-chain/RSETHRateProvider.sol`)

### Summary
When a TVL drop triggers the auto-pause in `LRTOracle._updateRsETHPrice()`, the function returns early at line 281 without writing the new lower price to `rsETHPrice`. The storage variable is frozen at the pre-pause inflated value. Because `RSETHRateProvider.updateRate()` has no access control and no check for whether `LRTOracle` is paused, any unprivileged caller can immediately broadcast the stale inflated rate cross-chain via LayerZero.

### Finding Description
`LRTOracle._updateRsETHPrice()` computes `newRsETHPrice` but, when `isPriceDecreaseOffLimit` is true, pauses the protocol and returns before reaching `rsETHPrice = newRsETHPrice` (line 313). The public storage variable `rsETHPrice` therefore remains at the pre-pause (higher) value indefinitely until an admin calls `unpause()` and a subsequent price update succeeds.

`RSETHRateProvider.getLatestRate()` reads `ILRTOracle(rsETHPriceOracle).rsETHPrice()` directly from storage. `CrossChainRateProvider.updateRate()` is callable by anyone, reads `getLatestRate()`, and sends the result via `ILayerZeroEndpoint.send()` to the destination chain. There is no guard that checks `LRTOracle.paused` before broadcasting.

### Impact Explanation
Cross-chain receivers get an inflated rsETH/ETH rate that does not reflect actual protocol collateral backing. Any protocol or pool on the destination chain that prices rsETH using this rate will overvalue it relative to what the L1 protocol can redeem. This matches the scoped impact: **Low — contract fails to deliver promised returns, but doesn't lose value**.

### Likelihood Explanation
The auto-pause is an intentional safety mechanism that will fire whenever a significant TVL drop occurs (e.g., slashing). The `updateRate()` call requires only ETH for gas. Any observer watching for the `Paused` event can immediately call `updateRate()` to lock in the stale rate cross-chain before the admin can unpause and correct it.

### Recommendation
Add a check in `CrossChainRateProvider.updateRate()` (or override it in `RSETHRateProvider`) that reverts if `LRTOracle` is paused:

```solidity
function updateRate() external payable nonReentrant {
    require(!ILRTOracle(rsETHPriceOracle).paused(), "Oracle paused");
    ...
}
```

Alternatively, update `rsETHPrice` to `newRsETHPrice` before calling `_pause()` and `return` in `_updateRsETHPrice()`, so the stored price always reflects the latest computed value regardless of pause state.

### Proof of Concept

```solidity
// 1. Simulate TVL drop beyond pricePercentageLimit
//    → _updateRsETHPrice() fires isPriceDecreaseOffLimit = true
//    → pauses protocol, returns at line 281
//    → rsETHPrice unchanged (stale high value)

// 2. Unprivileged caller immediately calls:
rsETHRateProvider.updateRate{value: lzFee}();

// 3. getLatestRate() returns ILRTOracle.rsETHPrice() — the stale value
// 4. LayerZero broadcasts stale inflated rate to destination chain

// Assert:
uint256 broadcastRate = rsETHRateProvider.rate();
uint256 actualRate = totalETHInProtocol / rsETH.totalSupply();
assert(broadcastRate > actualRate); // stale rate exceeds actual backing
```

### Citations

**File:** contracts/LRTOracle.sol (L277-281)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
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

**File:** contracts/cross-chain/RSETHRateProvider.sol (L27-29)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```
