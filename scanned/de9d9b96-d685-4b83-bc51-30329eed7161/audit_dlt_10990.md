# [?] fix overflow when compile to wasm32 (#812)

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2024-07-02
Source: https://github.com/succinctlabs/sp1/commit/c551ab71ffa7fd17ebc7cb65a8eefac83f1c59b4
Type: security-commit

## Details
fix overflow when compile to wasm32 (#812)

## Patch
### recursion/circuit/src/challenger.rs
```diff
@@ -125,7 +125,7 @@ pub fn reduce_32<C: Config>(builder: &mut Builder<C>, vals: &[Felt<C::F>]) -> Va
         let bits = builder.num2bits_f_circuit(*val);
         let val = builder.bits2num_v_circuit(&bits);
         builder.assign(result, result + val * power);
-        power *= C::N::from_canonical_usize(1usize << 32);
+        power *= C::N::from_canonical_u64(1u64 << 32);
     }
     result
 }
```
