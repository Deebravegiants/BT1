# [?] tests: guard against OoB errors when hacking RunNoVerify

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2022-09-01
Source: https://github.com/etclabscore/core-geth/commit/20fd6283b59f4b8d0aa531361685b5012e46cc61
Type: security-commit

## Details
tests: guard against OoB errors when hacking RunNoVerify

Date: 2022-09-01 06:54:10-07:00
Signed-off-by: meows <b5c6@protonmail.com>

## Patch
### tests/state_test_util.go
```diff
@@ -215,10 +215,21 @@ func (t *StateTest) Run(subtest StateSubtest, vmconfig vm.Config, snapshotter bo
 
 // RunNoVerify runs a specific subtest and returns the statedb and post-state root
 func (t *StateTest) RunNoVerifyWithPost(subtest StateSubtest, vmconfig vm.Config, snapshotter bool, post stPostState) (*snapshot.Tree, *state.StateDB, common.Hash, error) {
-	stPostCp := t.json.Post[subtest.Fork][subtest.Index]
+	var stPostCp stPostState
+	if v, ok := t.json.Post[subtest.Fork]; ok {
+		if len(v) > subtest.Index {
+			stPostCp = v[subtest.Index]
+		}
+	}
 	defer func() {
 		t.json.Post[subtest.Fork][subtest.Index] = stPostCp
 	}()
+	if _, ok := t.json.Post[subtest.Fork]; !ok {
+		t.json.Post[subtest.Fork] = make([]stPostState, subtest.Index+1)
+	}
+	if len(t.json.Post[subtest.Fork]) <= subtest.Index {
+		t.json.Post[subtest.Fork] = append(t.json.Post[subtest.Fork], make([]stPostState, subtest.Index-len(t.json.Post[subtest.Fork])+1)...)
+	}
 	t.json.Post[subtest.Fork][subtest.Index] = post
 	return t.RunNoVerify(subtest, vmconfig, snapshotter)
 }
```
