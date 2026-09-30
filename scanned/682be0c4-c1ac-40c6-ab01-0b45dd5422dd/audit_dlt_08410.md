# [?] fix(math): fix panic in `.Size()` (#17480)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2023-08-21
Source: https://github.com/cosmos/cosmos-sdk/commit/1089f715fc73d861599a55a62725293b2b6e4761
Type: security-commit

## Details
fix(math): fix panic in `.Size()` (#17480)

## Patch
### math/CHANGELOG.md
```diff
@@ -34,7 +34,13 @@ Ref: https://github.com/commitizen/conventional-commit-types/blob/v3.0.0/index.j
 
 # Changelog
 
-## [math/v1.1.0](https://github.com/cosmos/cosmos-sdk/releases/tag/math/v1.1.0) - 2023-08-18
+## [math/v1.1.1](https://github.com/cosmos/cosmos-sdk/releases/tag/math/v1.1.1) - 2023-08-21
+
+### Bug Fixes
+
+* [#17480](https://github.com/cosmos/cosmos-sdk/pull/17480) Fix panic when calling `.Size()` on a nil `math.Int` value.
+
+## [math/v1.1.0](https://github.com/cosmos/cosmos-sdk/releases/tag/math/v1.1.0) - 2023-08-19
 
 ### Features
 
@@ -48,7 +54,7 @@ Ref: https://github.com/commitizen/conventional-commit-types/blob/v3.0.0/index.j
 ### Bug Fixes
 
 * [#17352](https://github.com/cosmos/cosmos-sdk/pull/17352) Ensure that modifying the argument to `NewIntFromBigInt` doesn't mutate the returned value.
-* [#16266](https://github.com/cosmos/cosmos-sdk/pull/16266) fix: legacy dec power mut zero exponent precision.
+* [#16266](https://github.com/cosmos/cosmos-sdk/pull/16266) Fix legacy dec power mut zero exponent precision.
 
 ## [math/v1.0.1](https://github.com/cosmos/cosmos-sdk/releases/tag/math/v1.0.1) - 2023-05-15
 
```

### math/int.go
```diff
@@ -442,6 +442,10 @@ var (
 )
 
 func (i *Int) Size() (size int) {
+	if i == nil || i.i == nil {
+		return 1
+	}
+
 	sign := i.Sign()
 	if sign == 0 { // It is zero.
 		// log*(0) is undefined hence return early.
```

### math/int_test.go
```diff
@@ -531,6 +531,7 @@ var sizeTests = []struct {
 	s    string
 	want int
 }{
+	{"", 1},
 	{"0", 1},
 	{"-0", 1},
 	{"-10", 3},
```
