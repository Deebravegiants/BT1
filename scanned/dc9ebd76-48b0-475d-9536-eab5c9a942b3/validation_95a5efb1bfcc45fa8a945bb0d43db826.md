The vulnerability is real and traceable in the unmodified contract. Here is the full analysis:

---

### Title
Integer Truncation in `getMinAmount` Causes `InvalidMinAmount` Revert for Dust WETH Amounts - (`contracts/bridges/TACWETHBridge.sol`)

### Summary

`getMinAmount` uses integer division that truncates to zero for small `amount` values, causing `bridgeTokenToL1` to revert with `InvalidMinAmount` even though the `ZeroAmount` guard already passed. No funds are lost (the revert occurs before any token transfer), but the contract fails to bridge any nonzero amount below the truncation threshold.

### Finding Description

`BASIS_POINTS_DIVISOR` is `10_000`. [1](#0-0) 

`getMinAmount` computes:

```solidity
uint256 minAmount = amount * (BASIS_POINTS_DIVISOR - slippageTolerance) / BASIS_POINTS_DIVISOR;
if (minAmount == 0) revert InvalidMinAmount();
``` [2](#0-1) 

For any nonzero `slippageTolerance`, Solidity integer division truncates `minAmount` to `0` whenever:

```
amount < BASIS_POINTS_DIVISOR / (BASIS_POINTS_DIVISOR - slippageTolerance)
```

Concrete examples:

| `slippageTolerance` | Threshold (amounts that truncate to 0) |
|---|---|
| 1 (0.01%) | amount = 1 wei |
| 50 (0.5%) | amount = 1 wei |
| 100 (1%) | amount = 1 wei |
| 5_000 (50%) | amount = 1 wei |
| 9_999 (99.99%) | amounts 1–9_999 wei |

For any nonzero `slippageTolerance`, `amount = 1` always truncates to 0 because `1 * (10_000 - x) / 10_000 = 0` in integer arithmetic for all `x ≥ 1`.

`bridgeTokenToL1` only guards against `amount == 0`: [3](#0-2) 

It then immediately calls `getNativeFee`, which internally calls `getMinAmount`: [4](#0-3) [5](#0-4) 

This revert happens **before** the `safeTransferFrom` at line 116, so no tokens are moved: [6](#0-5) 

The `slippageTolerance` setter only validates `<= BASIS_POINTS_DIVISOR`, so any value from 1 to 10_000 is accepted: [7](#0-6) 

### Impact Explanation

The contract's `ZeroAmount` guard implies any nonzero amount is bridgeable, but this invariant is violated for dust amounts. Users attempting to bridge 1 wei of WETH (or up to `BASIS_POINTS_DIVISOR / (BASIS_POINTS_DIVISOR - slippageTolerance) - 1` wei for high slippage settings) receive an `InvalidMinAmount` revert. No funds are lost. Impact: **Low — contract fails to deliver promised returns, but doesn't lose value**.

### Likelihood Explanation

With typical slippage values (0.5–1%), only `amount = 1 wei` is affected — essentially worthless dust. The likelihood of a real user attempting to bridge exactly 1 wei of WETH is negligible. However, the bug is unconditional for any nonzero `slippageTolerance` and requires no special conditions or privileges to trigger.

### Recommendation

Add a minimum bridgeable amount check before the `ZeroAmount` guard, or replace the `InvalidMinAmount` revert with a floor of 1:

```solidity
// Option A: enforce a minimum amount
uint256 public minBridgeAmount;
if (amount < minBridgeAmount) revert AmountTooSmall();

// Option B: floor minAmount to 1 instead of reverting
uint256 minAmount = amount * (BASIS_POINTS_DIVISOR - slippageTolerance) / BASIS_POINTS_DIVISOR;
if (minAmount == 0) minAmount = 1;
```

Alternatively, document the minimum bridgeable amount as `ceil(BASIS_POINTS_DIVISOR / (BASIS_POINTS_DIVISOR - slippageTolerance))` and enforce it explicitly.

### Proof of Concept

```solidity
// Pseudocode fuzz test
function testFuzz_getMinAmountTruncation(uint256 amount, uint256 slippage) public {
    slippage = bound(slippage, 1, 9_999); // nonzero, below max
    amount = bound(amount, 1, 10_000);    // dust range
    bridge.setSlippageTolerance(slippage);

    uint256 expected = amount * (10_000 - slippage) / 10_000;
    if (expected == 0) {
        vm.expectRevert(TACWETHBridge.InvalidMinAmount.selector);
        bridge.getMinAmount(amount);
    } else {
        assertEq(bridge.getMinAmount(amount), expected);
    }
}
// Concrete: amount=1, slippageTolerance=50 → 1*9950/10000 = 0 → InvalidMinAmount
// Concrete: amount=1, slippageTolerance=9999 → 1*1/10000 = 0 → InvalidMinAmount
```

### Citations

**File:** contracts/bridges/TACWETHBridge.sol (L20-20)
```text
    uint256 public constant BASIS_POINTS_DIVISOR = 10_000;
```

**File:** contracts/bridges/TACWETHBridge.sol (L87-89)
```text
        if (newSlippageTolerance > BASIS_POINTS_DIVISOR) {
            revert InvalidSlippageTolerance();
        }
```

**File:** contracts/bridges/TACWETHBridge.sol (L103-105)
```text
        if (amount == 0) {
            revert ZeroAmount();
        }
```

**File:** contracts/bridges/TACWETHBridge.sol (L108-108)
```text
        uint256 nativeFee = getNativeFee(amount, recipient);
```

**File:** contracts/bridges/TACWETHBridge.sol (L116-116)
```text
        IERC20(address(wethOFT)).safeTransferFrom(msg.sender, address(this), amount);
```

**File:** contracts/bridges/TACWETHBridge.sol (L153-153)
```text
            minAmountLD: getMinAmount(amount),
```

**File:** contracts/bridges/TACWETHBridge.sol (L174-178)
```text
        uint256 minAmount = amount * (BASIS_POINTS_DIVISOR - slippageTolerance) / BASIS_POINTS_DIVISOR;

        if (minAmount == 0) {
            revert InvalidMinAmount();
        }
```
