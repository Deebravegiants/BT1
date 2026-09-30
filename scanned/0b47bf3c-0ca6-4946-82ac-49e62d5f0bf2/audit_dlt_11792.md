# [?] Cast `MAX_SAMPLES_PER_BLOCK * POINTS_PER_SAMPLE` to `int` to avoid `uint64` overflow

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/consensus-specs
Published: 2021-04-05
Source: https://github.com/ethereum/consensus-specs/commit/37fe8068cae08a3fad7d8d525ec6a339ac21abcc
Type: security-commit

## Details
Cast `MAX_SAMPLES_PER_BLOCK * POINTS_PER_SAMPLE` to `int` to avoid `uint64` overflow

## Patch
### specs/sharding/beacon-chain.md
```diff
@@ -108,7 +108,7 @@ The following values are (non-configurable) constants used throughout the specif
 | - | - |
 | `G1_SETUP` | Type `List[G1]`. The G1-side trusted setup `[G, G*s, G*s**2....]`; note that the first point is the generator. |
 | `G2_SETUP` | Type `List[G2]`. The G2-side trusted setup `[G, G*s, G*s**2....]` |
-| `ROOT_OF_UNITY` | `pow(PRIMITIVE_ROOT_OF_UNITY, (MODULUS - 1) // (MAX_SAMPLES_PER_BLOCK * POINTS_PER_SAMPLE), MODULUS)` |
+| `ROOT_OF_UNITY` | `pow(PRIMITIVE_ROOT_OF_UNITY, (MODULUS - 1) // int(MAX_SAMPLES_PER_BLOCK * POINTS_PER_SAMPLE), MODULUS)` |
 
 ### Gwei values
 
```
