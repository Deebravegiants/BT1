### Title
Zero-Rate Propagation via Unguarded `updateRate()` / `lzReceive()` Causes Division-by-Zero DoS in Pool Deposits — (`contracts/cross-chain/CrossChainRateReceiver.sol`, `contracts/cross-chain/MultiChainRateProvider.sol`)

---

### Summary

`MultiChainRateProvider.updateRate()` is permissionless and performs no zero-check on the rate fetched from `getLatestRate()` before encoding and broadcasting it via LayerZero. `CrossChainRateReceiver.lzReceive()` performs no zero-check before writing the decoded value to `rate`. If a zero rate reaches the receiver, every subsequent call to `RSETHPool.viewSwapRsETHAmountAndFee` and `RSETHPoolNoWrapper.viewSwapRsETHAmountAndFee` panics with a division-by-zero, bricking all pool deposits until a non-zero rate update arrives.

---

### Finding Description

**Step 1 — Permissionless, unguarded `updateRate()`**

`MultiChainRateProvider.updateRate()` has no access control — only `nonReentrant`. Any EOA or contract can call it at any time. [1](#0-0) 

The function fetches `latestRate = getLatestRate()` and immediately encodes it without any zero-check: [2](#0-1) 

**Step 2 — `getLatestRate()` can return 0**

`RSETHMultiChainRateProvider.getLatestRate()` delegates directly to `ILRTOracle.rsETHPrice()` with no floor or sanity check: [3](#0-2) 

If `rsETHPrice()` returns 0 (e.g., transient oracle failure, all underlying price feeds returning stale/zero data, or an edge-case in the oracle's arithmetic), the zero value is encoded and dispatched.

**Step 3 — `lzReceive()` stores zero unconditionally**

`CrossChainRateReceiver.lzReceive()` decodes the payload and writes it to `rate` with no zero-check: [4](#0-3) 

**Step 4 — Division-by-zero in both pool contracts**

`RSETHPool.viewSwapRsETHAmountAndFee` divides by `rsETHToETHrate` (sourced from `getRate()` → `CrossChainRateReceiver.rate`): [5](#0-4) 

`RSETHPoolNoWrapper.viewSwapRsETHAmountAndFee` has the identical pattern: [6](#0-5) 

Both `deposit()` functions call `viewSwapRsETHAmountAndFee` unconditionally, so every deposit reverts while `rate == 0`. [7](#0-6) [8](#0-7) 

---

### Impact Explanation

All ETH and token deposits into `RSETHPool` and `RSETHPoolNoWrapper` revert with a Solidity panic (division by zero) for the entire window between the zero-rate `lzReceive` and the next valid non-zero rate update. No funds are lost, but the pool fails to deliver its promised exchange service. This matches **Low — Contract fails to deliver promised returns, but doesn't lose value**.

---

### Likelihood Explanation

`updateRate()` is permissionless, so any caller (including a keeper bot or a griefing actor) can trigger it at the exact moment `rsETHPrice()` returns 0. The oracle returning 0 does not require oracle operator compromise — it can occur transiently if all underlying asset price feeds simultaneously return stale or zero data, or if the oracle's internal arithmetic produces a zero result (e.g., zero total ETH in pool during an edge-case state). The window of impact persists until the next successful non-zero `updateRate()` call propagates through LayerZero (minutes to hours depending on bridge latency).

---

### Recommendation

1. **In `MultiChainRateProvider.updateRate()`**: add `require(latestRate > 0, "rate cannot be zero")` before encoding and sending.
2. **In `CrossChainRateReceiver.lzReceive()`**: add `require(_rate > 0, "rate cannot be zero")` before writing to `rate`.
3. Optionally add a staleness/sanity bound (e.g., rate must be within ±X% of the previous rate) to guard against extreme oracle deviations.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// 1. Deploy a mock LRTOracle that returns 0 for rsETHPrice()
// 2. Deploy RSETHMultiChainRateProvider with the mock oracle
// 3. Call provider.updateRate() — encodes 0, sends via LZ
// 4. Simulate lzReceive on CrossChainRateReceiver with payload = abi.encode(0)
//    → rate is set to 0
// 5. Call RSETHPool.viewSwapRsETHAmountAndFee(1 ether)
//    → reverts with division-by-zero panic (0x12)

contract MockLRTOracle {
    function rsETHPrice() external pure returns (uint256) { return 0; }
}

// In test:
// mockOracle = new MockLRTOracle();
// provider = new RSETHMultiChainRateProvider(address(mockOracle), lzEndpoint);
// provider.updateRate{value: fee}();
// // LayerZero delivers abi.encode(0) to receiver
// receiver.lzReceive(srcChainId, srcAddress, 0, abi.encode(uint256(0)));
// assert(receiver.getRate() == 0);
// pool.viewSwapRsETHAmountAndFee(1 ether); // PANICS: division by zero
```

### Citations

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-115)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-97)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;
```

**File:** contracts/pools/RSETHPool.sol (L271-271)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
```

**File:** contracts/pools/RSETHPool.sol (L316-319)
```text
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L237-237)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L282-285)
```text
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```
