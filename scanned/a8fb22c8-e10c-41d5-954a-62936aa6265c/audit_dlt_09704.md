# [?] params/confp: panic invalid pointer; guard nils in config compatibility checks

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2023-02-21
Source: https://github.com/etclabscore/core-geth/commit/957a202f6c79a67961326ddfce9788db96f1f2b6
Type: security-commit

## Details
params/confp: panic invalid pointer; guard nils in config compatibility checks

Date: 2023-02-21 14:00:12-08:00
Signed-off-by: meows <b5c6@protonmail.com>

## Patch
### params/confp/configurator.go
```diff
@@ -221,13 +221,27 @@ func compatible(headBlock *big.Int, headTime *uint64, a, b ctypes.ChainConfigura
 				continue
 			}
 
-			// Check blocks.
-			if err := func(c1, c2, head *big.Int) *ConfigCompatError {
+			// Tolerates nil values.
+			check := func(c1, c2, head *big.Int) *ConfigCompatError {
 				if isBlockForkIncompatible(c1, c2, head) {
 					return newBlockCompatError("incompatible fork value: "+aNames[i], c1, c2)
 				}
 				return nil
-			}(new(big.Int).SetUint64(*afn()), new(big.Int).SetUint64(*bFns[i]()), headBlock); err != nil {
+			}
+
+			// Call the respective functions; these return pointers.
+			// We need to dereference them to get the actual values for the comparison
+			// before converting to big.Int pointers for the actual check.
+			av := afn()
+			bv := bFns[i]()
+			var aBig, bBig *big.Int
+			if av != nil {
+				aBig = new(big.Int).SetUint64(*av)
+			}
+			if bv != nil {
+				bBig = new(big.Int).SetUint64(*bv)
+			}
+			if err := check(aBig, bBig, headBlock); err != nil {
 				return err
 			}
 		}
@@ -256,12 +270,13 @@ func compatible(headBlock *big.Int, headTime *uint64, a, b ctypes.ChainConfigura
 			}
 
 			// Check blocks.
-			if err := func(c1, c2, head *uint64) *ConfigCompatError {
+			check := func(c1, c2, head *uint64) *ConfigCompatError {
 				if isTimeForkIncompatible(c1, c2, head) {
 					return newTimestampCompatError("incompatible fork value: "+aNames[i], c1, c2)
 				}
 				return nil
-			}(afn(), bFns[i](), headTime); err != nil {
+			}
+			if err := check(afn(), bFns[i](), headTime); err != nil {
 				return err
 			}
 		}
```
