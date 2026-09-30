# [?] Merge pull request from GHSA-qr8r-m495-7hc4

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-01-18
Source: https://github.com/cometbft/cometbft/commit/d766d20c0609e3018e26f30aadf91bd322f8cad9
Type: security-commit

## Details
Merge pull request from GHSA-qr8r-m495-7hc4

* Added comments, tests and more validation

* Added unclog message

* Update types/params.go

Co-authored-by: Sergio Mena <sergio@informal.systems>

* Update types/params.go

Co-authored-by: Sergio Mena <sergio@informal.systems>

* Update types/params.go

Co-authored-by: Greg Szabo <16846635+greg-szabo@users.noreply.github.com>

* Fixed unclog message

---------

Co-authored-by: Sergio Mena <sergio@informal.systems>

## Patch
### .changelog/unreleased/bug-fixes/0000-asa-2024-001-fix-validate.md
```diff
@@ -0,0 +1,2 @@
+`[consensus]` Fix for "Validation of `VoteExtensionsEnableHeight` can cause chain halt"
+  ([ASA-2024-001](https://github.com/cometbft/cometbft/security/advisories/GHSA-qr8r-m495-7hc4))
```

### types/params.go
```diff
@@ -205,27 +205,58 @@ func (params ConsensusParams) ValidateBasic() error {
 	return nil
 }
 
+// ValidateUpdate validates the updated VoteExtensionsEnableHeight.
+// | r | params...EnableHeight | updated...EnableHeight | result (nil == pass)
+// | 1 | *                     | (nil)                  | nil
+// | 2 | *                     | < 0                    | VoteExtensionsEnableHeight must be positive
+// | 3 | <=0                   | 0                      | nil
+// | 4 | > 0; <=height         | 0                      | vote extensions cannot be disabled once enabled
+// | 5 | > 0; > height         | 0                      | nil (disable a previous proposal)
+// | 6 | *                     | <=height               | vote extensions cannot be updated to a past height
+// | 7 | <=0                   | > height (*)           | nil
+// | 8 | (> 0) <=height        | > height (*)           | vote extensions cannot be modified once enabled
+// | 9 | (> 0) > height        | > height (*)           | nil
 func (params ConsensusParams) ValidateUpdate(updated *cmtproto.ConsensusParams, h int64) error {
-	if updated.Abci == nil {
+	// 1
+	if updated == nil || updated.Abci == nil {
 		return nil
 	}
-	if params.ABCI.VoteExtensionsEnableHeight == updated.Abci.VoteExtensionsEnableHeight {
+	// 2
+	if updated.Abci.VoteExtensionsEnableHeight < 0 {
+		return errors.New("VoteExtensionsEnableHeight must be positive")
+	}
+	// 3
+	if params.ABCI.VoteExtensionsEnableHeight <= 0 && updated.Abci.VoteExtensionsEnableHeight == 0 {
 		return nil
 	}
-	if params.ABCI.VoteExtensionsEnableHeight != 0 && updated.Abci.VoteExtensionsEnableHeight == 0 {
-		return errors.New("vote extensions cannot be disabled once enabled")
+	// 4 & 5
+	if params.ABCI.VoteExtensionsEnableHeight > 0 && updated.Abci.VoteExtensionsEnableHeight == 0 {
+		// 4
+		if params.ABCI.VoteExtensionsEnableHeight <= h {
+			return fmt.Errorf("vote extensions cannot be disabled once enabled"+
+				"old enable height: %d, current height %d",
+				params.ABCI.VoteExtensionsEnableHeight, h)
+		}
+		// 5
+		return nil
 	}
+	// 6 (implicit: updated.Abci.VoteExtensionsEnableHeight > 0)
 	if updated.Abci.VoteExtensionsEnableHeight <= h {
-		return fmt.Errorf("VoteExtensionsEnableHeight cannot be updated to a past height, "+
-			"initial height: %d, current height %d",
-			params.ABCI.VoteExtensionsEnableHeight, h)
+		return fmt.Errorf("vote extensions cannot be updated to a past or current height, "+
+			"enable height: %d, current height %d",
+			updated.Abci.VoteExtensionsEnableHeight, h)
+	}
+	// 7 (implicit: updated.Abci.VoteExtensionsEnableHeight > h)
+	if params.ABCI.VoteExtensionsEnableHeight <= 0 {
+		return nil
 	}
+	// 8 (implicit: params.ABCI.VoteExtensionsEnableHeight > 0 && updated.Abci.VoteExtensionsEnableHeight > h)
 	if params.ABCI.VoteExtensionsEnableHeight <= h {
-		return fmt.Errorf("VoteExtensionsEnableHeight cannot be modified once"+
-			"the initial height has occurred, "+
-			"initial height: %d, current height %d",
+		return fmt.Errorf("vote extensions cannot be modified once enabled"+
+			"enable height: %d, current height %d",
 			params.ABCI.VoteExtensionsEnableHeight, h)
 	}
+	// 9 (implicit: params.ABCI.VoteExtensionsEnableHeight > h && updated.Abci.VoteExtensionsEnableHeight > h)
 	return nil
 }
 
```

