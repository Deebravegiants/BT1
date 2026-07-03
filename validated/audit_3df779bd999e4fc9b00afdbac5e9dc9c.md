### Title
`setSlippageTolerance` Allows `BASIS_POINTS_DIVISOR` (10000), Causing All `bridgeTokenToL1` Calls to Revert — (`contracts/bridges/TACWETHBridge.sol`)

---

### Summary

`setSlippageTolerance` uses a strict `>` check, permitting `slippageTolerance = 10_000`. When set to that value, `getMinAmount` always computes `0` and reverts with `InvalidMinAmount`, bricking every bridge call until the admin resets the value.

---

### Finding Description

`setSlippageTolerance` validates with:

```solidity
if (newSlippageTolerance > BASIS_POINTS_DIVISOR) revert InvalidSlippageTolerance();
``` [1](#0-0) 

This allows `newSlippageTolerance = 10_000` (equal to `BASIS_POINTS_DIVISOR`). The same off-by-one exists in the constructor. [2](#0-1) 

`getMinAmount` then computes:

```
minAmount = amount * (10_000 - 10_000) / 10_000 = 0
```

and immediately reverts:

```solidity
if (minAmount == 0) revert InvalidMinAmount();
``` [3](#0-2) 

`bridgeTokenToL1` calls `getNativeFee` (which calls `getMinAmount`) and then constructs `SendParam` with `minAmountLD: getMinAmount(amount)`, so both paths revert for any non-zero `amount`. [4](#0-3) 

---

### Impact Explanation

All `bridgeTokenToL1` calls revert with `InvalidMinAmount` for any non-zero amount. No funds are lost (tokens are never transferred before the revert), but the bridge delivers no cross-chain transfers until the admin resets `slippageTolerance`. This matches **Low — contract fails to deliver promised returns, but doesn't lose value**.

---

### Likelihood Explanation

The root cause is a contract-level input validation bug (off-by-one `>` vs `>=`), not a malicious admin. An admin can trigger this accidentally by setting 100% slippage tolerance (a semantically plausible intent: "accept any received amount"). No key compromise or governance capture is required — only a single admin call to a function that explicitly permits the value.

---

### Recommendation

Change both validation checks from `>` to `>=`:

```solidity
// constructor
if (_slippageTolerance >= BASIS_POINTS_DIVISOR) revert InvalidSlippageTolerance();

// setSlippageTolerance
if (newSlippageTolerance >= BASIS_POINTS_DIVISOR) revert InvalidSlippageTolerance();
``` [5](#0-4) 

This ensures `slippageTolerance` can never reach `10_000`, so `getMinAmount` always returns a positive value.

---

### Proof of Concept

```solidity
// 1. Admin sets slippageTolerance to BASIS_POINTS_DIVISOR
bridge.setSlippageTolerance(10_000); // succeeds — no revert

// 2. Any user attempts to bridge
// bridgeTokenToL1 -> getNativeFee -> getMinAmount(amount)
// minAmount = amount * (10000 - 10000) / 10000 = 0
// → revert InvalidMinAmount()
bridge.bridgeTokenToL1{value: ...}(recipient, 1 ether); // reverts
```

`getMinAmount` with `slippageTolerance = 10_000`: [6](#0-5)

### Citations

**File:** contracts/bridges/TACWETHBridge.sol (L70-72)
```text
        if (_slippageTolerance > BASIS_POINTS_DIVISOR) {
            revert InvalidSlippageTolerance();
        }
```

**File:** contracts/bridges/TACWETHBridge.sol (L86-93)
```text
    function setSlippageTolerance(uint256 newSlippageTolerance) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (newSlippageTolerance > BASIS_POINTS_DIVISOR) {
            revert InvalidSlippageTolerance();
        }

        slippageTolerance = newSlippageTolerance;
        emit SlippageToleranceUpdated(newSlippageTolerance);
    }
```

**File:** contracts/bridges/TACWETHBridge.sol (L108-123)
```text
        uint256 nativeFee = getNativeFee(amount, recipient);

        // Check if the msg.value is equal to the native fee for bridging
        if (msg.value != nativeFee) {
            revert InvalidNativeFee();
        }

        // Transfer the tokens to this contract
        IERC20(address(wethOFT)).safeTransferFrom(msg.sender, address(this), amount);

        // Bridge WETH to the L1 recipient
        SendParam memory sendParam = SendParam({
            dstEid: dstLzChainId,
            to: getReceiver(recipient),
            amountLD: amount,
            minAmountLD: getMinAmount(amount),
```

**File:** contracts/bridges/TACWETHBridge.sol (L169-181)
```text
    function getMinAmount(uint256 amount) public view returns (uint256) {
        if (amount == 0) {
            revert ZeroAmount();
        }

        uint256 minAmount = amount * (BASIS_POINTS_DIVISOR - slippageTolerance) / BASIS_POINTS_DIVISOR;

        if (minAmount == 0) {
            revert InvalidMinAmount();
        }

        return minAmount;
    }
```
