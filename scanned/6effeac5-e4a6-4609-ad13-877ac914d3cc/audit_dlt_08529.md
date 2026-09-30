# [?] Fix haddock crash on CI.

## Summary
Severity: Unknown
Chain: Cardano
Component: IntersectMBO/plutus
Published: 2020-09-22
Source: https://github.com/IntersectMBO/plutus/commit/597d8639c49d74c1d85029b9f76bf1a68b150477
Type: security-commit

## Details
Fix haddock crash on CI.

## Patch
### nix/haskell.nix
```diff
@@ -63,6 +63,7 @@ let
             marlowe.doHaddock = false;
             plutus-use-cases.doHaddock = false;
             plutus-ledger.doHaddock = false;
+            plutus-benchmark.doHaddock = false;
             # FIXME: Haddock mysteriously gives a spurious missing-home-modules warning
             plutus-tx-plugin.doHaddock = false;
 
```
