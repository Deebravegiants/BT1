# [?] Add reentrancy test to swap path fixes (#352)

## Summary
Severity: Unknown
Chain: Balancer
Component: balancer/balancer-v3-monorepo
Published: 2024-03-12
Source: https://github.com/balancer/balancer-v3-monorepo/commit/a8e9e6850402dd7fc16b1e2f297e4aced9676dc1
Type: security-commit

## Details
Add reentrancy test to swap path fixes (#352)

## Patch
### pkg/vault/.forge-snapshots/routerAddLiquidityNative.snap
```diff
@@ -1 +1 @@
-402936
\ No newline at end of file
+403037
\ No newline at end of file
```

### pkg/vault/.forge-snapshots/routerAddLiquidityWETH.snap
```diff
@@ -1 +1 @@
-342584
\ No newline at end of file
+342685
\ No newline at end of file
```

### pkg/vault/.forge-snapshots/routerRemoveLiquidityNative.snap
```diff
@@ -1 +1 @@
-267393
\ No newline at end of file
+267513
\ No newline at end of file
```

### pkg/vault/.forge-snapshots/routerRemoveLiquidityWETH.snap
```diff
@@ -1 +1 @@
-229687
\ No newline at end of file
+229807
\ No newline at end of file
```

### pkg/vault/.forge-snapshots/routerSwapSingleTokenExactInNative.snap
```diff
@@ -1 +1 @@
-346432
\ No newline at end of file
+346409
\ No newline at end of file
```

### pkg/vault/.forge-snapshots/routerSwapSingleTokenExactInWETH.snap
```diff
@@ -1 +1 @@
-293681
\ No newline at end of file
+293658
\ No newline at end of file
```

### pkg/vault/.forge-snapshots/vaultAddLiquiditySingleTokenExactOut.snap
```diff
@@ -1 +1 @@
-276155
\ No newline at end of file
+276137
\ No newline at end of file
```

### pkg/vault/.forge-snapshots/vaultAddLiquidityUnbalanced.snap
```diff
@@ -1 +1 @@
-309711
\ No newline at end of file
+309742
\ No newline at end of file
```

### pkg/vault/.forge-snapshots/vaultRemoveLiquidityProportional.snap
```diff
@@ -1 +1 @@
-220121
\ No newline at end of file
+220162
\ No newline at end of file
```

### pkg/vault/.forge-snapshots/vaultRemoveLiquiditySingleTokenExactIn.snap
```diff
@@ -1 +1 @@
-206039
\ No newline at end of file
+206128
\ No newline at end of file
```

### pkg/vault/.forge-snapshots/vaultRemoveLiquiditySingleTokenExactOut.snap
```diff
@@ -1 +1 @@
-211245
\ No newline at end of file
+211330
\ No newline at end of file
```

### pkg/vault/.forge-snapshots/vaultSwapSingleTokenExactIn.snap
```diff
@@ -1 +1 @@
-287281
\ No newline at end of file
+287169
\ No newline at end of file
```
