# [?] fix panic: log after test completed (#8501)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2023-02-21
Source: https://github.com/smartcontractkit/ccip/commit/851daa82fa5f64eb8608c9c879717464e70722d1
Type: security-commit

## Details
fix panic: log after test completed (#8501)

## Patch
### core/chains/evm/txmgr/txmgr_test.go
```diff
@@ -729,6 +729,7 @@ func TestTxm_Reset(t *testing.T) {
 	})
 
 	require.NoError(t, txm.Start(testutils.Context(t)))
+	defer func() { assert.NoError(t, txm.Close()) }()
 
 	t.Run("calls function if started", func(t *testing.T) {
 		f := new(fnMock)
@@ -758,4 +759,5 @@ func TestTxm_Reset(t *testing.T) {
 		require.NoError(t, err)
 		assert.Equal(t, 0, count)
 	})
+
 }
```
