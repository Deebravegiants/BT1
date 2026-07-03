### Title
`getMinAmount` Integer Truncation Causes `getNativeFee` and `bridgeTokenToL1` to Revert for Small Amounts — (`contracts/bridges/TACWETHBridge.sol`)

---

### Summary

`getNativeFee` and `bridgeTokenToL1` both call `getMinAmount(amount)` internally. `getMinAmount` computes `minAmount` via integer division and reverts with `InvalidMinAmount` if the result truncates to zero. This creates a silent dead zone: any `amount` small enough that `amount * (BASIS_POINTS_DIVISOR - slippageTolerance) < BASIS_POINTS_DIVISOR` will cause both the view quote function and the actual bridge function to revert, even though the only documented rejection condition is `amount == 0`.

---

### Finding Description

`getMinAmount` computes:

```solidity
uint256 minAmount = amount * (BASIS_POINTS_DIVISOR - slippageTolerance) / BASIS_POINTS_DIVISOR;
if (minAmount == 0) {
    revert InvalidMinAmount();
}
``` [1](#0-0) 

The truncation condition is: `amount < BASIS_POINTS_DIVISOR / (BASIS_POINTS_DIVISOR - slippageTolerance)`.

Concrete cases:

| `slippageTolerance` | Failing amounts |
|---|---|
| 1 (0.01%) | `amount = 1` (`1 * 9999 / 10000 = 0`) |
| 5000 (50%) | `amount = 1` (`1 * 5000 / 10000 = 0`) |
| 9999 (99.99%) | `amount` in `[1, 9999]` |
| 10000 (100%) | **all amounts** (`0 * anything = 0`) |

The constructor and `setSlippageTolerance` both use a strict `>` check, meaning `slippageTolerance = BASIS_POINTS_DIVISOR` (10 000) is explicitly permitted:

```solidity
if (_slippageTolerance > BASIS_POINTS_DIVISOR) {
    revert InvalidSlippageTolerance();
}
``` [2](#0-1) 

At `slippageTolerance = 10_000`, `getMinAmount` reverts for every possible `amount`, completely bricking the bridge. At any non-zero `slippageTolerance`, `amount = 1 wei` always fails.

`getNativeFee` calls `getMinAmount` at line 153, so the revert propagates to the view function:

```solidity
minAmountLD: getMinAmount(amount),
``` [3](#0-2) 

`bridgeTokenToL1` calls `getNativeFee` at line 108, so the revert also propagates to the state-changing bridge entry point:

```solidity
uint256 nativeFee = getNativeFee(amount, recipient);
``` [4](#0-3) 

---

### Impact Explanation

The contract's only documented guard against invalid amounts is `ZeroAmount` (amount == 0). Any `amount > 0` is implicitly promised to be bridgeable. However, due to integer truncation in `getMinAmount`, amounts in the range `(0, BASIS_POINTS_DIVISOR / (BASIS_POINTS_DIVISOR - slippageTolerance))` silently revert at both the quoting stage (`getNativeFee`) and the execution stage (`bridgeTokenToL1`). No funds are lost, but the contract fails to deliver its promised bridging service for these amounts. Scope: **Low — contract fails to deliver promised returns, but doesn't lose value**.

---

### Likelihood Explanation

- With any non-zero `slippageTolerance` (the normal operational state), `amount = 1 wei` always fails.
- The admin can set `slippageTolerance = 10_000` without triggering any revert, which breaks the bridge for all amounts.
- UI/integrator layers calling `getNativeFee` as a view to pre-check feasibility will receive an unexpected revert rather than a fee quote, breaking UX flows silently.

---

### Recommendation

Replace the hard revert in `getMinAmount` with a floor of 1 when the computed value truncates to zero, or add a minimum-amount pre-check in `getNativeFee` that returns a descriptive error before calling `getMinAmount`. Additionally, change the `slippageTolerance` guard to `>=` to reject the degenerate 100% case:

```solidity
// In constructor and setSlippageTolerance:
if (newSlippageTolerance >= BASIS_POINTS_DIVISOR) revert InvalidSlippageTolerance();

// In getMinAmount:
uint256 minAmount = amount * (BASIS_POINTS_DIVISOR - slippageTolerance) / BASIS_POINTS_DIVISOR;
if (minAmount == 0) minAmount = 1; // floor to avoid spurious revert
```

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Foundry fuzz test (run: forge test --match-test testGetNativeFeeNeverRevertsForPositiveAmount -vvv)
contract TACWETHBridgeFuzzTest is Test {
    TACWETHBridge bridge;

    function setUp() public {
        // Deploy with slippageTolerance = 500 (5%)
        bridge = new TACWETHBridge(admin, wethOFT, dstChainId, 500);
    }

    function testGetMinAmountRevertsForSmallAmount() public {
        // amount = 1, slippageTolerance = 500
        // minAmount = 1 * (10000 - 500) / 10000 = 9500 / 10000 = 0 → InvalidMinAmount
        vm.expectRevert(TACWETHBridge.InvalidMinAmount.selector);
        bridge.getMinAmount(1);
    }

    function testGetNativeFeeRevertsForSmallAmount() public {
        // getNativeFee calls getMinAmount internally → same revert
        vm.expectRevert(TACWETHBridge.InvalidMinAmount.selector);
        bridge.getNativeFee(1, address(0xBEEF));
    }

    function testSlippageTolerance10000BricksAllAmounts(uint256 amount) public {
        vm.assume(amount > 0);
        // Admin sets slippageTolerance to 10_000 — allowed by the > guard
        vm.prank(admin);
        bridge.setSlippageTolerance(10_000);

        // getMinAmount = amount * 0 / 10000 = 0 → InvalidMinAmount for every amount
        vm.expectRevert(TACWETHBridge.InvalidMinAmount.selector);
        bridge.getMinAmount(amount);
    }
}
```

### Citations

**File:** contracts/bridges/TACWETHBridge.sol (L70-72)
```text
        if (_slippageTolerance > BASIS_POINTS_DIVISOR) {
            revert InvalidSlippageTolerance();
        }
```

**File:** contracts/bridges/TACWETHBridge.sol (L108-108)
```text
        uint256 nativeFee = getNativeFee(amount, recipient);
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
