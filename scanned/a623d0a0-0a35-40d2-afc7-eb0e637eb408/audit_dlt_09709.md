# [?] core/vm: PTAL hacky(?) fix to panic on jump table creation

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2022-01-19
Source: https://github.com/etclabscore/core-geth/commit/f3ff4d9ee64eca70978bb732d7d03b37931ec804
Type: security-commit

## Details
core/vm: PTAL hacky(?) fix to panic on jump table creation

Date: 2022-01-18 17:35:54-08:00
Signed-off-by: meows <b5c6@protonmail.com>

## Patch
### core/vm/interpreter.go
```diff
@@ -94,7 +94,7 @@ func NewEVMInterpreter(evm *EVM, cfg Config) *EVMInterpreter {
 	// We use the STOP instruction to see whether
 	// the jump table was initialised. If it was not
 	// we'll set the default jump table.
-	if cfg.JumpTable[STOP] == nil {
+	if cfg.JumpTable == nil || cfg.JumpTable[STOP] == nil {
 		var jt = instructionSetForConfig(evm.chainConfig, evm.Context.BlockNumber)
 		cfg.JumpTable = &jt
 
```
