### Title
Uninitialized `rsETHPrice` (Zero) Causes Division-by-Zero in Deposits and Zero-Asset Withdrawals — (File: `contracts/LRTDepositPool.sol`, `contracts/LRTOracle.sol`, `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTOracle.rsETHPrice` is never set in `initialize()` and defaults to `0`. Two downstream consumers read this value without a zero-guard: `LRTDepositPool.getRsETHAmountToMint()` divides by it (division-by-zero revert, blocking all deposits), and `LRTWithdrawalManager.getExpectedAssetAmount()` multiplies by it (silently returns `0`, allowing a withdrawal request to be recorded with `expectedAssetAmount = 0`).

---

### Finding Description

`LRTOracle.initialize()` sets only `lrtConfig` and emits an event. The storage variable `rsETHPrice` is left at its Solidity default of `0`:

```solidity
// contracts/LRTOracle.sol:64-68
function initialize(address lrtConfigAddr) external initializer {
    UtilLib.checkNonZeroAddress(lrtConfigAddr);
    lrtConfig = ILRTConfig(lrtConfigAddr);
    emit UpdatedLRTConfig(lrtConfigAddr);
}
```

`rsETHPrice` is only written by `_updateRsETHPrice()`, which is reached via the public `updateRSETHPrice()`. The first call when `rsethSupply == 0` sets it to `1 ether`:

```solidity
// contracts/LRTOracle.sol:218-222
if (rsethSupply == 0) {
    rsETHPrice = 1 ether;
    highestRsethPrice = 1 ether;
    return;
}
```

Until that call is made, `rsETHPrice == 0`.

**Path 1 — Deposit revert (division by zero):**

```solidity
// contracts/LRTDepositPool.sol:520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.rsETHPrice()` returns `0` → Solidity 0.8 panics with division-by-zero → every call to `depositETH()` / `depositAsset()` reverts.

**Path 2 — Zero-asset withdrawal (silent fund loss):**

```solidity
// contracts/LRTWithdrawalManager.sol:593
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

`lrtOracle.rsETHPrice() == 0` → `underlyingToReceive = 0`. `initiateWithdrawal()` then proceeds:

```solidity
// contracts/LRTWithdrawalManager.sol:166-175
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);
if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
assetsCommitted[asset] += expectedAssetAmount; // += 0
_addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount); // stores 0
```

The user's rsETH is transferred to the contract and later burned in `unlockQueue()`, while `request.expectedAssetAmount == 0` means `_transferAsset(asset, user, 0)` — the user receives nothing.

---

### Impact Explanation

**Path 1**: All deposits revert until `updateRSETHPrice()` is called — **temporary freezing of funds** (Medium).

**Path 2**: If rsETH tokens exist in any holder's wallet while `rsETHPrice == 0` (e.g., after a new oracle deployment before price initialization, or if rsETH was minted directly by admin), any holder who calls `initiateWithdrawal()` will have their rsETH permanently burned for zero underlying assets — **permanent freezing / direct theft of user funds** (Critical).

---

### Likelihood Explanation

In a fresh deployment the window exists between `initialize()` and the first `updateRSETHPrice()` call. More concretely, if the protocol ever deploys a new `LRTOracle` implementation and updates `LRTConfig.contractMap` to point to it before calling `updateRSETHPrice()`, all existing rsETH holders are exposed to Path 2. The `setContract()` call is a single admin transaction; the gap between it and the price initialization is a realistic race window. Likelihood is **Medium**.

---

### Recommendation

Initialize `rsETHPrice` to `1 ether` directly inside `initialize()`, mirroring the safe-default logic already present in `_updateRsETHPrice()`:

```solidity
function initialize(address lrtConfigAddr) external initializer {
    UtilLib.checkNonZeroAddress(lrtConfigAddr);
    lrtConfig = ILRTConfig(lrtConfigAddr);
    rsETHPrice = 1 ether;          // safe default, analog to snap state wrapper
    highestRsethPrice = 1 ether;
    emit UpdatedLRTConfig(lrtConfigAddr);
}
```

Additionally, add a zero-guard in `getRsETHAmountToMint()` and `getExpectedAssetAmount()` to revert explicitly rather than silently returning `0`.

---

### Proof of Concept

1. Deploy `LRTOracle` proxy and call `initialize(lrtConfigAddr)`.
2. Observe `rsETHPrice == 0` (storage slot never written).
3. **Path 1**: Call `LRTDepositPool.depositETH{value: 1 ether}(0, "")` → reverts with Panic(0x12) (division by zero) at `LRTDepositPool.sol:520`.
4. **Path 2** (oracle swap scenario): Admin mints rsETH directly to `alice`, then deploys a new `LRTOracle` and calls `lrtConfig.setContract(LRT_ORACLE, newOracle)` before calling `updateRSETHPrice()`. Alice calls `initiateWithdrawal(stETH, aliceRsETHBalance, "")`. `getExpectedAssetAmount` returns `0`. Alice's rsETH is transferred to `LRTWithdrawalManager`. After `unlockQueue()` burns it, Alice calls `completeWithdrawal` and receives `0` stETH — her rsETH is permanently destroyed for nothing. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L64-68)
```text
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
    }
```

**File:** contracts/LRTOracle.sol (L218-222)
```text
        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }
```

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L166-176)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

```

**File:** contracts/LRTWithdrawalManager.sol (L589-594)
```text
        // setup oracle contract
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
