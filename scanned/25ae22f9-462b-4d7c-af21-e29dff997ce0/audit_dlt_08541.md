# [?] AVM: Avoid panics while type checking bad immediates (#5271)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2023-04-10
Source: https://github.com/algorand/go-algorand/commit/e5ad8eebc962a0411995aea057490e93135540d9
Type: security-commit

## Details
AVM: Avoid panics while type checking bad immediates (#5271)

## Patch
### data/transactions/logic/assembler.go
```diff
@@ -1158,8 +1158,9 @@ func asmDefault(ops *OpStream, spec *OpSpec, args []string) error {
 	return nil
 }
 
-// getImm interprets the arg at index argIndex as an immediate
-func getImm(args []string, argIndex int) (int, bool) {
+// getImm interprets the arg at index argIndex as an immediate that must be
+// between -128 and 127 (if signed=true) or between 0 and 255 (if signed=false)
+func getImm(args []string, argIndex int, signed bool) (int, bool) {
 	if len(args) <= argIndex {
 		return 0, false
 	}
@@ -1169,6 +1170,15 @@ func getImm(args []string, argIndex int) (int, bool) {
 	if err != nil {
 		return 0, false
 	}
+	if signed {
+		if n < -128 || n > 127 {
+			return 0, false
+		}
+	} else {
+		if n < 0 || n > 255 {
+			return 0, false
+		}
+	}
 	return int(n), true
 }
 
@@ -1193,7 +1203,7 @@ func typeSwap(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, err
 }
 
 func typeDig(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, error) {
-	n, ok := getImm(args, 0)
+	n, ok := getImm(args, 0, false)
 	if !ok {
 		return nil, nil, nil
 	}
@@ -1210,7 +1220,7 @@ func typeDig(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, erro
 }
 
 func typeBury(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, error) {
-	n, ok := getImm(args, 0)
+	n, ok := getImm(args, 0, false)
 	if !ok {
 		return nil, nil, nil
 	}
@@ -1242,7 +1252,7 @@ func typeBury(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, err
 }
 
 func typeFrameDig(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, error) {
-	n, ok := getImm(args, 0)
+	n, ok := getImm(args, 0, true)
 	if !ok {
 		return nil, nil, nil
 	}
@@ -1263,7 +1273,7 @@ func typeFrameDig(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes,
 }
 
 func typeFrameBury(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, error) {
-	n, ok := getImm(args, 0)
+	n, ok := getImm(args, 0, true)
 	if !ok {
 		return nil, nil, nil
 	}
@@ -1351,7 +1361,7 @@ func typeSetBit(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, e
 }
 
 func typeCover(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, error) {
-	n, ok := getImm(args, 0)
+	n, ok := getImm(args, 0, false)
 	if !ok {
 		return nil, nil, nil
 	}
@@ -1373,7 +1383,7 @@ func typeCover(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, er
 }
 
 func typeUncover(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, error) {
-	n, ok := getImm(args, 0)
+	n, ok := getImm(args, 0, false)
 	if !ok {
 		return nil, nil, nil
 	}
@@ -1402,7 +1412,7 @@ func typeTxField(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes,
 }
 
 func typeStore(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, error) {
-	scratchIndex, ok := getImm(args, 0)
+	scratchIndex, ok := getImm(args, 0, false)
 	if !ok {
 		return nil, nil, nil
 	}
@@ -1428,16 +1438,16 @@ func typeStores(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, e
 }
 
 func typeLoad(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, error) {
-	scratchIndex, ok := getImm(args, 0)
+	scratchIndex, ok := getImm(args, 0, false)
 	if !ok {
 		return nil, nil, nil
 	}
 	return nil, StackTypes{pgm.scratchSpace[scratchIndex]}, nil
 }
 
 func typeProto(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, error) {
-	a, aok := getImm(args, 0)
-	_, rok := getImm(args, 1)
+	a, aok := getImm(args, 0, false)
+	_, rok := getImm(args, 1, false)
 	if !aok || !rok {
 		return nil, nil, nil
 	}
@@ -1462,15 +1472,15 @@ func typeLoads(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, er
 }
 
 func typePopN(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, error) {
-	n, ok := getImm(args, 0)
+	n, ok := getImm(args, 0, false)
 	if !ok {
 		return nil, nil, nil
 	}
 	return anyTypes(n), nil, nil
 }
 
 func typeDupN(pgm *ProgramKnowledge, args []string) (StackTypes, StackTypes, error) {
-	n, ok := getImm(args, 0)
+	n, ok := getImm(args, 0, false)
 	if !ok {
 		return nil, nil, nil
 	}
```

### data/transactions/logic/assembler_test.go
```diff
@@ -3284,6 +3284,34 @@ add:
 	require.EqualError(t, err, "0: invalid syntax: not#pragma")
 }
 
+func TestAssembleImmediateRanges(t *testing.T) {
+	partitiontest.PartitionTest(t)
+	t.Parallel()
+
+	/* Perhaps all of these "unable to parse" errors could be improved to
+	   discuss limits rather than bailout when the immediate is, in fact, an
+	   integer. */
+
+	testProg(t, "int 1; store 0;", AssemblerMaxVersion)
+	testProg(t, "load 255;", AssemblerMaxVersion)
+
+	testProg(t, "int 1; store -1000;", AssemblerMaxVersion,
+		Expect{1, "store unable to parse..."})
+	testProg(t, "load -100;", AssemblerMaxVersion,
+		Expect{1, "load unable to parse..."})
+	testProg(t, "int 1; store 256;", AssemblerMaxVersion,
+		Expect{1, "store i beyond 255: 256"})
+
+	testProg(t, "frame_dig -1;", AssemblerMaxVersion)
+	testProg(t, "frame_dig 127;", AssemblerMaxVersion)
+	testProg(t, "int 1; frame_bury -128;", AssemblerMaxVersion)
+
+	testProg(t, "frame_dig 128;", AssemblerMaxVersion,
+		Expect{1, "frame_dig unable to parse..."})
+	testProg(t, "int 1; frame_bury -129;", AssemblerMaxVersion,
+		Expect{1, "frame_bury unable to parse..."})
+}
+
 func TestAssembleMatch(t *testing.T) {
 	partitiontest.PartitionTest(t)
 	t.Parallel()
```
