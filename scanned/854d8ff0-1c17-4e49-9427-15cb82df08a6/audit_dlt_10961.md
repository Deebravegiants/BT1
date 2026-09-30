# [?] fix: fix race condition when compiling circuits in parallel (#676)

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark
Published: 2023-05-05
Source: https://github.com/Consensys-Incorporated/gnark/commit/5dae2c51d8551b3632f8b5cb5d66db8195f46cc4
Type: security-commit

## Details
fix: fix race condition when compiling circuits in parallel (#676)

## Patch
### constraint/blueprint.go
```diff
@@ -48,21 +48,21 @@ type BlueprintSolvable interface {
 // BlueprintR1C indicates that the blueprint and associated calldata encodes a R1C
 type BlueprintR1C interface {
 	Blueprint
-	CompressR1C(c *R1C) []uint32
+	CompressR1C(c *R1C, to *[]uint32)
 	DecompressR1C(into *R1C, instruction Instruction)
 }
 
 // BlueprintSparseR1C indicates that the blueprint and associated calldata encodes a SparseR1C.
 type BlueprintSparseR1C interface {
 	Blueprint
-	CompressSparseR1C(c *SparseR1C) []uint32
+	CompressSparseR1C(c *SparseR1C, to *[]uint32)
 	DecompressSparseR1C(into *SparseR1C, instruction Instruction)
 }
 
 // BlueprintHint indicates that the blueprint and associated calldata encodes a hint.
 type BlueprintHint interface {
 	Blueprint
-	CompressHint(HintMapping) []uint32
+	CompressHint(h HintMapping, to *[]uint32)
 	DecompressHint(h *HintMapping, instruction Instruction)
 }
 
```

### constraint/blueprint_hint.go
```diff
@@ -34,7 +34,7 @@ func (b *BlueprintGenericHint) DecompressHint(h *HintMapping, inst Instruction)
 	h.OutputRange.End = inst.Calldata[j+1]
 }
 
-func (b *BlueprintGenericHint) CompressHint(h HintMapping) []uint32 {
+func (b *BlueprintGenericHint) CompressHint(h HintMapping, to *[]uint32) {
 	nbInputs := 1 // storing nb inputs
 	nbInputs++    // hintID
 	nbInputs++    // len(h.Inputs)
@@ -45,24 +45,19 @@ func (b *BlueprintGenericHint) CompressHint(h HintMapping) []uint32 {
 
 	nbInputs += 2 // output range start / end
 
-	r := getBuffer(nbInputs)
-	r = append(r, uint32(nbInputs))
-	r = append(r, uint32(h.HintID))
-	r = append(r, uint32(len(h.Inputs)))
+	(*to) = append((*to), uint32(nbInputs))
+	(*to) = append((*to), uint32(h.HintID))
+	(*to) = append((*to), uint32(len(h.Inputs)))
 
 	for _, l := range h.Inputs {
-		r = append(r, uint32(len(l)))
+		(*to) = append((*to), uint32(len(l)))
 		for _, t := range l {
-			r = append(r, uint32(t.CoeffID()), uint32(t.WireID()))
+			(*to) = append((*to), uint32(t.CoeffID()), uint32(t.WireID()))
 		}
 	}
 
-	r = append(r, h.OutputRange.Start)
-	r = append(r, h.OutputRange.End)
-	if len(r) != nbInputs {
-		panic("invalid")
-	}
-	return r
+	(*to) = append((*to), h.OutputRange.Start)
+	(*to) = append((*to), h.OutputRange.End)
 }
 
 func (b *BlueprintGenericHint) CalldataSize() int {
```

### constraint/blueprint_r1cs.go
```diff
@@ -17,22 +17,20 @@ func (b *BlueprintGenericR1C) NbOutputs(inst Instruction) int {
 	return 0
 }
 
-func (b *BlueprintGenericR1C) CompressR1C(c *R1C) []uint32 {
+func (b *BlueprintGenericR1C) CompressR1C(c *R1C, to *[]uint32) {
 	// we store total nb inputs, len L, len R, len O, and then the "flatten" linear expressions
 	nbInputs := 4 + 2*(len(c.L)+len(c.R)+len(c.O))
-	r := getBuffer(nbInputs)
-	r = append(r, uint32(nbInputs))
-	r = append(r, uint32(len(c.L)), uint32(len(c.R)), uint32(len(c.O)))
+	(*to) = append((*to), uint32(nbInputs))
+	(*to) = append((*to), uint32(len(c.L)), uint32(len(c.R)), uint32(len(c.O)))
 	for _, t := range c.L {
-		r = append(r, uint32(t.CoeffID()), uint32(t.WireID()))
+		(*to) = append((*to), uint32(t.CoeffID()), uint32(t.WireID()))
 	}
 	for _, t := range c.R {
-		r = append(r, uint32(t.CoeffID()), uint32(t.WireID()))
+		(*to) = append((*to), uint32(t.CoeffID()), uint32(t.WireID()))
 	}
 	for _, t := range c.O {
-		r = append(r, uint32(t.CoeffID()), uint32(t.WireID()))
+		(*to) = append((*to), uint32(t.CoeffID()), uint32(t.WireID()))
 	}
-	return r
 }
 
 func (b *BlueprintGenericR1C) DecompressR1C(c *R1C, inst Instruction) {
@@ -80,17 +78,3 @@ func (b *BlueprintGenericR1C) WireWalker(inst Instruction) func(cb func(wire uin
 		appendWires(lenO, offset+2*(lenL+lenR))
 	}
 }
-
-// since frontend is single threaded, to avoid allocating slices at each compress call
-// we transit the compressed output through here
-var bufCalldata []uint32
-
-// getBuffer return a slice with at least the given capacity to use in Compress methods
-// this is obviously not thread safe, but the frontend is single threaded anyway.
-func getBuffer(size int) []uint32 {
-	if cap(bufCalldata) < size {
-		bufCalldata = make([]uint32, 0, size*2)
-	}
-	bufCalldata = bufCalldata[:0]
-	return bufCalldata
-}
```

### constraint/blueprint_scs.go
```diff
@@ -36,17 +36,8 @@ func (b *BlueprintGenericSparseR1C) WireWalker(inst Instruction) func(cb func(wi
 	}
 }
 
-func (b *BlueprintGenericSparseR1C) CompressSparseR1C(c *SparseR1C) []uint32 {
-	bufSCS[0] = c.XA
-	bufSCS[1] = c.XB
-	bufSCS[2] = c.XC
-	bufSCS[3] = c.QL
-	bufSCS[4] = c.QR
-	bufSCS[5] = c.QO
-	bufSCS[6] = c.QM
-	bufSCS[7] = c.QC
-	bufSCS[8] = uint32(c.Commitment)
-	return bufSCS[:]
+func (b *BlueprintGenericSparseR1C) CompressSparseR1C(c *SparseR1C, to *[]uint32) {
+	*to = append(*to, c.XA, c.XB, c.XC, c.QL, c.QR, c.QO, c.QM, c.QC, uint32(c.Commitment))
 }
 
 func (b *BlueprintGenericSparseR1C) DecompressSparseR1C(c *SparseR1C, inst Instruction) {
@@ -189,12 +180,8 @@ func (b *BlueprintSparseR1CMul) WireWalker(inst Instruction) func(cb func(wire u
 	}
 }
 
-func (b *BlueprintSparseR1CMul) CompressSparseR1C(c *SparseR1C) []uint32 {
-	bufSCS[0] = c.XA
-	bufSCS[1] = c.XB
-	bufSCS[2] = c.XC
-	bufSCS[3] = c.QM
-	return bufSCS[:4]
+func (b *BlueprintSparseR1CMul) CompressSparseR1C(c *SparseR1C, to *[]uint32) {
+	*to = append(*to, c.XA, c.XB, c.XC, c.QM)
 }
 
 func (b *BlueprintSparseR1CMul) Solve(s Solver, inst Instruction) error {
@@ -241,14 +228,8 @@ func (b *BlueprintSparseR1CAdd) WireWalker(inst Instruction) func(cb func(wire u
 	}
 }
 
-func (b *BlueprintSparseR1CAdd) CompressSparseR1C(c *SparseR1C) []uint32 {
-	bufSCS[0] = c.XA
-	bufSCS[1] = c.XB
-	bufSCS[2] = c.XC
-	bufSCS[3] = c.QL
-	bufSCS[4] = c.QR
-	bufSCS[5] = c.QC
-	return bufSCS[:6]
+func (b *BlueprintSparseR1CAdd) CompressSparseR1C(c *SparseR1C, to *[]uint32) {
+	*to = append(*to, c.XA, c.XB, c.XC, c.QL, c.QR, c.QC)
 }
 
 func (blueprint *BlueprintSparseR1CAdd) Solve(s Solver, inst Instruction) error {
@@ -298,11 +279,8 @@ func (b *BlueprintSparseR1CBool) WireWalker(inst Instruction) func(cb func(wire
 	}
 }
 
-func (b *BlueprintSparseR1CBool) CompressSparseR1C(c *SparseR1C) []uint32 {
-	bufSCS[0] = c.XA
-	bufSCS[1] = c.QL
-	bufSCS[2] = c.QM
-	return bufSCS[:3]
+func (b *BlueprintSparseR1CBool) CompressSparseR1C(c *SparseR1C, to *[]uint32) {
+	*to = append(*to, c.XA, c.QL, c.QM)
 }
 
 func (blueprint *BlueprintSparseR1CBool) Solve(s Solver, inst Instruction) error {
@@ -325,7 +303,3 @@ func (b *BlueprintSparseR1CBool) DecompressSparseR1C(c *SparseR1C, inst Instruct
 	c.QL = inst.Calldata[1]
 	c.QM = inst.Calldata[2]
 }
-
-// since frontend is single threaded, to avoid allocating slices at each compress call
-// we transit the compressed output through here
-var bufSCS [9]uint32
```

### constraint/core.go
```diff
@@ -3,6 +3,7 @@ package constraint
 import (
 	"fmt"
 	"math/big"
+	"sync"
 
 	"github.com/blang/semver/v4"
 	"github.com/consensys/gnark"
@@ -275,9 +276,16 @@ func (system *System) AddSolverHint(f solver.Hint, input []LinearExpression, nbO
 	}
 
 	blueprint := system.Blueprints[system.genericHint]
-	calldata := blueprint.(BlueprintHint).CompressHint(hm)
 
-	system.AddInstruction(system.genericHint, calldata)
+	// get []uint32 from the pool
+	calldata := getBuffer()
+
+	blueprint.(BlueprintHint).CompressHint(hm, calldata)
+
+	system.AddInstruction(system.genericHint, *calldata)
+
+	// return []uint32 to the pool
+	putBuffer(calldata)
 
 	return
 }
@@ -324,9 +332,16 @@ func (cs *System) AddR1C(c R1C, bID BlueprintID) int {
 	profile.RecordConstraint()
 
 	blueprint := cs.Blueprints[bID]
-	calldata := blueprint.(BlueprintR1C).CompressR1C(&c)
 
-	cs.AddInstruction(bID, calldata)
+	// get a []uint32 from a pool
+	calldata := getBuffer()
+
+	// compress the R1C into a []uint32 and add the instruction
+	blueprint.(BlueprintR1C).CompressR1C(&c, calldata)
+	cs.AddInstruction(bID, *calldata)
+
+	// release the []uint32 to the pool
+	putBuffer(calldata)
 
 	return cs.NbConstraints - 1
 }
@@ -335,9 +350,17 @@ func (cs *System) AddSparseR1C(c SparseR1C, bID BlueprintID) int {
 	profile.RecordConstraint()
 
 	blueprint := cs.Blueprints[bID]
-	calldata := blueprint.(BlueprintSparseR1C).CompressSparseR1C(&c)
 
-	cs.AddInstruction(bID, calldata)
+	// get a []uint32 from a pool
+	calldata := getBuffer()
+
+	// compress the SparceR1C into a []uint32 and add the instruction
+	blueprint.(BlueprintSparseR1C).CompressSparseR1C(&c, calldata)
+
+	cs.AddInstruction(bID, *calldata)
+
+	// release the []uint32 to the pool
+	putBuffer(calldata)
 
 	return cs.NbConstraints - 1
 }
@@ -392,3 +415,30 @@ func (cs *System) GetR1CIterator() R1CIterator {
 func (cs *System) GetSparseR1CIterator() SparseR1CIterator {
 	return SparseR1CIterator{cs: cs}
 }
+
+// bufPool is a pool of buffers used by getBuffer and putBuffer.
+// It is used to avoid allocating buffers for each constraint.
+var bufPool = sync.Pool{
+	New: func() interface{} {
+		r := make([]uint32, 0, 20)
+		return &r
+	},
+}
+
+// getBuffer returns a buffer of at least the given size.
+// The buffer is taken from the pool if it is large enough,
+// otherwise a new buffer is allocated.
+// Caller must call putBuffer when done with the buffer.
+func getBuffer() *[]uint32 {
+	to := bufPool.Get().(*[]uint32)
+	*to = (*to)[:0]
+	return to
+}
+
+// putBuffer returns a buffer to the pool.
+func putBuffer(buf *[]uint32) {
+	if buf == nil {
+		panic("invalid entry in putBuffer")
+	}
+	bufPool.Put(buf)
+}
```

### test/engine.go
```diff
@@ -24,6 +24,7 @@ import (
 	"runtime"
 	"strconv"
 	"strings"
+	"sync/atomic"
 
 	"github.com/consensys/gnark/constraint"
 	"github.com/consensys/gnark/constraint/solver"
@@ -154,11 +155,11 @@ func callDeferred(builder *engine) error {
 var cptAdd, cptMul, cptSub, cptToBinary, cptFromBinary, cptAssertIsEqual uint64
 
 func (e *engine) Add(i1, i2 frontend.Variable, in ...frontend.Variable) frontend.Variable {
-	cptAdd++
+	atomic.AddUint64(&cptAdd, 1)
 	res := new(big.Int)
 	res.Add(e.toBigInt(i1), e.toBigInt(i2))
 	for i := 0; i < len(in); i++ {
-		cptAdd++
+		atomic.AddUint64(&cptAdd, 1)
 		res.Add(res, e.toBigInt(in[i]))
 	}
 	res.Mod(res, e.modulus())
@@ -178,11 +179,11 @@ func (e *engine) MulAcc(a, b, c frontend.Variable) frontend.Variable {
 }
 
 func (e *engine) Sub(i1, i2 frontend.Variable, in ...frontend.Variable) frontend.Variable {
-	cptSub++
+	atomic.AddUint64(&cptSub, 1)
 	res := new(big.Int)
 	res.Sub(e.toBigInt(i1), e.toBigInt(i2))
 	for i := 0; i < len(in); i++ {
-		cptSub++
+		atomic.AddUint64(&cptSub, 1)
 		res.Sub(res, e.toBigInt(in[i]))
 	}
 	res.Mod(res, e.modulus())
@@ -197,7 +198,7 @@ func (e *engine) Neg(i1 frontend.Variable) frontend.Variable {
 }
 
 func (e *engine) Mul(i1, i2 frontend.Variable, in ...frontend.Variable) frontend.Variable {
-	cptMul++
+	atomic.AddUint64(&cptMul, 1)
 	b2 := e.toBigInt(i2)
 	if len(in) == 0 && b2.IsUint64() && b2.Uint64() <= 1 {
 		// special path to avoid useless allocations
@@ -211,7 +212,7 @@ func (e *engine) Mul(i1, i2 frontend.Variable, in ...frontend.Variable) frontend
 	res.Mul(b1, b2)
 	res.Mod(res, e.modulus())
 	for i := 0; i < len(in); i++ {
-		cptMul++
+		atomic.AddUint64(&cptMul, 1)
 		res.Mul(res, e.toBigInt(in[i]))
 		res.Mod(res, e.modulus())
 	}
@@ -251,7 +252,7 @@ func (e *engine) Inverse(i1 frontend.Variable) frontend.Variable {
 }
 
 func (e *engine) ToBinary(i1 frontend.Variable, n ...int) []frontend.Variable {
-	cptToBinary++
+	atomic.AddUint64(&cptToBinary, 1)
 	nbBits := e.FieldBitLen()
 	if len(n) == 1 {
 		nbBits = n[0]
@@ -283,7 +284,7 @@ func (e *engine) ToBinary(i1 frontend.Variable, n ...int) []frontend.Variable {
 }
 
 func (e *engine) FromBinary(v ...frontend.Variable) frontend.Variable {
-	cptFromBinary++
+	atomic.AddUint64(&cptFromBinary, 1)
 	bits := make([]bool, len(v))
 	for i := 0; i < len(v); i++ {
 		be := e.toBigInt(v[i])
@@ -380,7 +381,7 @@ func (e *engine) Cmp(i1, i2 frontend.Variable) frontend.Variable {
 }
 
 func (e *engine) AssertIsEqual(i1, i2 frontend.Variable) {
-	cptAssertIsEqual++
+	atomic.AddUint64(&cptAssertIsEqual, 1)
 	b1, b2 := e.toBigInt(i1), e.toBigInt(i2)
 	if b1.Cmp(b2) != 0 {
 		panic(fmt.Sprintf("[assertIsEqual] %s == %s", b1.String(), b2.String()))
```
