# [?] Fix `compute_quotient_eval_within_domain` overflow

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/consensus-specs
Published: 2023-02-16
Source: https://github.com/ethereum/consensus-specs/commit/c7ac9ccea38cce05b5c8e0812e04e3c4e5bc6847
Type: security-commit

## Details
Fix `compute_quotient_eval_within_domain` overflow

## Patch
### specs/deneb/polynomial-commitments.md
```diff
@@ -459,7 +459,7 @@ def compute_quotient_eval_within_domain(z: BLSFieldElement,
         f_i = int(BLS_MODULUS) + int(polynomial[i]) - int(y) % BLS_MODULUS
         numerator = f_i * int(omega_i) % BLS_MODULUS
         denominator = int(z) * (int(BLS_MODULUS) + int(z) - int(omega_i)) % BLS_MODULUS
-        result += div(BLSFieldElement(numerator), BLSFieldElement(denominator))
+        result += int(div(BLSFieldElement(numerator), BLSFieldElement(denominator)))
 
     return BLSFieldElement(result % BLS_MODULUS)
 ```
```
