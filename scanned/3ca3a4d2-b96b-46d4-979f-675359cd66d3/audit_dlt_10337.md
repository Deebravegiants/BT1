# [?] Protect parsing of execution plan from stack overflow (#1044)

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2026-06-12
Source: https://github.com/0xsoniclabs/sonic/commit/26a219618c5d5f5d1c044c62eba40acdc1133ce3
Type: security-commit

## Details
Protect parsing of execution plan from stack overflow (#1044)

## Patch
### gossip/blockproc/bundle/execution_plan.go
```diff
@@ -17,6 +17,7 @@
 package bundle
 
 import (
+	"bytes"
 	"errors"
 	"fmt"
 	"io"
@@ -205,14 +206,77 @@ func (s *ExecutionStep) encode(writer io.Writer) error {
 }
 
 func (s *ExecutionStep) decode(reader io.Reader) error {
+	// The encoded step is read as raw RLP first, so that its nesting depth can be
+	// bounded before it is decoded into the recursive stepEncodingV1 structure.
+	// The plan's nesting depth is limited to MaxGroupNestingDepth, but that limit
+	// is only enforced by validateStep, after decoding. Since both rlp.Decode and
+	// fromEncodingV1 recurse once per nesting level, a maliciously deep plan could
+	// exhaust the goroutine stack during decoding, before validation ever runs
+	// (a single deeply nested envelope decoded by every node would crash the
+	// network). checkStepEncodingDepth guards against this by rejecting overly
+	// deep encodings up front, using a walker whose own recursion is bounded by
+	// the same limit.
+	raw, err := rlp.NewStream(reader, 0).Raw()
+	if err != nil {
+		return err
+	}
+	if err := checkStepEncodingDepth(raw); err != nil {
+		return err
+	}
+
 	var encoding stepEncodingV1
-	if err := rlp.Decode(reader, &encoding); err != nil {
+	if err := rlp.DecodeBytes(raw, &encoding); err != nil {
 		return err
 	}
 	s.fromEncodingV1(encoding)
 	return nil
 }
 
+// maxStepEncodingRlpDepth is the maximum RLP nesting depth permitted for an
+// encoded execution step. It is a loose, consensus-neutral anti-DoS bound used
+// during decoding, distinct from the precise MaxGroupNestingDepth rule enforced
+// later by validateStep. A valid step has at most MaxGroupNestingDepth levels of
+// nested groups; each group level contributes a small constant number of RLP
+// list levels (the step list, its sub-steps list, and a leaf's TxReference
+// list). The factor of 4 leaves ample headroom so that no plan satisfying the
+// MaxGroupNestingDepth rule is ever rejected here, while still bounding the
+// decode recursion far below any level that could exhaust the goroutine stack.
+const maxStepEncodingRlpDepth = 4 * (MaxGroupNestingDepth + 1)
+
+// checkStepEncodingDepth verifies that the RLP nesting depth of an encoded
+// execution step does not exceed maxStepEncodingRlpDepth. It walks the raw RLP
+// structure, descending into every nested list, but stops as soon as the depth
+// limit is exceeded. Its own recursion (and therefore stack usage) is thus
+// bounded by the limit, making it safe to run on untrusted input. It must be
+// called before decoding the raw bytes into the recursive stepEncodingV1
+// structure to prevent stack exhaustion from maliciously deep encodings.
+func checkStepEncodingDepth(raw []byte) error {
+	return checkRlpNestingDepth(rlp.NewStream(bytes.NewReader(raw), 0), 0)
+}
+
+func checkRlpNestingDepth(stream *rlp.Stream, depth int) error {
+	if depth > maxStepEncodingRlpDepth {
+		return fmt.Errorf(
+			"encoded execution step exceeds maximum nesting depth of %d",
+			maxStepEncodingRlpDepth,
+		)
+	}
+	if _, err := stream.List(); err != nil {
+		if err == rlp.ErrExpectedList {
+			// A non-list value (string/byte) can not nest; consume and return.
+			_, err := stream.Raw()
+			return err
+		}
+		return err
+	}
+	for stream.MoreDataInList() {
+		if err := checkRlpNestingDepth(stream, depth+1); err != nil {
+			return err
+		}
+	}
+	return stream.ListEnd()
+}
+
 func (s *ExecutionStep) toEncodingV1() stepEncodingV1 {
 	encoding := stepEncodingV1{}
 	if s.single != nil {
```

### gossip/blockproc/bundle/execution_plan_test.go
```diff
@@ -23,6 +23,7 @@ import (
 
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/crypto"
+	"github.com/ethereum/go-ethereum/rlp"
 	"github.com/stretchr/testify/require"
 	"go.uber.org/mock/gomock"
 )
@@ -460,6 +461,58 @@ func TestExecutionStep_decode_FailsOnInvalidInput(t *testing.T) {
 	require.Error(t, s.decode(bytes.NewReader(data)))
 }
 
+// TestExecutionStep_decode_RejectsDeeplyNestedEncoding ensures that decoding a
+// maliciously deep execution step is rejected up front by the nesting-depth
+// guard, rather than recursing through the whole structure (in rlp.Decode and
+// fromEncodingV1) and exhausting the goroutine stack. The test reaching this
+// assertion without a stack-overflow crash is itself part of what is verified.
+func TestExecutionStep_decode_RejectsDeeplyNestedEncoding(t *testing.T) {
+	require := require.New(t)
+
+	// Encode a valid leaf step to use as the innermost element.
+	leaf := NewTxStep(TxReference{From: common.Address{1}, Hash: common.Hash{2}})
+
+	// Check 1000 and 1 million nested steps, both of which exceed the
+	// MaxGroupNestingDepth limit and should be rejected by the depth guard.
+	// The 1 million case lead to a stack overflow before the guard was
+	// implemented, so is included to ensure the guard is effective.
+	for _, size := range []int{1000, 1_000_000} {
+		nested := leaf
+		for range size {
+			nested = NewAllOfStep(nested)
+		}
+		var buf bytes.Buffer
+		require.NoError(nested.encode(&buf))
+
+		var s ExecutionStep
+		require.ErrorContains(s.decode(bytes.NewReader(buf.Bytes())), "nesting depth")
+	}
+}
+
+// TestExecutionStep_decode_AcceptsEncodingAtNestingLimit ensures the decode-time
+// depth guard never rejects a plan that satisfies the consensus nesting rule
+// (MaxGroupNestingDepth). A step nested exactly to that limit must still decode,
+// validate, and round-trip unchanged.
+func TestExecutionStep_decode_AcceptsEncodingAtNestingLimit(t *testing.T) {
+	require := require.New(t)
+
+	step := NewTxStep(TxReference{From: common.Address{1}, Hash: common.Hash{2}})
+	for range MaxGroupNestingDepth {
+		step = NewAllOfStep(step)
+	}
+
+	// The plan is valid under the precise consensus rule.
+	require.NoError(validateStep(step))
+
+	var buf bytes.Buffer
+	require.NoError(step.encode(&buf))
+	encoded := buf.Bytes()
+
+	var decoded ExecutionStep
+	require.NoError(decoded.decode(bytes.NewReader(encoded)))
+	require.Equal(step, decoded)
+}
+
 func TestExecutionStep_String_PrintsReadableRepresentation(t *testing.T) {
 	ref1 := TxReference{From: common.Address{1}}
 	ref2 := TxReference{From: common.Address{2}}
@@ -526,3 +579,18 @@ func TestExecutionStep_String_PrintsReadableRepresentation(t *testing.T) {
 		})
 	}
 }
+
+func TestCheckRlpNestingDepth_ReachingMaxDepth_ReturnsError(t *testing.T) {
+	require.ErrorContains(t,
+		checkRlpNestingDepth(nil, maxStepEncodingRlpDepth+1),
+		"encoded execution step exceeds maximum nesting depth",
+	)
+}
+
+func TestCheckRlpNestingDepth_EmptyInput_ReturnsAnError(t *testing.T) {
+	stream := rlp.NewStream(bytes.NewReader([]byte("")), 0)
+	require.ErrorContains(t,
+		checkRlpNestingDepth(stream, maxStepEncodingRlpDepth),
+		"EOF",
+	)
+}
```
