# [?] fix(prover): resolve data race in limitless prover (#3442)

## Summary
Severity: Unknown
Chain: Linea
Component: Consensys/linea-monorepo
Published: 2026-06-26
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/ce8db72e2f80846e7d0778bc2900546ab9953b16
Type: security-commit

## Details
fix(prover): resolve data race in limitless prover (#3442)

* fix(prover): make ExpressionBoard.Compile concurrency-safe

The limitless pipeline shares one cached compiled circuit across a
module's concurrent segment provers. Compile mutates the board in place
on first Evaluate, so they raced, corrupting constraint evaluation.

Guard Compile with a mutex and an atomic flag; Evaluate's fast path
stays lock-free. The flag is unexported so serde skips it.

* fix(prover): make PlonkInWizard.GetNbPublicInputs concurrency-safe

The query is shared across a module's concurrent segment provers, which
call it during proving; its lazy load raced. Guard with a mutex and an
atomic flag (mirrors the ExpressionBoard.Compile fix).