### types/params_test.go
```diff
@@ -154,63 +154,78 @@ func TestConsensusParamsUpdate_AppVersion(t *testing.T) {
 }
 
 func TestConsensusParamsUpdate_VoteExtensionsEnableHeight(t *testing.T) {
-	t.Run("set to height but initial height already run", func(*testing.T) {
-		initialParams := makeParams(1, 0, 2, 0, valEd25519, 1)
-		update := &cmtproto.ConsensusParams{
-			Abci: &cmtproto.ABCIParams{
-				VoteExtensionsEnableHeight: 10,
-			},
-		}
-		require.Error(t, initialParams.ValidateUpdate(update, 1))
-		require.Error(t, initialParams.ValidateUpdate(update, 5))
-	})
-	t.Run("reset to 0", func(t *testing.T) {
-		initialParams := makeParams(1, 0, 2, 0, valEd25519, 1)
-		update := &cmtproto.ConsensusParams{
-			Abci: &cmtproto.ABCIParams{
-				VoteExtensionsEnableHeight: 0,
-			},
-		}
-		require.Error(t, initialParams.ValidateUpdate(update, 1))
-	})
-	t.Run("set to height before current height run", func(*testing.T) {
-		initialParams := makeParams(1, 0, 2, 0, valEd25519, 100)
-		update := &cmtproto.ConsensusParams{
-			Abci: &cmtproto.ABCIParams{
-				VoteExtensionsEnableHeight: 10,
-			},
-		}
-		require.Error(t, initialParams.ValidateUpdate(update, 11))
-		require.Error(t, initialParams.ValidateUpdate(update, 99))
-	})
-	t.Run("set to height after current height run", func(*testing.T) {
-		initialParams := makeParams(1, 0, 2, 0, valEd25519, 300)
-		update := &cmtproto.ConsensusParams{
-			Abci: &cmtproto.ABCIParams{
-				VoteExtensionsEnableHeight: 99,
-			},
-		}
-		require.NoError(t, initialParams.ValidateUpdate(update, 11))
-		require.NoError(t, initialParams.ValidateUpdate(update, 98))
-	})
-	t.Run("no error when unchanged", func(*testing.T) {
-		initialParams := makeParams(1, 0, 2, 0, valEd25519, 100)
-		update := &cmtproto.ConsensusParams{
-			Abci: &cmtproto.ABCIParams{
-				VoteExtensionsEnableHeight: 100,
-			},
-		}
-		require.NoError(t, initialParams.ValidateUpdate(update, 500))
-	})
-	t.Run("updated from 0 to 0", func(t *testing.T) {
-		initialParams := makeParams(1, 0, 2, 0, valEd25519, 0)
-		update := &cmtproto.ConsensusParams{
-			Abci: &cmtproto.ABCIParams{
-				VoteExtensionsEnableHeight: 0,
-			},
-		}
-		require.NoError(t, initialParams.ValidateUpdate(update, 100))
-	})
+	const nilTest = -10000000
+	testCases := []struct {
+		name        string
+		current     int64
+		from        int64
+		to          int64
+		expectedErr bool
+	}{
+		// no change
+		{"current: 3, 0 -> 0", 3, 0, 0, false},
+		{"current: 3, 100 -> 100, ", 3, 100, 100, false},
+		{"current: 100, 100 -> 100, ", 100, 100, 100, true},
+		{"current: 300, 100 -> 100, ", 300, 100, 100, true},
+		// set for the first time
+		{"current: 3, 0 -> 5, ", 3, 0, 5, false},
+		{"current: 4, 0 -> 5, ", 4, 0, 5, false},
+		{"current: 5, 0 -> 5, ", 5, 0, 5, true},
+		{"current: 6, 0 -> 5, ", 6, 0, 5, true},
+		{"current: 50, 0 -> 5, ", 50, 0, 5, true},
+		// reset to 0
+		{"current: 4, 5 -> 0, ", 4, 5, 0, false},
+		{"current: 5, 5 -> 0, ", 5, 5, 0, true},
+		{"current: 6, 5 -> 0, ", 6, 5, 0, true},
+		{"current: 10, 5 -> 0, ", 10, 5, 0, true},
+		// modify backwards
+		{"current: 1, 10 -> 5, ", 1, 10, 5, false},
+		{"current: 4, 10 -> 5, ", 4, 10, 5, false},
+		{"current: 5, 10 -> 5, ", 5, 10, 5, true},
+		{"current: 6, 10 -> 5, ", 6, 10, 5, true},
+		{"current: 9, 10 -> 5, ", 9, 10, 5, true},
+		{"current: 10, 10 -> 5, ", 10, 10, 5, true},
+		{"current: 11, 10 -> 5, ", 11, 10, 5, true},
+		{"current: 100, 10 -> 5, ", 100, 10, 5, true},
+		// modify forward
+		{"current: 3, 10 -> 15, ", 3, 10, 15, false},
+		{"current: 9, 10 -> 15, ", 9, 10, 15, false},
+		{"current: 10, 10 -> 15, ", 10, 10, 15, true},
+		{"current: 11, 10 -> 15, ", 11, 10, 15, true},
+		{"current: 14, 10 -> 15, ", 14, 10, 15, true},
+		{"current: 15, 10 -> 15, ", 15, 10, 15, true},
+		{"current: 16, 10 -> 15, ", 16, 10, 15, true},
+		{"current: 100, 10 -> 15, ", 100, 10, 15, true},
+		// negative values
+		{"current: 3, 0 -> -5", 3, 0, -5, true},
+		{"current: 3, -5 -> 100, ", 3, -5, 100, false},
+		{"current: 3, -10 -> 3, ", 3, -10, 3, true},
+		{"current: 3, -3 -> -3", 3, -3, -3, true},
+		{"current: 100, -8 -> -9, ", 100, -8, -9, true},
+		{"current: 300, -10 -> -8, ", 300, -10, -8, true},
+		// test for nil
+		{"current: 300, 400 -> nil, ", 300, 400, nilTest, false},
+		{"current: 300, 200 -> nil, ", 300, 200, nilTest, false},
+	}
+
+	for _, tc := range testCases {
+		t.Run(tc.name, func(*testing.T) {
+			initialParams := makeParams(1, 0, 2, 0, valEd25519, tc.from)
+			update := &cmtproto.ConsensusParams{}
+			if tc.to == nilTest {
+				update.Abci = nil
+			} else {
+				update.Abci = &cmtproto.ABCIParams{
+					VoteExtensionsEnableHeight: tc.to,
+				}
+			}
+			if tc.expectedErr {
+				require.Error(t, initialParams.ValidateUpdate(update, tc.current))
+			} else {
+				require.NoError(t, initialParams.ValidateUpdate(update, tc.current))
+			}
+		})
+	}
 }
 
 func TestProto(t *testing.T) {
```
