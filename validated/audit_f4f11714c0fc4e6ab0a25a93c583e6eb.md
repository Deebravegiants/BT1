### Title
Absence of Pause Propagation in RSETHRateReceiver Allows Stale Rate to Drive L2 Minting After L1 Oracle Pause - (File: contracts/cross-chain/RSETHRateReceiver.sol)

---

### Summary

`RSETHRateReceiver` (and its base `CrossChainRateReceiver`) has no pause mechanism and no staleness guard on `getRate()`. When `LRTOracle` on L1 is paused — including via the automatic downside-protection path in `_updateRsETHPrice()` — the last `rsETHPrice` stored in the oracle remains readable, and the L2 receiver continues to serve it to pool depositors without any indication that the L1 safety halt has occurred.

---

### Finding Description

**L1 side — `LRTOracle`**

`LRTOracle` exposes a public `paused` flag and a `whenNotPaused` modifier that blocks `updateRSETHPrice()`. However, the `rsETHPrice` state variable is always readable regardless of pause state: [1](#0-0) [2](#0-1) 

The auto-pause path in `_updateRsETHPrice()` triggers when the price drops beyond `pricePercentageLimit`, freezing `rsETHPrice` at the pre-drop (inflated) value: [3](#0-2) 

**Rate provider — no pause check on `rsETHPrice` read**

Both `RSETHRateProvider` and `RSETHMultiChainRateProvider` read `rsETHPrice` directly with no oracle-pause guard: [4](#0-3) [5](#0-4) 

`CrossChainRateProvider.updateRate()` is callable by **anyone** with no access control and no pause guard, so the stale `rsETHPrice` can be pushed to L2 at any time after the oracle is paused: [6](#0-5) 

**L2 side — `RSETHRateReceiver` / `CrossChainRateReceiver`**

`CrossChainRateReceiver` stores `lastUpdated` but never uses it. `getRate()` returns the cached `rate` unconditionally: [7](#0-6) 

`RSETHRateReceiver` adds no pause mechanism on top of this: [8](#0-7) 

**Pool — uses the stale rate directly**

`RSETHPoolV2.deposit()` and `RSETHPoolV3.deposit()` call `getRate()` on the oracle (which resolves to `RSETHRateReceiver.getRate()`) and use it to compute the rsETH mint amount: [9](#0-8) [10](#0-9) 

The pool has its own independent `paused` flag, but it is not linked to the L1 oracle state in any way.

---

### Impact Explanation

When `LRTOracle` auto-pauses due to a price drop, `rsETHPrice` is frozen at the pre-drop (inflated) value. L2 depositors calling `deposit()` receive:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate
```

With an inflated `rsETHToETHrate`, users receive **fewer rsETH tokens than the current true rate entitles them to**. The protocol does not lose ETH, but users do not receive the returns the contract promises at the time of deposit. This matches the scoped impact: **Low — Contract fails to deliver promised returns, but doesn't lose value.**

---

### Likelihood Explanation

The auto-pause in `_updateRsETHPrice()` is a normal operational event (triggered whenever the price moves beyond `pricePercentageLimit`). The window between L1 oracle pause and a manual L2 pool pause is non-zero and can span multiple blocks or minutes. During this window, any user can deposit on L2 at the stale rate. Additionally, `updateRate()` is permissionless, so the stale rate can be actively re-pushed to L2 after the oracle is paused.

---

### Recommendation

1. Add a `paused` flag and `pause()`/`unpause()` functions to `CrossChainRateReceiver` (and therefore `RSETHRateReceiver`), and add a `whenNotPaused` guard to `lzReceive()` and `getRate()`.
2. Add a staleness check in `getRate()` using the stored `lastUpdated` timestamp, reverting if the rate is older than a configurable threshold.
3. Consider adding a pause guard to `CrossChainRateProvider.updateRate()` so the rate cannot be pushed to L2 when the L1 oracle is paused.
4. Alternatively, have `RSETHRateProvider.getLatestRate()` check `LRTOracle.paused()` and revert if the oracle is paused, preventing stale rate propagation at the source.

---

### Proof of Concept

```solidity
// Fork test (local fork, no public mainnet)
// 1. Deploy/fork with LRTOracle, RSETHRateProvider, RSETHRateReceiver, RSETHPoolV2

// 2. Simulate a price drop triggering auto-pause on L1
lrtOracle.updateRSETHPrice(); // triggers _pause() internally if price drop > limit
assert(lrtOracle.paused() == true);

uint256 stalePriceOnL1 = lrtOracle.rsETHPrice(); // still returns pre-pause inflated value

// 3. Anyone can still push the stale rate to L2
rsETHRateProvider.updateRate{value: lzFee}(); // no revert — reads rsETHPrice directly

// 4. L2 receiver holds the stale rate
assert(rsETHRateReceiver.getRate() == stalePriceOnL1);
assert(rsETHRateReceiver.getRate() > currentTrueRate); // inflated

// 5. Pool deposit succeeds at the stale (inflated) rate
uint256 rsETHBefore = wrsETH.balanceOf(user);
rsETHPoolV2.deposit{value: 1 ether}("ref");
uint256 rsETHAfter = wrsETH.balanceOf(user);

// User receives fewer rsETH than the true rate would give
uint256 expectedAtTrueRate = 1 ether * 1e18 / currentTrueRate;
assert(rsETHAfter - rsETHBefore < expectedAtTrueRate);
```

### Citations

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

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L102-105)
```text
    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/cross-chain/RSETHRateReceiver.sol (L9-16)
```text
contract RSETHRateReceiver is CrossChainRateReceiver {
    constructor(uint16 _srcChainId, address _rateProvider, address _layerZeroEndpoint) {
        rateInfo = RateInfo({ tokenSymbol: "rsETH", baseTokenSymbol: "ETH" });
        srcChainId = _srcChainId;
        rateProvider = _rateProvider;
        layerZeroEndpoint = _layerZeroEndpoint;
    }
}
```

**File:** contracts/pools/RSETHPoolV2.sol (L200-203)
```text
    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L225-233)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```
