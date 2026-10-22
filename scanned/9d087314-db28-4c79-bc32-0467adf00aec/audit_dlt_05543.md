# [?] C01: native ERC20 double spend (#779)

## Summary
Severity: Unknown
Chain: Uniswap
Component: Uniswap/v4-core
Published: 2024-07-14
Source: https://github.com/Uniswap/v4-core/commit/4287ddf9c35bf37c6a81e45cfe2fb9dcae00fa28
Type: security-commit

## Details
C01: native ERC20 double spend (#779)

* Add test verifying vulnerability

* c-01: enforcing strict sync, send, settle rules

* make sync external

* add comment explaining the NativeERC20 contract

* Moved AlreadySynced() error to Reserves

* Implemented comment feedback

* reverted renaming

* reverted renaming of constant

* renaming for clarity

* only reset currency after erc20 settle

* updated snaps

* correctly cast to address

* updated comment in settle function

* updated NativeERC20 test

* resolved feedback

* Updated getReserves in TransientStateLibrary

* fixed tests after renaming getReserves

* Rename reset to resetCurrency

---------

Co-authored-by: gretzke <daniel@gretzke.de>
Co-authored-by: Alice Henshaw <henshawalice@gmail.com>

### .forge-snapshots/add liquidity to already existing position with salt.snap
```diff
@@ -1 +1 @@
-144833
\ No newline at end of file
+144394
\ No newline at end of file
```

### .forge-snapshots/addLiquidity CA fee.snap
```diff
@@ -1 +1 @@
-319014
\ No newline at end of file
+318575
\ No newline at end of file
```

### .forge-snapshots/addLiquidity with empty hook.snap
```diff
@@ -1 +1 @@
-273990
\ No newline at end of file
+273551
\ No newline at end of file
```

### .forge-snapshots/addLiquidity with native token.snap
```diff
@@ -1 +1 @@
-135309
\ No newline at end of file
+134864
\ No newline at end of file
```

### .forge-snapshots/create new liquidity to a position with salt.snap
```diff
@@ -1 +1 @@
-293038
\ No newline at end of file
+292527
\ No newline at end of file
```

### .forge-snapshots/donate gas with 1 token.snap
```diff
@@ -1 +1 @@
-104644
\ No newline at end of file
+104438
\ No newline at end of file
```

### .forge-snapshots/donate gas with 2 tokens.snap
```diff
@@ -1 +1 @@
-144524
\ No newline at end of file
+144067
\ No newline at end of file
```

### .forge-snapshots/extsload getFeeGrowthGlobals.snap
```diff
@@ -1 +1 @@
-704
\ No newline at end of file
+726
\ No newline at end of file
```

### .forge-snapshots/extsload getFeeGrowthInside.snap
```diff
@@ -1 +1 @@
-375
\ No newline at end of file
+397
\ No newline at end of file
```

### .forge-snapshots/extsload getLiquidity.snap
```diff
@@ -1 +1 @@
-375
\ No newline at end of file
+397
\ No newline at end of file
```

### .forge-snapshots/extsload getPositionInfo.snap
```diff
@@ -1 +1 @@
-874
\ No newline at end of file
+896
\ No newline at end of file
```

### .forge-snapshots/extsload getPositionLiquidity.snap
```diff
@@ -1 +1 @@
-375
\ No newline at end of file
+397
\ No newline at end of file
```
