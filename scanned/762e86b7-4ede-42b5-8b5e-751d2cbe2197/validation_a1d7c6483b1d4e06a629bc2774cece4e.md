### Title
Missing Positive Validation on Chainlink Price Enables Division-by-Zero in Pool Deposit Functions — (`contracts/oracles/ChainlinkPriceOracle.sol`, `contracts/pools/RSETHPool.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice` does not validate that the Chainlink `price` return value is strictly positive. A zero price propagates through `LRTOracle` into the `rsETHPrice` state variable, which is returned by `getRate()` in every L2 pool contract. All `viewSwapRsETHAmountAndFee` overloads divide by `rsETHToETHrate` without a zero guard, so if `getRate()` returns `0` the division reverts, freezing all user deposits across every pool variant.

---

### Finding Description

**Root cause 1 — oracle layer (`ChainlinkPriceOracle.sol`)**

`getAssetPrice` casts the raw Chainlink `int256 price` directly to `uint256` and divides, with no `require(price > 0)` guard:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

Chainlink can legitimately return `0` for a stale or circuit-broken feed. When it does, `getAssetPrice` returns `0` for that asset. `LRTOracle._updateRsETHPrice` then computes `totalETHInProtocol` using these zero prices, which can drive `newRsETHPrice` to `0`, persisting `rsETHPrice = 0`. [2](#0-1) 

**Root cause 2 — pool layer (all pool variants)**

Every `viewSwapRsETHAmountAndFee(uint256 amount)` overload fetches the rate and immediately divides by it with no zero guard:

```solidity
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;   // reverts if 0
``` [3](#0-2) 

The same unguarded division appears in the token-deposit overload:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [4](#0-3) 

Identical unguarded patterns exist in every other pool variant: [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) 

Note the inconsistency: `viewSwapAssetToPremintedRsETH` in `RSETHPoolV3` **does** guard against zero (`if (rsETHToETHrate == 0) revert UnsupportedOracle()`), confirming the developers are aware of the risk but did not apply the same guard to the deposit path. [9](#0-8) 

**Deposit entry point**

`deposit()` calls `viewSwapRsETHAmountAndFee` directly, so any revert there blocks the entire deposit flow: [10](#0-9) 

---

### Impact Explanation

If `getRate()` returns `0` — whether due to a Chainlink zero-price event, an uninitialized oracle, or a cross-chain rate receiver that has not yet received its first update — every call to `deposit()` across all pool variants reverts with a division-by-zero panic. Users cannot deposit ETH or supported tokens until the oracle is corrected and `rsETHPrice` is updated to a non-zero value. This constitutes **temporary freezing of funds** (Medium).

---

### Likelihood Explanation

Chainlink feeds can return `0` during circuit-breaker events or feed migrations. Additionally, `LRTOracle.rsETHPrice` is `0` by default before the first `updateRSETHPrice()` call, and cross-chain rate receivers may hold `0` before the first cross-chain message arrives. Any of these conditions, reachable without privileged access, triggers the freeze.

---

### Recommendation

1. In `ChainlinkPriceOracle.getAssetPrice`, add `require(price > 0, "Chainlink price error")` before returning.
2. In every `viewSwapRsETHAmountAndFee` overload, add `if (rsETHToETHrate == 0) revert UnsupportedOracle()` before the division — mirroring the guard already present in `viewSwapAssetToPremintedRsETH`.

---

### Proof of Concept

1. Chainlink ETH/LST feed enters a circuit-breaker state and returns `price = 0`.
2. `ChainlinkPriceOracle.getAssetPrice(asset)` returns `0` (no positive check).
3. `LRTOracle._updateRsETHPrice()` computes `totalETHInProtocol = 0`, setting `rsETHPrice = 0`.
4. `RSETHPool.getRate()` → `IOracle(rsETHOracle).getRate()` returns `0`.
5. Any user calls `RSETHPool.deposit{value: 1 ether}("ref")`.
6. `viewSwapRsETHAmountAndFee(1 ether)` executes `rsETHAmount = amountAfterFee * 1e18 / 0` → Solidity panic (division by zero), revert.
7. All deposits across all pool variants are frozen until the oracle recovers and `updateRSETHPrice()` is called successfully.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-54)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

**File:** contracts/LRTOracle.sol (L249-250)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/pools/RSETHPool.sol (L265-278)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPool.sol (L316-319)
```text
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPool.sol (L346-346)
```text
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L284-285)
```text
        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3.sol (L306-307)
```text
        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3.sol (L392-393)
```text
        uint256 rsETHToETHrate = getRate();
        if (rsETHToETHrate == 0) revert UnsupportedOracle();
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L425-426)
```text
        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L342-343)
```text
        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```
