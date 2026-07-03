Audit Report

## Title
Division by Zero in `viewSwapRsETHAmountAndFee` Due to Uninitialized `CrossChainRateReceiver.rate` — (File: `contracts/cross-chain/CrossChainRateReceiver.sol`)

## Summary
`CrossChainRateReceiver.rate` is a plain `uint256` that defaults to `0` at deployment and is only updated when a valid LayerZero message is received via `lzReceive`. Every L2 pool's `viewSwapRsETHAmountAndFee` divides by this rate without a zero-guard, causing a Solidity panic revert on any deposit attempt before the first cross-chain rate message arrives. This completely blocks the deposit path for all unprivileged users during that window.

## Finding Description
`CrossChainRateReceiver` declares `uint256 public rate` at line 13 with no initialization. [1](#0-0) 

The concrete subclass `RSETHRateReceiver` sets only `rateInfo`, `srcChainId`, `rateProvider`, and `layerZeroEndpoint` in its constructor — `rate` is never written. [2](#0-1) 

The sole write path is `lzReceive`, which decodes and stores any `uint256` payload including `0` with no non-zero validation. [3](#0-2) 

`getRate()` returns `rate` directly with no zero-check. [4](#0-3) 

Every pool's `viewSwapRsETHAmountAndFee` calls `getRate()` and immediately divides by the result. In `RSETHPoolV3`: [5](#0-4) 

The same unguarded division is present in `RSETHPool`: [6](#0-5) 

And in `RSETHPoolV3ExternalBridge`: [7](#0-6) 

The inconsistency is confirmed by the fact that `viewSwapAssetToPremintedRsETH` in the same contracts **does** guard against zero — for example in `RSETHPoolV3`: [8](#0-7) 

And in `RSETHPoolV3ExternalBridge`: [9](#0-8) 

The deposit functions in all affected pools call `viewSwapRsETHAmountAndFee` directly (and also via the `limitDailyMint` modifier in V3), meaning any deposit attempt while `rate == 0` will panic-revert. [10](#0-9) 

## Impact Explanation
**Medium — Temporary freezing of funds.**

While `rate == 0`, every call to `deposit()` (ETH or token variant) reverts with a division-by-zero panic. No user can swap ETH or LSTs for `wrsETH`/`rsETH` through any affected pool. The deposit service is completely frozen for all unprivileged users until a valid non-zero rate is delivered via LayerZero. This matches the allowed impact: **Medium. Temporary freezing of funds.**

## Likelihood Explanation
**Low–Medium.** The zero-rate window exists between pool deployment and the first successful LayerZero rate propagation. Any user who attempts a deposit during this window triggers the revert. A secondary trigger exists if a zero-valued rate message is delivered (no on-chain guard prevents `lzReceive` from writing `rate = 0`), which could re-open the window at any time.

## Recommendation
Add a zero-rate guard in both overloads of `viewSwapRsETHAmountAndFee`, consistent with the guard already present in `viewSwapAssetToPremintedRsETH`:

```solidity
uint256 rsETHToETHrate = getRate();
if (rsETHToETHrate == 0) revert UnsupportedOracle();
```

Additionally, add a non-zero validation in `lzReceive` before writing to `rate`:

```solidity
uint256 _rate = abi.decode(_payload, (uint256));
require(_rate > 0, "Rate cannot be zero");
rate = _rate;
```

## Proof of Concept
1. Deploy `RSETHRateReceiver`. `rate` is `0`.
2. Configure an L2 pool (e.g., `RSETHPoolV3`) with this receiver as `rsETHOracle`.
3. Before any LayerZero message arrives, call `deposit{value: 1 ether}("ref")`.
4. Execution reaches `viewSwapRsETHAmountAndFee(1 ether)`:
   - `rsETHToETHrate = getRate()` → returns `0`
   - `rsETHAmount = amountAfterFee * 1e18 / 0` → **Panic: division by zero**
5. Transaction reverts. All depositors are blocked until the first valid rate message is received.

**Foundry test plan:**
```solidity
function test_depositRevertsWhenRateIsZero() public {
    // Deploy RSETHRateReceiver with rate == 0 (default)
    RSETHRateReceiver receiver = new RSETHRateReceiver(srcChainId, rateProvider, lzEndpoint);
    // Deploy and initialize RSETHPoolV3 pointing to receiver as oracle
    // ...
    vm.expectRevert(); // Panic: division by zero
    pool.deposit{value: 1 ether}("ref");
}
```

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-13)
```text
    uint256 public rate;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-95)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L103-105)
```text
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/cross-chain/RSETHRateReceiver.sol (L10-15)
```text
    constructor(uint16 _srcChainId, address _rateProvider, address _layerZeroEndpoint) {
        rateInfo = RateInfo({ tokenSymbol: "rsETH", baseTokenSymbol: "ETH" });
        srcChainId = _srcChainId;
        rateProvider = _rateProvider;
        layerZeroEndpoint = _layerZeroEndpoint;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L246-265)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L392-393)
```text
        uint256 rsETHToETHrate = getRate();
        if (rsETHToETHrate == 0) revert UnsupportedOracle();
```

**File:** contracts/pools/RSETHPool.sol (L311-320)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L418-427)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L523-524)
```text
        uint256 rsETHToETHrate = getRate();
        if (rsETHToETHrate == 0) revert UnsupportedOracle();
```
