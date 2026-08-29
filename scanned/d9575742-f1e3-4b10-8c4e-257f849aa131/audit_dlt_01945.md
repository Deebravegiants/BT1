# [?] fixed race condition in the prepareWitnesses function: before the fix, goroutine used to change numEffWitnesses but the top-level method did not wait 

## Summary
Severity: Unknown
Chain: Linea
Component: Consensys/linea-monorepo
Published: 2025-05-06
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/3bede19e492619f65978ec162c2b301befeaecf8
Type: security-commit

## Details
fixed race condition in the prepareWitnesses function: before the fix, goroutine used to change numEffWitnesses but the top-level method did not wait for goroutine to complete, that caused the usage of the numEffWitnesses before it change in the other methods (#939)
