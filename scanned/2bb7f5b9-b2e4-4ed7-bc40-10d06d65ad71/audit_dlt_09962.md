# [?] fix(StETH): check uint128 overflow on share mint

## Summary
Severity: Unknown
Chain: Lido
Component: lidofinance/core
Published: 2025-10-01
Source: https://github.com/lidofinance/core/commit/ac68c5c69928edc1f2d1ea79f41dab60bcb82f5c
Type: security-commit

## Details
fix(StETH): check uint128 overflow on share mint

## Patch
### contracts/0.4.24/StETH.sol
```diff
@@ -92,6 +92,11 @@ contract StETH is IERC20, Pausable {
     bytes32 internal constant TOTAL_SHARES_POSITION_LOW128 =
         0x6038150aecaa250d524370a0fdcdec13f2690e0723eaf277f41d7cae26b359e6;
 
+    /**
+     * @dev Bitmask for high 128 bits of 256-bit slot
+     */
+    uint256 constant internal UINT128_HIGH_MASK = ~uint256(0) << 128;
+
     /**
       * @notice An executed shares transfer from `sender` to `recipient`.
       *
@@ -515,6 +520,8 @@ contract StETH is IERC20, Pausable {
         require(_recipient != address(this), "MINT_TO_STETH_CONTRACT");
 
         newTotalShares = _getTotalShares().add(_sharesAmount);
+        require(newTotalShares & UINT128_HIGH_MASK == 0, "SHARES_OVERFLOW");
+
         TOTAL_SHARES_POSITION_LOW128.setLowUint128(newTotalShares);
 
         shares[_recipient] = shares[_recipient].add(_sharesAmount);
```

### test/0.4.24/steth.test.ts
```diff
@@ -495,4 +495,28 @@ describe("StETH.sol:non-ERC-20 behavior", () => {
       );
     });
   });
+
+  context("_mintShares", () => {
+    it("Reverts when minting to zero address", async () => {
+      await expect(steth.harness__mintShares(ZeroAddress, 1000n)).to.be.revertedWith("MINT_TO_ZERO_ADDR");
+    });
+
+    it("Reverts when minting to stETH contract", async () => {
+      await expect(steth.harness__mintShares(steth, 1000n)).to.be.revertedWith("MINT_TO_STETH_CONTRACT");
+    });
+
+    it("Reverts when minting shares overflow 128 bits", async () => {
+      await expect(steth.harness__mintShares(holder, 2n ** 128n)).to.be.revertedWith("SHARES_OVERFLOW");
+    });
+
+    it("Reverts when minting shares overflow 256 bits", async () => {
+      await expect(steth.harness__mintShares(holder, 2n ** 256n - 1n)).to.be.revertedWith("MATH_ADD_OVERFLOW");
+    });
+
+    it("Mints shares to the recipient", async () => {
+      const balanceOfHolderBefore = await steth.balanceOf(holder);
+      await expect(steth.harness__mintShares(holder, 1000n)).to.not.be.reverted;
+      expect(await steth.sharesOf(holder)).to.equal(balanceOfHolderBefore + 1000n);
+    });
+  });
 });
```
