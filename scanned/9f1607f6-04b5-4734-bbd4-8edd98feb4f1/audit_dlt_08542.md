# [?] AVM: Avoid panics in disassembly when branch instructions are short (#5252)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2023-04-04
Source: https://github.com/algorand/go-algorand/commit/896015f3ecc7592a43d3119cd8ad501a165f6470
Type: security-commit

## Details
AVM: Avoid panics in disassembly when branch instructions are short (#5252)

Additional error information on poorly formed programs.

## Patch
### data/transactions/logic/assembler.go
```diff
@@ -2650,7 +2650,7 @@ func disassemble(dis *disassembleState, spec *OpSpec) (string, error) {
 		out += " "
 		switch imm.kind {
 		case immByte, immInt8:
-			if pc >= len(dis.program) {
+			if pc+1 > len(dis.program) {
 				return "", fmt.Errorf("program end while reading immediate %s for %s",
 					imm.Name, spec.Name)
 			}
@@ -2680,6 +2680,10 @@ func disassemble(dis *disassembleState, spec *OpSpec) (string, error) {
 
 			pc++
 		case immLabel:
+			// decodeBranchOffset assumes it has two bytes to work with
+			if pc+2 > len(dis.program) {
+				return "", fmt.Errorf("program end while reading label for %s", spec.Name)
+			}
 			offset := decodeBranchOffset(dis.program, pc)
 			target := offset + pc + 2
 			var label string
@@ -2744,9 +2748,9 @@ func disassemble(dis *disassembleState, spec *OpSpec) (string, error) {
 			}
 			pc = nextpc
 		case immLabels:
-			targets, nextpc, err := parseSwitch(dis.program, pc)
+			targets, nextpc, err := parseLabels(dis.program, pc)
 			if err != nil {
-				return "", err
+				return "", fmt.Errorf("%w for %s", err, spec.Name)
 			}
 
 			var labels []string
@@ -2873,10 +2877,18 @@ func checkByteImmArgs(cx *EvalContext) error {
 	return err
 }
 
-func parseSwitch(program []byte, pos int) (targets []int, nextpc int, err error) {
+func parseLabels(program []byte, pos int) (targets []int, nextpc int, err error) {
+	if pos >= len(program) {
+		err = errors.New("could not decode label count")
+		return
+	}
 	numOffsets := int(program[pos])
 	pos++
 	end := pos + 2*numOffsets // end of op: offset is applied to this position
+	if end > len(program) {
+		err = errors.New("could not decode labels")
+		return
+	}
 	for i := 0; i < numOffsets; i++ {
 		offset := decodeBranchOffset(program, pos)
 		target := end + offset
```

### data/transactions/logic/assembler_test.go
```diff
@@ -3487,3 +3487,84 @@ warning 2
 	expected = "1 error: 42: super annoying error\n"
 	assertWithMsg(t, expected, b)
 }
+
+// TestDisassembleBadBranch ensures a clean error when a branch has no target.
+func TestDisassembleBadBranch(t *testing.T) {
+	partitiontest.PartitionTest(t)
+	t.Parallel()
+
+	for _, br := range []byte{0x40, 0x41, 0x42} {
+		dis, err := Disassemble([]byte{2, br})
+		require.Error(t, err, dis)
+		dis, err = Disassemble([]byte{2, br, 0x01})
+		require.Error(t, err, dis)
+
+		// It would be reasonable to error here, since it's a jump past the end.
+		dis, err = Disassemble([]byte{2, br, 0x00, 0x05})
+		require.NoError(t, err, dis)
+
+		// It would be reasonable to error here, since it's a back jump in v2.
+		dis, err = Disassemble([]byte{2, br, 0xff, 0x02})
+		require.NoError(t, err, dis)
+
+		dis, err = Disassemble([]byte{2, br, 0x00, 0x01, 0x00})
+		require.NoError(t, err)
+	}
+}
+
+// TestDisassembleBadSwitch ensures a clean error when a switch ends early
+func TestDisassembleBadSwitch(t *testing.T) {
+	partitiontest.PartitionTest(t)
+	t.Parallel()
+
+	source := `
+    int 1
+	switch label1 label2
+	label1:
+    label2:
+	`
+	ops, err := AssembleStringWithVersion(source, AssemblerMaxVersion)
+	require.NoError(t, err)
+
+	dis, err := Disassemble(ops.Program)
+	require.NoError(t, err, dis)
+
+	// chop off all the labels, but keep the label count
+	dis, err = Disassemble(ops.Program[:len(ops.Program)-4])
+	require.ErrorContains(t, err, "could not decode labels for switch", dis)
+
+	// chop off before the label count
+	dis, err = Disassemble(ops.Program[:len(ops.Program)-5])
+	require.ErrorContains(t, err, "could not decode label count for switch", dis)
+
+	// chop off half of a label
+	dis, err = Disassemble(ops.Program[:len(ops.Program)-1])
+	require.ErrorContains(t, err, "could not decode labels for switch", dis)
+}
+
+// TestDisassembleBadMatch ensures a clean error when a match ends early
+func TestDisassembleBadMatch(t *testing.T) {
+	partitiontest.PartitionTest(t)
+	t.Parallel()
+
+	source := `
+    int 40
+    int 45
+    int 40
+	match label1 label2
+	label1:
+    label2:
+	`
+	ops, err := AssembleStringWithVersion(source, AssemblerMaxVersion)
+	require.NoError(t, err)
+
+	dis, err := Disassemble(ops.Program)
+	require.NoError(t, err, dis)
+
+	// return the label count, but chop off the labels themselves
+	dis, err = Disassemble(ops.Program[:len(ops.Program)-5])
+	require.ErrorContains(t, err, "could not decode label count for match", dis)
+
+	dis, err = Disassemble(ops.Program[:len(ops.Program)-1])
+	require.ErrorContains(t, err, "could not decode labels for match", dis)
+}
```
