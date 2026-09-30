# [?] fix nil assert state functions panic in test (#186)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2022-08-09
Source: https://github.com/ava-labs/avalanchego/commit/d23811eb1cbd6dc28ce420d458f99f63fffc67de
Type: security-commit

## Details
fix nil assert state functions panic in test (#186)

## Patch
### core/genesis_test.go
```diff
@@ -216,7 +216,10 @@ func TestStatefulPrecompilesConfigure(t *testing.T) {
 			if err != nil {
 				t.Fatal(err)
 			}
-			test.assertState(t, statedb)
+
+			if test.assertState != nil {
+				test.assertState(t, statedb)
+			}
 		})
 	}
 }
```

### core/stateful_precompile_test.go
```diff
@@ -286,7 +286,9 @@ func TestContractDeployerAllowListRun(t *testing.T) {
 			assert.Equal(t, uint64(0), remainingGas)
 			assert.Equal(t, test.expectedRes, ret)
 
-			test.assertState(t, state)
+			if test.assertState != nil {
+				test.assertState(t, state)
+			}
 		})
 	}
 }
@@ -519,7 +521,9 @@ func TestTxAllowListRun(t *testing.T) {
 			assert.Equal(t, uint64(0), remainingGas)
 			assert.Equal(t, test.expectedRes, ret)
 
-			test.assertState(t, state)
+			if test.assertState != nil {
+				test.assertState(t, state)
+			}
 		})
 	}
 }
@@ -769,7 +773,9 @@ func TestContractNativeMinterRun(t *testing.T) {
 			assert.Equal(t, uint64(0), remainingGas)
 			assert.Equal(t, test.expectedRes, ret)
 
-			test.assertState(t, state)
+			if test.assertState != nil {
+				test.assertState(t, state)
+			}
 		})
 	}
 }
@@ -1049,7 +1055,9 @@ func TestFeeConfigManagerRun(t *testing.T) {
 			assert.Equal(t, uint64(0), remainingGas)
 			assert.Equal(t, test.expectedRes, ret)
 
-			test.assertState(t, state)
+			if test.assertState != nil {
+				test.assertState(t, state)
+			}
 		})
 	}
 }
```
