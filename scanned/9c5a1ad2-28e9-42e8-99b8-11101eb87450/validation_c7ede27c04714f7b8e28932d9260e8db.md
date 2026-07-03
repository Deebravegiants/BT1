### Title
Zero-Rate Broadcast via Uninitialized `rsETHPrice` Freezes Cross-Chain Pool Deposits — (`contracts/cross-chain/RSETHRateProvider.sol`)

---

### Summary

`LRTOracle.rsETHPrice` defaults to `0` before the first `updateRSETHPrice()` call. `RSETHRateProvider.updateRate()` is permissionless and contains no zero-rate guard, so any caller can broadcast this `0` value over LayerZero. The receiver stores `rate = 0`, causing `RSETHPoolV2NBA.deposit()` to revert with a division-by-zero until a valid rate is re-propagated.

---

### Finding Description

**Step 1 — Default state of `rsETHPrice`**

`rsETHPrice` is a plain `uint256` storage variable. Its Solidity default is `0`. It is only written inside `_updateRsETHPrice()`. [1](#0-0) 

`_updateRsETHPrice()` sets it to `1 ether` only when `rsethSupply == 0`, and to a computed value otherwise. Before the first call, the value is `0`. [2](#0-1) 

**Step 2 — `getLatestRate()` reads the raw storage value**

`RSETHRateProvider.getLatestRate()` directly returns `ILRTOracle(rsETHPriceOracle).rsETHPrice()` with no zero-value guard. [3](#0-2) 

**Step 3 — `updateRate()` is permissionless and has no zero-rate check**

`CrossChainRateProvider.updateRate()` is `external payable` with no access control. It reads `getLatestRate()`, stores it, encodes it, and sends it via LayerZero — all without checking `latestRate > 0`. [4](#0-3) 

**Step 4 — Receiver stores the zero rate unconditionally**

`CrossChainRateReceiver.lzReceive()` decodes the payload and writes `rate = _rate` with no zero-value guard. [5](#0-4) 

**Step 5 — Pool deposit divides by the rate**

`RSETHPoolV2NBA.viewSwapRsETHAmountAndFee()` computes `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate`. When `rsETHToETHrate == 0` this is a division-by-zero revert. [6](#0-5) 

`deposit()` calls `viewSwapRsETHAmountAndFee()` unconditionally, so every deposit reverts. [7](#0-6) 

---

### Impact Explanation

All calls to `RSETHPoolV2NBA.deposit()` revert with division-by-zero for as long as the receiver holds `rate == 0`. No new ETH→rsETH swaps can be executed on the destination chain. The freeze is temporary: it ends once the operator calls `updateRSETHPrice()` on mainnet (setting a non-zero price) and then calls `updateRate()` again to propagate the corrected value. This matches **Medium — Temporary freezing of funds**.

---

### Likelihood Explanation

The attack window is the period between contract deployment and the first successful `updateRSETHPrice()` call. `updateRate()` requires only enough ETH to cover LayerZero fees (a few dollars), has no role restriction, and can be called by any EOA. The attacker does not need any privileged access. The window is short in a careful deployment but is a realistic race condition, especially on a new chain deployment.

---

### Recommendation

Add a non-zero rate guard in `CrossChainRateProvider.updateRate()`:

```solidity
function updateRate() external payable nonReentrant {
    uint256 latestRate = getLatestRate();
    require(latestRate > 0, "Rate must be non-zero");
    ...
}
```

Alternatively (or additionally), add the same guard in `CrossChainRateReceiver.lzReceive()` before writing `rate = _rate`.

---

### Proof of Concept

```solidity
// Local fork test (no mainnet interaction)
function testZeroRateBroadcast() public {
    // 1. Deploy LRTOracle proxy — do NOT call updateRSETHPrice()
    LRTOracle oracle = deployLRTOracle(...);
    assertEq(oracle.rsETHPrice(), 0);

    // 2. Deploy RSETHRateProvider pointing at oracle
    RSETHRateProvider provider = new RSETHRateProvider(
        address(oracle), dstChainId, address(mockLZEndpoint)
    );
    assertEq(provider.getLatestRate(), 0);

    // 3. Anyone calls updateRate() with LZ fee
    provider.updateRate{value: 0.01 ether}();
    // mockLZEndpoint records payload = abi.encode(0)

    // 4. Deliver message to RSETHRateReceiver
    bytes memory payload = abi.encode(uint256(0));
    receiver.lzReceive(srcChainId, abi.encodePacked(address(provider), address(receiver)), 0, payload);
    assertEq(receiver.rate(), 0);

    // 5. Pool deposit reverts
    vm.expectRevert(); // division by zero
    pool.deposit{value: 1 ether}("ref");
}
```

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L218-222)
```text
        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
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

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-97)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L106-117)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L129-132)
```text
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```
