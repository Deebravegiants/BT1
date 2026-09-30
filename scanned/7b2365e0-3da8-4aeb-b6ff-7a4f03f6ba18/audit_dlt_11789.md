# [?] int casting to avoid underflow

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/consensus-specs
Published: 2022-09-27
Source: https://github.com/ethereum/consensus-specs/commit/5a0d84ed01a978196dfc54ed3633eabffc52c840
Type: security-commit

## Details
int casting to avoid underflow

## Patch
### specs/eip4844/polynomial-commitments.md
```diff
@@ -329,7 +329,7 @@ def compute_kzg_proof(polynomial: Polynomial, z: BLSFieldElement) -> KZGProof:
 
     # Make sure we won't divide by zero during division
     assert z not in ROOTS_OF_UNITY
-    denominator_poly = [(x - z) % BLS_MODULUS for x in bit_reversal_permutation(ROOTS_OF_UNITY)]
+    denominator_poly = [(int(x) - z) % BLS_MODULUS for x in bit_reversal_permutation(ROOTS_OF_UNITY)]
 
     # Calculate quotient polynomial by doing point-by-point division
     quotient_polynomial = [div(a, b) for a, b in zip(polynomial_shifted, denominator_poly)]
```
