# [?] Vault: Fix non-determinism issue (#22677)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2026-05-28
Source: https://github.com/smartcontractkit/chainlink/commit/5f93f315350a823cd075624e098bac57f4afeda8
Type: security-commit

## Details
Vault: Fix non-determinism issue (#22677)

Fix non-determinism issue

## Patch
### core/services/ocr2/plugins/vault/plugin.go
```diff
@@ -1939,6 +1939,17 @@ func (r *ReportingPlugin) stateTransitionPendingQueue(ctx context.Context, seqNr
 		return bytes.Compare(sortKey(i.Id, salt), sortKey(j.Id, salt))
 	})
 
+	if !r.optimizationsEnabled(ctx) {
+		// Step 5: Apply batch size and write the latest batch to the store's pending queue.
+		if err := r.cfg.MaxBatchSize.Check(ctx, len(keptItems)); err != nil {
+			var errBoundLimited limits.ErrorBoundLimited[int]
+			if !errors.As(err, &errBoundLimited) {
+				return fmt.Errorf("failed to check batch size limit: %w", err)
+			}
+			keptItems = keptItems[:errBoundLimited.Limit]
+		}
+	}
+
 	r.metrics.trackPendingQueueWrittenSize(ctx, len(keptItems))
 	r.lggr.Infow("pending queue items persisted to storage", "seqNr", seqNr, "writtenCount", len(keptItems))
 
```

### core/services/ocr2/plugins/vault/plugin_test.go
```diff
@@ -5555,15 +5555,8 @@ func TestPlugin_StateTransition_StoresPendingQueue(t *testing.T) {
 }
 
 func TestPlugin_StateTransition_StoresPendingQueue_AllConsensusItems(t *testing.T) {
-	ctx := t.Context()
 	_, pk, shares, err := tdh2easy.GenerateKeys(1, 3)
 	require.NoError(t, err)
-	r := newTestReportingPlugin(t, withBatchSize(1), withMaxIdentifierLengths(30, 30, 30), withKeys(pk, shares[0]), withOnchainCfg(4, 1))
-
-	seqNr := uint64(1)
-	rdr := &kv{
-		m: make(map[string]response),
-	}
 
 	req1 := &vaultcommon.ListSecretIdentifiersRequest{
 		Owner:     "owner",
@@ -5617,8 +5610,6 @@ func TestPlugin_StateTransition_StoresPendingQueue_AllConsensusItems(t *testing.
 		},
 	}
 
-	r.unmarshalBlob = bf.unmarshalBlob
-
 	o1 := &vaultcommon.Observations{
 		PendingQueueItems: [][]byte{
 			{0},
@@ -5652,41 +5643,72 @@ func TestPlugin_StateTransition_StoresPendingQueue_AllConsensusItems(t *testing.
 	o3b, err := proto.Marshal(o3)
 	require.NoError(t, err)
 
-	reportPrecursor, err := r.StateTransition(
-		ctx,
-		seqNr,
-		types.AttributedQuery{},
-		[]types.AttributedObservation{
-			{Observer: 0, Observation: o1b},
-			{Observer: 1, Observation: o2b},
-			{Observer: 2, Observation: o3b},
-		},
-		rdr,
-		bf,
-	)
-	require.NoError(t, err)
-
-	os := &vaultcommon.Outcomes{}
-	err = proto.Unmarshal(reportPrecursor, os)
-	require.NoError(t, err)
+	runStateTransition := func(t *testing.T, r *ReportingPlugin) []*vaultcommon.StoredPendingQueueItem {
+		t.Helper()
+		ctx := t.Context()
+		seqNr := uint64(1)
+		rdr := &kv{m: make(map[string]response)}
+		r.unmarshalBlob = bf.unmarshalBlob
 
-	assert.Empty(t, os.Outcomes)
+		reportPrecursor, err := r.StateTransition(
+			ctx,
+			seqNr,
+			types.AttributedQuery{},
+			[]types.AttributedObservation{
+				{Observer: 0, Observation: o1b},
+				{Observer: 1, Observation: o2b},
+				{Observer: 2, Observation: o3b},
+			},
+			rdr,
+			bf,
+		)
+		require.NoError(t, err)
 
-	pq, err := newTestReadStore(t, rdr).GetPendingQueue(ctx)
-	require.NoError(t, err)
-	require.Len(t, pq, len(stored))
+		os := &vaultcommon.Outcomes{}
+		err = proto.Unmarshal(reportPrecursor, os)
+		require.NoError(t, err)
+		assert.Empty(t, os.Outcomes)
 
-	got := make([]string, len(pq))
-	for i, it := range pq {
-		got[i] = it.Id
+		pq, err := newTestReadStore(t, rdr).GetPendingQueue(ctx)
+		require.NoError(t, err)
+		return pq
 	}
-	want := make([]string, len(stored))
-	for i, it := range stored {
-		want[i] = it.Id
+
+	sortedIDs := func(items []*vaultcommon.StoredPendingQueueItem) []string {
+		ids := make([]string, len(items))
+		for i, it := range items {
+			ids[i] = it.Id
+		}
+		slices.Sort(ids)
+		return ids
 	}
-	slices.Sort(got)
-	slices.Sort(want)
-	require.Equal(t, want, got, "all F+1 consensus pending queue items are written without byte-budget truncation")
+
+	t.Run("optimizations enabled writes all F+1 consensus items", func(t *testing.T) {
+		r := newTestReportingPlugin(
+			t,
+			withBatchSize(1),
+			withMaxIdentifierLengths(30, 30, 30),
+			withKeys(pk, shares[0]),
+			withOnchainCfg(4, 1),
+			withVaultOptimizationsEnabled(),
+		)
+		pq := runStateTransition(t, r)
+		require.Len(t, pq, len(stored))
+		require.Equal(t, sortedIDs(stored), sortedIDs(pq), "all F+1 consensus pending queue items are written without MaxBatchSize truncation")
+	})
+
+	t.Run("optimizations disabled applies MaxBatchSize", func(t *testing.T) {
+		r := newTestReportingPlugin(
+			t,
+			withBatchSize(1),
+			withMaxIdentifierLengths(30, 30, 30),
+			withKeys(pk, shares[0]),
+			withOnchainCfg(4, 1),
+		)
+		pq := runStateTransition(t, r)
+		require.Len(t, pq, 1)
+		require.Equal(t, stored[0].Id, pq[0].Id, "MaxBatchSize keeps the first item after deterministic sort")
+	})
 }
 
 func TestPlugin_StateTransition_OutcomesStoppedByPrecursorWireSize(t *testing.T) {
```
