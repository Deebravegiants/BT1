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

## Patch
### prover/protocol/query/plonk_in_wizard.go
```diff
@@ -4,6 +4,7 @@ import (
 	"errors"
 	"fmt"
 	"sync"
+	"sync/atomic"
 
 	"github.com/consensys/gnark-crypto/field/koalabear"
 
@@ -70,10 +71,8 @@ type PlonkInWizard struct {
 	// first time [PlonkInWizard.GetNbPublicInputs] is called and saved there.
 	nbPublicInputs int `serde:"omit"`
 
-	// nbPublicInputs loaded is a flag indicating whether we need to compute the
-	// number of public input. It is not using [sync.Once] that way we don't need
-	// to initialize the value.
-	nbPublicInputsLoaded bool      `serde:"omit"`
+	// nbPublicInputsLoaded is set to 1 atomically once nbPublicInputs is computed.
+	nbPublicInputsLoaded uint32    `serde:"omit"`
 	uuid                 uuid.UUID `serde:"omit"`
 }
 
@@ -238,16 +237,23 @@ func (piw *PlonkInWizard) CheckGnark(api frontend.API, run ifaces.GnarkRuntime)
 	utils.Panic("UNSUPPORTED : can't check a PlonkInWizard query directly into the circuit, query-name=%v", piw.Name())
 }
 
+// nbPublicInputsMu guards the lazy load below for queries shared across
+// concurrent provers.
+var nbPublicInputsMu sync.Mutex
+
 // GetNbPublicInputs returns the number of public inputs of the circuit provided
 // by the query.
 func (piw *PlonkInWizard) GetNbPublicInputs() int {
-	// The lazy loading does not need to be thread-safe as (1) it is not
-	// meant to be run concurrently and (2) the initialization is idempotent
-	// anyway.
-	if !piw.nbPublicInputsLoaded {
-		piw.nbPublicInputsLoaded = true
-		nbPub, _ := gnarkutil.CountVariables(piw.Circuit)
-		piw.nbPublicInputs = nbPub
+	// Thread-safe lazy load: the query is shared across a module's concurrent
+	// segment provers (limitless), which call this during proving.
+	if atomic.LoadUint32(&piw.nbPublicInputsLoaded) == 0 {
+		nbPublicInputsMu.Lock()
+		if piw.nbPublicInputsLoaded == 0 {
+			nbPub, _ := gnarkutil.CountVariables(piw.Circuit)
+			piw.nbPublicInputs = nbPub
+			atomic.StoreUint32(&piw.nbPublicInputsLoaded, 1)
+		}
+		nbPublicInputsMu.Unlock()
 	}
 	return piw.nbPublicInputs
 }
```

### prover/symbolic/compiler.go
```diff
@@ -1,6 +1,8 @@
 package symbolic
 
 import (
+	"sync"
+	"sync/atomic"
 	"unsafe"
 
 	"github.com/consensys/gnark-crypto/field/koalabear/extensions"
@@ -11,6 +13,10 @@ import (
 	"github.com/consensys/linea-monorepo/prover/utils/parallel"
 )
 
+// compileMu guards the lazy Compile, since a compiled board may be shared
+// across concurrent provers. Evaluate's fast path stays lock-free.
+var compileMu sync.Mutex
+
 // Program is a compiled expression board ready for evaluation.
 
 type opCode uint8
@@ -41,7 +47,7 @@ func areAllConstants(inp []smartvectors.SmartVector) bool {
 }
 
 func (b *ExpressionBoard) Evaluate(inputs []smartvectors.SmartVector) smartvectors.SmartVector {
-	if b.ProgramNodesCount != len(b.Nodes) {
+	if atomic.LoadUint32(&b.compiled) == 0 {
 		b.Compile()
 	}
 
@@ -152,11 +158,26 @@ func (b *ExpressionBoard) Evaluate(inputs []smartvectors.SmartVector) smartvecto
 
 // Compile compiles the expression board into a program.
 func (b *ExpressionBoard) Compile() {
+	compileMu.Lock()
+	defer compileMu.Unlock()
+
+	// Double-check: another prover may have compiled while we waited.
+	if atomic.LoadUint32(&b.compiled) == 1 {
+		return
+	}
+
 	if len(b.Nodes) == 0 {
 		b.Bytecode = nil
 		b.Constants = nil
 		b.NumSlots = 0
 		b.ProgramNodesCount = 0
+		atomic.StoreUint32(&b.compiled, 1)
+		return
+	}
+
+	// Already compiled (e.g. deserialized with bytecode intact).
+	if b.ProgramNodesCount == len(b.Nodes) {
+		atomic.StoreUint32(&b.compiled, 1)
 		return
 	}
 
@@ -245,6 +266,7 @@ func (b *ExpressionBoard) Compile() {
 	b.NumSlots = nextSlot
 	b.ResultSlot = slots[len(b.Nodes)-1]
 	b.ProgramNodesCount = len(b.Nodes)
+	atomic.StoreUint32(&b.compiled, 1)
 }
 
 // VM for Base elements
```

### prover/symbolic/expression_board.go
```diff
@@ -22,6 +22,10 @@ type ExpressionBoard struct {
 	NumSlots          int
 	ResultSlot        int
 	ProgramNodesCount int
+
+	// compiled is set to 1 atomically once the program above is built. Unexported
+	// so serde skips it: it resets to 0 on load, triggering one compile on use.
+	compiled uint32
 }
 
 // BytecodeStats holds counts of each opcode kind in a compiled board.
```
