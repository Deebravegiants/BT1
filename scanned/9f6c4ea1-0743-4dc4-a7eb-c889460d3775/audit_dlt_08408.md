# [?] fix(math): fix panic on Uint.BigInt() (#18228)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2023-10-24
Source: https://github.com/cosmos/cosmos-sdk/commit/ff3ec258732029ae7aaea6067a8f476640b21917
Type: security-commit

## Details
fix(math): fix panic on Uint.BigInt() (#18228)

## Patch
### math/CHANGELOG.md
```diff
@@ -42,6 +42,7 @@ Ref: https://github.com/commitizen/conventional-commit-types/blob/v3.0.0/index.j
 
 ### Bug Fixes
 
+* [#18228](https://github.com/cosmos/cosmos-sdk/pull/18228) Fix panic when calling `BigInt()` on an uninitialized `Uint`.
 * [#18214](https://github.com/cosmos/cosmos-sdk/pull/18214) Ensure that modifying the argument to `NewUIntFromBigInt` doesn't mutate the returned value.
 * [#18211](https://github.com/cosmos/cosmos-sdk/pull/18211) RelativePow now returns 1 when 0^0, before it was returning the scale factor.
 * [#17725](https://github.com/cosmos/cosmos-sdk/pull/17725) Fix state break in ApproxRoot. This has been present since math/v1.0.1. It changed the rounding behavior at precision end in an intermediary division from banker's to truncation. The truncation occurs from binary right shift in the case of square roots. The change is now reverted back to banker's rounding universally for any root.
```

### math/uint.go
```diff
@@ -15,6 +15,9 @@ type Uint struct {
 
 // BigInt converts Uint to big.Int
 func (u Uint) BigInt() *big.Int {
+	if u.IsNil() {
+		return nil
+	}
 	return new(big.Int).Set(u.i)
 }
 
```

### math/uint_test.go
```diff
@@ -69,6 +69,8 @@ func (s *uintTestSuite) TestUintPanics() {
 	s.Require().Panics(func() { uintmin.Sub(sdkmath.OneUint()) })
 	s.Require().Panics(func() { uintmin.Decr() })
 
+	s.Require().NotPanics(func() { sdkmath.Uint{}.BigInt() })
+
 	s.Require().Equal(uint64(0), sdkmath.MinUint(sdkmath.ZeroUint(), sdkmath.OneUint()).Uint64())
 	s.Require().Equal(uint64(1), sdkmath.MaxUint(sdkmath.ZeroUint(), sdkmath.OneUint()).Uint64())
 
```
