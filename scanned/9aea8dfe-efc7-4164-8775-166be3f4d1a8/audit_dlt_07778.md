# [?] duties v2 fix no assignment panic  (#15466)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2025-07-03
Source: https://github.com/OffchainLabs/prysm/commit/fac509a3e65426f20053e70c7b3e48e7e2d0f957
Type: security-commit

## Details
duties v2 fix no assignment panic  (#15466)

* adding fix

* preston's suggestion

## Patch
### beacon-chain/core/helpers/beacon_committee.go
```diff
@@ -403,7 +403,7 @@ func AssignmentForValidator(
 			}
 		}
 	}
-	return nil // validator is not scheduled this epoch
+	return &LiteAssignment{} // validator is not scheduled this epoch
 }
 
 // CommitteeAssignments calculates committee assignments for each validator during the specified epoch.
```

### beacon-chain/core/helpers/beacon_committee_test.go
```diff
@@ -912,6 +912,7 @@ func TestAssignmentForValidator(t *testing.T) {
 			{{4, 5, 6}},
 		}
 		got = helpers.AssignmentForValidator(bySlot, start, primitives.ValidatorIndex(99))
-		require.IsNil(t, got)
+		// should be empty to be safe
+		require.DeepEqual(t, &helpers.LiteAssignment{}, got)
 	})
 }
```

### beacon-chain/rpc/prysm/v1alpha1/validator/duties_v2.go
```diff
@@ -261,6 +261,10 @@ func (vs *Server) buildValidatorDuty(
 }
 
 func populateCommitteeFields(duty *ethpb.DutiesV2Response_Duty, la *helpers.LiteAssignment) {
+	if duty == nil || la == nil {
+		// should never be the case as previous functions should set
+		return
+	}
 	duty.CommitteeLength = la.CommitteeLength
 	duty.CommitteeIndex = la.CommitteeIndex
 	duty.ValidatorCommitteeIndex = la.ValidatorCommitteeIndex
```

### changelog/james-prysm_fix-duties-v2-assignment.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- Fix panic on dutiesv2 when there is no committee assignment on the epoch
\ No newline at end of file
```
