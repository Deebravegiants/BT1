# [?] tracers: avoid panic on invalid arguments  (#20612)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2020-02-04
Source: https://github.com/celo-org/celo-blockchain/commit/33791dbeb51ce910983d15dda53fd83c05be9bb3
Type: security-commit

## Details
tracers: avoid panic on invalid arguments  (#20612)

* add regression tests for #20611

* eth/tracers: fix panics occurring for invalid params in js-tracers

Co-authored-by: Martin Holst Swende <martin@swende.se>

## Patch
### eth/tracers/tracer.go
```diff
@@ -93,6 +93,15 @@ type memoryWrapper struct {
 
 // slice returns the requested range of memory as a byte slice.
 func (mw *memoryWrapper) slice(begin, end int64) []byte {
+	if end == begin {
+		return []byte{}
+	}
+	if end < begin || begin < 0 {
+		// TODO(karalabe): We can't js-throw from Go inside duktape inside Go. The Go
+		// runtime goes belly up https://github.com/golang/go/issues/15639.
+		log.Warn("Tracer accessed out of bound memory", "offset", begin, "end", end)
+		return nil
+	}
 	if mw.memory.Len() < int(end) {
 		// TODO(karalabe): We can't js-throw from Go inside duktape inside Go. The Go
 		// runtime goes belly up https://github.com/golang/go/issues/15639.
@@ -104,7 +113,7 @@ func (mw *memoryWrapper) slice(begin, end int64) []byte {
 
 // getUint returns the 32 bytes at the specified address interpreted as a uint.
 func (mw *memoryWrapper) getUint(addr int64) *big.Int {
-	if mw.memory.Len() < int(addr)+32 {
+	if mw.memory.Len() < int(addr)+32 || addr < 0 {
 		// TODO(karalabe): We can't js-throw from Go inside duktape inside Go. The Go
 		// runtime goes belly up https://github.com/golang/go/issues/15639.
 		log.Warn("Tracer accessed out of bound memory", "available", mw.memory.Len(), "offset", addr, "size", 32)
@@ -147,7 +156,7 @@ type stackWrapper struct {
 
 // peek returns the nth-from-the-top element of the stack.
 func (sw *stackWrapper) peek(idx int) *big.Int {
-	if len(sw.stack.Data()) <= idx {
+	if len(sw.stack.Data()) <= idx || idx < 0 {
 		// TODO(karalabe): We can't js-throw from Go inside duktape inside Go. The Go
 		// runtime goes belly up https://github.com/golang/go/issues/15639.
 		log.Warn("Tracer accessed out of bound stack", "size", len(sw.stack.Data()), "index", idx)
```

### eth/tracers/tracer_test.go
```diff
@@ -63,6 +63,39 @@ func runTrace(tracer *Tracer) (json.RawMessage, error) {
 	return tracer.GetResult()
 }
 
+// TestRegressionPanicSlice tests that we don't panic on bad arguments to memory access
+func TestRegressionPanicSlice(t *testing.T) {
+	tracer, err := New("{depths: [], step: function(log) { this.depths.push(log.memory.slice(-1,-2)); }, fault: function() {}, result: function() { return this.depths; }}")
+	if err != nil {
+		t.Fatal(err)
+	}
+	if _, err = runTrace(tracer); err != nil {
+		t.Fatal(err)
+	}
+}
+
+// TestRegressionPanicSlice tests that we don't panic on bad arguments to stack peeks
+func TestRegressionPanicPeek(t *testing.T) {
+	tracer, err := New("{depths: [], step: function(log) { this.depths.push(log.stack.peek(-1)); }, fault: function() {}, result: function() { return this.depths; }}")
+	if err != nil {
+		t.Fatal(err)
+	}
+	if _, err = runTrace(tracer); err != nil {
+		t.Fatal(err)
+	}
+}
+
+// TestRegressionPanicSlice tests that we don't panic on bad arguments to memory getUint
+func TestRegressionPanicGetUint(t *testing.T) {
+	tracer, err := New("{ depths: [], step: function(log, db) { this.depths.push(log.memory.getUint(-64));}, fault: function() {}, result: function() { return this.depths; }}")
+	if err != nil {
+		t.Fatal(err)
+	}
+	if _, err = runTrace(tracer); err != nil {
+		t.Fatal(err)
+	}
+}
+
 func TestTracing(t *testing.T) {
 	tracer, err := New("{count: 0, step: function() { this.count += 1; }, fault: function() {}, result: function() { return this.count; }}")
 	if err != nil {
```
