# [?] fix: Add bounds check to circle_two_adic_generator to prevent underflow (#1130)

## Summary
Severity: Unknown
Chain: ZK
Component: Plonky3/Plonky3
Published: 2025-11-07
Source: https://github.com/Plonky3/Plonky3/commit/a6deb7146fdccdb58dde6061a9fdcd7cba794423
Type: security-commit

## Details
fix: Add bounds check to circle_two_adic_generator to prevent underflow (#1130)

## Patch
### mersenne-31/src/complex.rs
```diff
@@ -30,6 +30,7 @@ impl ComplexExtendable for Mersenne31 {
         // 1584694829*u + 311014874
         // sage: assert(g.multiplicative_order() == 2^31)
         // sage: assert(g.norm() == 1)
+        assert!(bits <= Self::CIRCLE_TWO_ADICITY);
         let base = Complex::new_complex(Self::new(311_014_874), Self::new(1_584_694_829));
         base.exp_power_of_2(Self::CIRCLE_TWO_ADICITY - bits)
     }
```
