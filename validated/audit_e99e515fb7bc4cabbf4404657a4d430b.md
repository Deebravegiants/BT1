Audit Report

## Title
Zero-Rate Propagation via Unguarded `updateRate()` / `lzReceive()` Causes Division-by-Zero DoS in Pool Deposits — (`contracts/cross-chain/MultiChainRateProvider.sol`, `contracts/cross-chain/CrossChainRateReceiver.sol`)

## Summary

`MultiChainRateProvider.updateRate()` is permissionless and performs no zero-check on the rate returned by `getLatestRate()` before encoding and broadcasting it via LayerZero. `CrossChainRateReceiver.lzReceive()` performs no zero-check before writing the decoded value to `rate`. If a zero rate reaches the receiver, every subsequent call to `RSETHPool.viewSwapRsETHAmountAndFee` and `RSETHPoolNoWrapper.viewSwapRsETHAmountAndFee` panics with a division-by-zero, bricking all pool deposits until a valid non-zero rate update propagates.

## Finding Description

**Step 1 — Permissionless, unguarded `updateRate()`**

`MultiChainRateProvider.updateRate()` carries only a `nonReentrant` modifier — no access control. Any EOA or contract can call it at any time. [1](#0-0) 

The function fetches `latestRate = getLatestRate()` and immediately encodes it without any zero-check before dispatching via LayerZero.

**Step 2 — `getLatestRate()` can return 0**

`RSETHMultiChainRateProvider.getLatestRate()` delegates directly to `ILRTOracle(rsETHPriceOracle).rsETHPrice()` with no floor or sanity check. [2](#0-1) 

The `ILRTOracle` interface declares `rsETHPrice()` as a plain `uint256` return with no guaranteed lower bound. [3](#0-2) 

If `rsETHPrice()` returns 0 (e.g., transient oracle arithmetic edge-case, or all underlying price feeds returning stale/zero data), the zero value is encoded and dispatched cross-chain.

**Step 3 — `lzReceive()` stores zero unconditionally**

`CrossChainRateReceiver.lzReceive()` decodes the payload and writes it to `rate` with no zero-check. [4](#0-3) 

**Step 4 — Division-by-zero in both pool contracts**

`RSETHPool.viewSwapRsETHAmountAndFee` divides by `rsETHToETHrate` (sourced from `getRate()` → `CrossChainRateReceiver.rate`) with no zero guard. [5](#0-4) 

`RSETHPoolNoWrapper.viewSwapRsETHAmountAndFee` has the identical pattern. [6](#0-5) 

Both `deposit()` functions call `viewSwapRsETHAmountAndFee` unconditionally, so every deposit reverts while `rate == 0`. [7](#0-6) [8](#0-7) 

## Impact Explanation

All ETH and token deposits into `RSETHPool` and `RSETHPoolNoWrapper` revert with a Solidity panic (division by zero) for the entire window between the zero-rate `lzReceive` and the next valid non-zero rate update. No funds are lost, but the pool fails to deliver its promised exchange service. This matches **Low — Contract fails to deliver promised returns, but doesn't lose value**.

## Likelihood Explanation

`updateRate()` is permissionless, so any caller can trigger it at the moment `rsETHPrice()` returns 0. The LRTOracle is the protocol's own oracle (not a third-party oracle excluded by SECURITY.md), and its `rsETHPrice()` return value has no on-chain floor enforced in the cross-chain path. A transient zero from the oracle's arithmetic (e.g., zero total ETH in pool during an edge-case state) is sufficient. The window of impact persists until the next successful non-zero `updateRate()` call propagates through LayerZero.

## Recommendation

1. **In `MultiChainRateProvider.updateRate()`**: add `require(latestRate > 0, "rate cannot be zero")` before encoding and sending. [1](#0-0) 

2. **In `CrossChainRateReceiver.lzReceive()`**: add `require(_rate > 0, "rate cannot be zero")` before writing to `rate`. [4](#0-3) 

3. Optionally add a staleness/sanity bound (e.g., rate must be within ±X% of the previous rate) to guard against extreme oracle deviations.

## Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// 1. Deploy a mock LRTOracle that returns 0 for rsETHPrice()
contract MockLRTOracle {
    function rsETHPrice() external pure returns (uint256) { return 0; }
}

// 2. Deploy RSETHMultiChainRateProvider with the mock oracle
// 3. Call provider.updateRate{value: fee}()
//    → encodes 0, sends via LayerZero
// 4. Simulate lzReceive on CrossChainRateReceiver:
//    receiver.lzReceive(srcChainId, srcAddress, 0, abi.encode(uint256(0)));
//    → rate is set to 0
// 5. Call RSETHPool.viewSwapRsETHAmountAndFee(1 ether)
//    → PANICS: division by zero (0x12)
// 6. Call RSETHPool.deposit{value: 1 ether}("ref")
//    → REVERTS: all deposits bricked until next valid rate update
```

Foundry fork test plan: fork Arbitrum mainnet, deploy `MockLRTOracle`, wire it to `RSETHMultiChainRateProvider`, call `updateRate()`, simulate `lzReceive` with `abi.encode(uint256(0))` on the deployed `CrossChainRateReceiver`, then assert `RSETHPool.deposit` reverts with panic `0x12`.

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

**File:** contracts/interfaces/ILRTOracle.sol (L31-31)
```text
    function rsETHPrice() external view returns (uint256);
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
