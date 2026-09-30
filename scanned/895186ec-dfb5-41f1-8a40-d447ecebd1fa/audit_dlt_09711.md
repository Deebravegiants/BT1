# [?] tests: fix? oob err stPostState slice

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2021-03-26
Source: https://github.com/etclabscore/core-geth/commit/727658efbed42aaef2566a6d80ea6edac51772ab
Type: security-commit

## Details
tests: fix? oob err stPostState slice

Date: 2021-03-26 07:30:20-05:00
Signed-off-by: meows <b5c6@protonmail.com>

## Patch
### tests/state_mgen_test.go
```diff
@@ -76,11 +76,6 @@ func (tm *testMatcherGen) stateTestsGen(w io.WriteCloser) func(t *testing.T, nam
 
 		subtests := test.Subtests(nil)
 
-		// We can use any fork to get the number of subtests that will be run for each fork
-		// since they must all be equivalent, and we assume that there must be at least one tested fork.
-		anyFork := subtests[0].Fork
-		subtestsLen := len(test.json.Post[anyFork])
-
 		targets := map[string][]stPostState{}
 
 		for _, s := range subtests {
@@ -95,7 +90,9 @@ func (tm *testMatcherGen) stateTestsGen(w io.WriteCloser) func(t *testing.T, nam
 			if ref == "" {
 				continue
 			}
+
 			if _, ok := targets[target]; !ok {
+				subtestsLen := len(test.json.Post[s.Fork])
 				targets[target] = make([]stPostState, subtestsLen)
 			}
 
@@ -229,7 +226,6 @@ func (tm *testMatcherGen) testWriteTest(t *testing.T, name string, test *StateTe
 	tm.runTestFile(t, name, name, tm.stateTestRunner)
 	tm.runTestFile(t, name, name, tm.stateTestsGen(testOut))
 	tm.runTestFile(t, testOut.Name(), testOut.Name(), tm.stateTestRunner)
-
 }
 
 func (tm *testMatcher) withWritingTests(t *testing.T, name string, test *StateTest) {
```
