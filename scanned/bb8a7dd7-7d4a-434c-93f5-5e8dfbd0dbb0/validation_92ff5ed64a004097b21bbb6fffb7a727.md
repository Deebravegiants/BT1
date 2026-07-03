### Title
Unprivileged caller can broadcast stale pre-pause rsETH rate to L2 pools when LRTOracle auto-pauses on price anomaly — (`contracts/cross-chain/MultiChainRateProvider.sol`)

---

### Summary

`MultiChainRateProvider.updateRate()` has no access control and no oracle-pause guard. `RSETHMultiChainRateProvider.getLatestRate()` reads `LRTOracle.rsETHPrice` — a plain public storage variable — directly. When `LRTOracle` auto-pauses due to a price-drop anomaly, it returns early **without** updating `rsETHPrice`, leaving it at the pre-drop inflated value. Any caller can immediately invoke `updateRate()` to broadcast that stale inflated rate to every configured L2 receiver.

---

### Finding Description

**Step 1 — Auto-pause leaves `rsETHPrice` stale.**

`LRTOracle._updateRsETHPrice()` contains downside protection logic:

```solidity
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;   // <-- exits WITHOUT writing rsETHPrice
}
``` [1](#0-0) 

`rsETHPrice` is never updated in this branch; it retains the last written value, which is the pre-drop inflated price. [2](#0-1) 

**Step 2 — `getLatestRate()` reads the stale storage variable unconditionally.**

```solidity
function getLatestRate() public view override returns (uint256) {
    return ILRTOracle(rsETHPriceOracle).rsETHPrice();
}
``` [3](#0-2) 

`rsETHPrice()` is a public getter for a storage slot — it does not check `paused`. There is no staleness guard anywhere in this call.

**Step 3 — `updateRate()` is permissionless and has no pause check.**

```solidity
function updateRate() external payable nonReentrant {
    uint256 latestRate = getLatestRate();
    rate = latestRate;
    ...
    ILayerZeroEndpoint(layerZeroEndpoint).send{value: estimatedFee}(...);
``` [4](#0-3) 

No `onlyOwner`, no `whenNotPaused`, no check that `ILRTOracle.paused == false`. Any EOA can call this with enough ETH for LZ fees.

**Complete exploit path (no privileged access required):**

1. Market event causes rsETH backing to drop sharply.
2. Someone (or a bot) calls `LRTOracle.updateRSETHPrice()` → `_updateRsETHPrice()` detects the drop exceeds `pricePercentageLimit`, auto-pauses oracle + deposit pool + withdrawal manager, and **returns without writing the new lower price**.
3. `rsETHPrice` now holds the pre-drop inflated value (e.g. 1.10 ETH when true value is 0.95 ETH).
4. Attacker calls `RSETHMultiChainRateProvider.updateRate{value: lzFee}()`.
5. `getLatestRate()` returns the stale 1.10 value; it is encoded and sent via LayerZero to every L2 rate receiver.
6. L2 pools (e.g. Curve, Balancer, Pendle) reprice rsETH at 1.10 ETH.
7. Attacker swaps ETH → rsETH on L2 at the inflated rate, extracting ETH from pool reserves.

---

### Impact Explanation

L2 liquidity pool LPs suffer direct ETH loss. The attacker acquires rsETH at a price above its true backing, profiting from the spread between the broadcast stale rate and the real post-anomaly rate. This is direct theft of at-rest user funds held in L2 pools. The L1 deposit pool being paused does not prevent L2-side exploitation.

---

### Likelihood Explanation

- Auto-pause is triggered by normal market conditions, not admin action — no collusion required.
- `updateRate()` is permissionless; the attacker only needs to supply LZ fees (a few dollars of ETH).
- The window is open from the moment the oracle auto-pauses until the admin manually unpauses and re-broadcasts a correct rate — potentially hours.
- The scenario is directly incentivized: the larger the price drop that triggered the pause, the larger the spread the attacker can exploit.

---

### Recommendation

Add an oracle-pause guard to `updateRate()` (and `estimateFees`/`estimateTotalFee` for consistency):

```solidity
// In RSETHMultiChainRateProvider or in MultiChainRateProvider base
function updateRate() external payable nonReentrant {
    require(!ILRTOracle(rsETHPriceOracle).paused(), "Oracle paused");
    ...
}
```

Alternatively, expose a `paused()` view on `ILRTOracle` and check it inside `getLatestRate()`, reverting if the oracle is paused so that no stale rate can ever be read or broadcast.

---

### Proof of Concept

```solidity
// Fork test (Ethereum mainnet fork)
function testStaleBroadcastAfterAutoPause() public {
    // 1. Simulate a large price drop by manipulating underlying asset prices
    //    such that _updateRsETHPrice() triggers the auto-pause branch.
    //    (Use vm.mockCall or a mock price oracle returning a value below threshold.)
    vm.mockCall(
        address(assetPriceOracle),
        abi.encodeWithSelector(IPriceFetcher.getAssetPrice.selector, stETH),
        abi.encode(0.80 ether) // large drop
    );
    lrtOracle.updateRSETHPrice(); // triggers auto-pause, rsETHPrice NOT updated

    // 2. Confirm oracle is paused and rsETHPrice is stale (inflated)
    assertTrue(lrtOracle.paused());
    uint256 staleRate = lrtOracle.rsETHPrice(); // still pre-drop value

    // 3. Attacker broadcasts stale rate — no privilege needed
    vm.deal(attacker, 1 ether);
    vm.prank(attacker);
    rateProvider.updateRate{value: lzFee}();

    // 4. Assert the broadcast rate equals the stale inflated value
    assertEq(rateProvider.rate(), staleRate);
    // L2 pool now prices rsETH at staleRate > true backing → exploit window open
}
```

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
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
