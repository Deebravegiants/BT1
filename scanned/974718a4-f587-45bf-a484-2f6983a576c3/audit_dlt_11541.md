# [?] fix(assignment): nil pointer dereference (#1634)

## Summary
Severity: Unknown
Chain: EigenDA
Component: Layr-Labs/eigenda
Published: 2025-06-03
Source: https://github.com/Layr-Labs/eigenda/commit/4f57e6095d10c8ba63cb510db23dac1d0f5de8c7
Type: security-commit

## Details
fix(assignment): nil pointer dereference (#1634)

* Fix assignment pointer error

* Update core/v2/assignment_test.go

Co-authored-by: Daniel Mancia <21249320+dmanc@users.noreply.github.com>

---------

Co-authored-by: Daniel Mancia <21249320+dmanc@users.noreply.github.com>

## Patch
### core/v2/assignment.go
```diff
@@ -115,6 +115,13 @@ func AddAssignmentsForQuorum(
 	for _, id := range orderedOps {
 		newAssignmentIndicesCount := len(dummyAssignments[id].Indices)
 
+		if _, ok := assignments[id]; !ok {
+			newAssignments[id] = &Assignment{
+				Indices: make([]uint32, 0, newAssignmentIndicesCount),
+			}
+			continue
+		}
+
 		if newAssignmentIndicesCount > len(assignments[id].Indices) {
 			newAssignmentIndicesCount = len(assignments[id].Indices)
 		}
```

### core/v2/assignment_test.go
```diff
@@ -153,6 +153,61 @@ func TestTwoQuorums(t *testing.T) {
 	}
 }
 
+func TestTwoQuorumsReverseOrder(t *testing.T) {
+
+	stakes := map[core.QuorumID]map[core.OperatorID]int{
+		1: {
+			mock.MakeOperatorId(0): 1,
+			mock.MakeOperatorId(1): 10,
+			mock.MakeOperatorId(2): 1,
+			mock.MakeOperatorId(3): 1,
+			mock.MakeOperatorId(4): 3,
+		},
+		0: {
+			mock.MakeOperatorId(0): 2,
+			mock.MakeOperatorId(1): 1,
+			mock.MakeOperatorId(2): 10,
+			mock.MakeOperatorId(3): 1,
+		},
+	}
+
+	dat, err := mock.NewChainDataMock(stakes)
+	assert.NoError(t, err)
+
+	state := dat.GetTotalOperatorState(context.Background(), 0)
+
+	assignmentsBothQuorums, err := corev2.GetAssignmentsForBlob(state.OperatorState, blobParams, []core.QuorumID{0, 1})
+	assert.NoError(t, err)
+	assert.Len(t, assignmentsBothQuorums, 5)
+
+	assignmentsQuorum0, err := corev2.GetAssignmentsForBlob(state.OperatorState, blobParams, []core.QuorumID{1})
+	assert.NoError(t, err)
+	assert.Len(t, assignmentsQuorum0, 5)
+
+	assignmentsQuorum1, err := corev2.GetAssignmentsForBlob(state.OperatorState, blobParams, []core.QuorumID{0})
+	assert.NoError(t, err)
+	assert.Len(t, assignmentsQuorum1, 4)
+
+	// Check that the length of the assignment for each operator is equal to the maximum of the assignments for that operator in each quorum
+	for id := range assignmentsBothQuorums {
+
+		// Get the bigger assignemnt between the two quorums
+		maxChunks := uint32(0)
+		assignment, ok := assignmentsQuorum0[id]
+		if ok {
+			maxChunks = assignment.NumChunks()
+		}
+		assignment, ok = assignmentsQuorum1[id]
+		if ok {
+			if assignment.NumChunks() > maxChunks {
+				maxChunks = assignment.NumChunks()
+			}
+		}
+		fmt.Println(id, assignmentsBothQuorums[id].NumChunks(), maxChunks)
+		assert.LessOrEqual(t, assignmentsBothQuorums[id].NumChunks(), maxChunks)
+	}
+}
+
 func TestManyQuorums(t *testing.T) {
 
 	testCases := []uint8{1, 2, 3, 4, 5, 10, 15, 20, 50, 100, 200, 255}
```
