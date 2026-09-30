# [?] Avoid overflow in PaymasterERC20._erc20Cost rounding (L-15) (#6655)

## Summary
Severity: Unknown
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2026-07-28
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/commit/3419a37554e6aefde6277b34ea0d889fc99915a5
Type: security-commit

## Details
Avoid overflow in PaymasterERC20._erc20Cost rounding (L-15) (#6655)

## Patch
### contracts/account/paymaster/extensions/PaymasterERC20.sol
```diff
@@ -5,6 +5,7 @@ pragma solidity ^0.8.20;
 import {ERC4337Utils, PackedUserOperation} from "../../utils/ERC4337Utils.sol";
 import {IERC20, SafeERC20} from "../../../token/ERC20/utils/SafeERC20.sol";
 import {Math} from "../../../utils/math/Math.sol";
+import {SafeCast} from "../../../utils/math/SafeCast.sol";
 import {Paymaster} from "../Paymaster.sol";
 
 /**
@@ -57,6 +58,7 @@ import {Paymaster} from "../Paymaster.sol";
 abstract contract PaymasterERC20 is Paymaster {
     using ERC4337Utils for *;
     using Math for *;
+    using SafeCast for *;
     using SafeERC20 for IERC20;
 
     /**
@@ -296,8 +298,13 @@ abstract contract PaymasterERC20 is Paymaster {
     function _erc20Cost(uint256 nativeCost, uint256 tokenPerNative) internal view virtual returns (uint256) {
         uint256 denominator = _tokenPerNativeDenominator();
         (uint256 high, ) = nativeCost.mul512(tokenPerNative);
+        // Round up using a saturating add to avoid possible overflow of the rounding.
         return
-            high < denominator ? nativeCost.mulDiv(tokenPerNative, denominator, Math.Rounding.Ceil) : type(uint256).max;
+            high < denominator
+                ? nativeCost.mulDiv(tokenPerNative, denominator).saturatingAdd(
+                    (mulmod(nativeCost, tokenPerNative, denominator) > 0).toUint()
+                )
+                : type(uint256).max;
     }
 
     /// @dev Internal function that allows the withdrawer to extract ERC-20 tokens resulting from gas payments.
```

### test/account/paymaster/PaymasterERC20.test.js
```diff
@@ -323,4 +323,24 @@ describe('PaymasterERC20', function () {
       await expect(this.paymaster.connect(this.other).withdrawTokens(this.token, this.receiver, 10n)).to.be.reverted;
     });
   });
+
+  describe('edge cases', function () {
+    it('_erc20Cost returns max uint256 without reverting when muldiv overflows', async function () {
+      const tokenPerNative = ethers.MaxUint256;
+      const nativeCost = ethers.MaxUint256;
+
+      await expect(this.paymaster.$_erc20Cost(nativeCost, tokenPerNative)).to.eventually.equal(ethers.MaxUint256);
+    });
+
+    it('_erc20Cost rounds up without overflowing when the ceil result saturates', async function () {
+      // Values provided here make the floor division land exactly on type(uint256).max with a non-zero remainder.
+      // We check that the saturating addition that implements the rounding up does not overflow like the default
+      // `Math.mulDiv(..., Math.Rounding.Ceil)` would.
+      const denominator = await this.paymaster.$_tokenPerNativeDenominator();
+      const tokenPerNative = denominator + 1n;
+      const nativeCost = 0xffffffffffffffed8da22e2dbc54606ce862ed069eb19350550de6906b1de3b1n;
+
+      await expect(this.paymaster.$_erc20Cost(nativeCost, tokenPerNative)).to.eventually.equal(ethers.MaxUint256);
+    });
+  });
 });
```
