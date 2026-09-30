# [?] fix(sha256):  BuildParentTreeRootsWithNRoutines will panic if n := 0 (#158)

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2024-02-15
Source: https://github.com/berachain/beacon-kit/commit/42adcdf80eb6b7dc199a6f65aa03439bffc16c1a
Type: security-commit

## Details
fix(sha256):  BuildParentTreeRootsWithNRoutines will panic if n := 0 (#158)

* bugfix

* add test

* add test

* add test

* add test

* add test

* add test

* add test

## Patch
### crypto/sha256/hash_tree.go
```diff
@@ -50,33 +50,42 @@ func BuildParentTreeRoots(inputList [][32]byte) ([][32]byte, error) {
 	return BuildParentTreeRootsWithNRoutines(inputList, runtime.GOMAXPROCS(0)-1)
 }
 
-// HashTreeRoot takes a list of roots and hashes them using CPU
-// specific vector instructions. Depending on host machine's specific
-// hardware configuration, using this routine can lead to a significant
-// performance improvement compared to the default method of hashing
-// lists.
+// BuildParentTreeRootsWithNRoutines optimizes the hashing of a list of roots by utilizing
+// CPU-specific vector instructions and parallel processing. This method adapts to the host
+// machine's hardware configuration for potential performance gains over sequential hashing.
 func BuildParentTreeRootsWithNRoutines(inputList [][32]byte, n int) ([][32]byte, error) {
-	if len(inputList)%2 != 0 {
+	// Validate the input list length.
+	inputLength := len(inputList)
+	if inputLength%2 != 0 {
 		return nil, ErrOddLengthTreeRoots
 	}
-	outputList := make([][32]byte, len(inputList)/two)
+
+	// Build output variables
+	outputLength := inputLength / two
+	outputList := make([][32]byte, outputLength)
+
 	// If the input list is small, hash it using the default method since
 	// the overhead of parallelizing the hashing process is not worth it.
-	if len(inputList) < MinParallelizationSize {
+	if inputLength < MinParallelizationSize {
 		return outputList, gohashtree.Hash(outputList, inputList)
 	}
 
 	// Otherwise parallelize the hashing process for large inputs.
-
-	groupSize := len(inputList) / (two * (n + 1))
+	// Take the max(n, 1) to prevent division by 0.
+	groupSize := inputLength / (two * max(n, 1))
+	twiceGroupSize := two * groupSize
 	eg := new(errgroup.Group)
 
 	// if n is 0 the parallelization is disabled and the whole inputList is hashed in the main
 	// goroutine at the end of this function.
-	for j := 0; j < n; j++ {
+	for j := 0; j <= n; j++ {
 		// capture loop variable
 		cj := j
 
+		// Define the segment of the inputList each goroutine will process.
+		segmentStart := cj * twiceGroupSize
+		segmentEnd := min((cj+1)*twiceGroupSize, inputLength)
+
 		// inputList:  [---------------------2*groupSize---------------------]
 		//              ^                    ^                    ^          ^
 		//              |                    |                    |          |
@@ -92,24 +101,13 @@ func BuildParentTreeRootsWithNRoutines(inputList [][32]byte, n int) ([][32]byte,
 		// size of the input by half.
 		eg.Go(func() error {
 			return gohashtree.Hash(
-				outputList[cj*groupSize:], inputList[cj*two*groupSize:(cj+1)*two*groupSize],
+				outputList[cj*groupSize:min((cj+1)*groupSize, outputLength)],
+				inputList[segmentStart:segmentEnd],
 			)
 		})
 	}
 
-	// The last segment of inputList is processed here because the division of the inputList
-	// among the goroutines might leave a remainder segment that is not exactly divisible by
-	// the number of goroutines spawned. This remainder segment is processed in the main goroutine
-	// to ensure all parts of the inputList are hashed.
-	remainderStartIndex := n * two * groupSize
-	if remainderStartIndex < len(inputList) { // Check if there's a remainder segment to process.
-		err := gohashtree.Hash(outputList[n*groupSize:], inputList[remainderStartIndex:])
-		if err != nil {
-			return nil, err
-		}
-	}
-
-	// Wait for all goroutines to finish processing their segments.
+	// Wait for all goroutines to complete.
 	if err := eg.Wait(); err != nil {
 		return nil, err
 	}
```

### crypto/sha256/hash_tree_test.go
```diff
@@ -105,3 +105,11 @@ func Test_GoHashTreeHashConformance(t *testing.T) {
 		})
 	}
 }
+
+func TestBuildParentTreeRootsWithNRoutines_DivisionByZero(t *testing.T) {
+	// Attempt to call BuildParentTreeRootsWithNRoutines with n set to 0
+	// to test handling of division by zero.
+	inputList := make([][32]byte, 10) // Arbitrary size larger than 0
+	_, err := sha256.BuildParentTreeRootsWithNRoutines(inputList, 0)
+	require.NoError(t, err, "BuildParentTreeRootsWithNRoutines should handle n=0 without error")
+}
```
