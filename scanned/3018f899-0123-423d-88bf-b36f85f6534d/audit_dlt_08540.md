# [?] tests: fix close - commit data race in tracker tests (#5619)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2023-08-09
Source: https://github.com/algorand/go-algorand/commit/fb8adcfb809ed218fc1a3bc6e338b6064286b030
Type: security-commit

## Details
tests: fix close - commit data race in tracker tests (#5619)

## Patch
### ledger/acctonline_test.go
```diff
@@ -730,8 +730,7 @@ func TestAcctOnlineRoundParamsCache(t *testing.T) {
 
 	conf := config.GetDefaultLocal()
 	au, ao := newAcctUpdates(t, ml, conf)
-	defer au.close()
-	defer ao.close()
+	// au and ao are closed via ml.Close() -> ml.trackers.close()
 
 	// cover 10 genesis blocks
 	rewardLevel := uint64(0)
```

### ledger/acctupdates_test.go
```diff
@@ -532,8 +532,7 @@ func testAcctUpdates(t *testing.T, conf config.Local) {
 			defer ml.Close()
 
 			au, ao := newAcctUpdates(t, ml, conf)
-			defer au.close()
-			defer ao.close()
+			// au and ao are closed via ml.Close() -> ml.trackers.close()
 
 			// cover 10 genesis blocks
 			rewardLevel := uint64(0)
@@ -662,9 +661,8 @@ func BenchmarkBalancesChanges(b *testing.B) {
 
 	conf := config.GetDefaultLocal()
 	maxAcctLookback := conf.MaxAcctLookback
-	au, ao := newAcctUpdates(b, ml, conf)
-	defer au.close()
-	defer ao.close()
+	au, _ := newAcctUpdates(b, ml, conf)
+	// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 
 	// cover initialRounds genesis blocks
 	rewardLevel := uint64(0)
@@ -798,7 +796,7 @@ func testAcctUpdatesUpdatesCorrectness(t *testing.T, cfg config.Local) {
 		}
 
 		au, _ := newAcctUpdates(t, ml, cfg)
-		defer au.close()
+		// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 
 		// cover 10 genesis blocks
 		rewardLevel := uint64(0)
@@ -929,7 +927,7 @@ func TestBoxNamesByAppIDs(t *testing.T) {
 
 	conf := config.GetDefaultLocal()
 	au, _ := newAcctUpdates(t, ml, conf)
-	defer au.close()
+	// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 
 	knownCreatables := make(map[basics.CreatableIndex]bool)
 	opts := auNewBlockOpts{ledgercore.AccountDeltas{}, protocol.ConsensusCurrentVersion, protoParams, knownCreatables}
@@ -1050,7 +1048,7 @@ func TestKVCache(t *testing.T) {
 
 	conf := config.GetDefaultLocal()
 	au, _ := newAcctUpdates(t, ml, conf)
-	defer au.close()
+	// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 
 	knownCreatables := make(map[basics.CreatableIndex]bool)
 	opts := auNewBlockOpts{ledgercore.AccountDeltas{}, protocol.ConsensusCurrentVersion, protoParams, knownCreatables}
@@ -1224,7 +1222,7 @@ func BenchmarkLargeMerkleTrieRebuild(b *testing.B) {
 	cfg := config.GetDefaultLocal()
 	cfg.Archival = true
 	au, _ := newAcctUpdates(b, ml, cfg)
-	defer au.close()
+	// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 
 	// at this point, the database was created. We want to fill the accounts data
 	accountsNumber := 6000000 * b.N
@@ -1613,7 +1611,7 @@ func TestAcctUpdatesCachesInitialization(t *testing.T) {
 
 	conf = config.GetDefaultLocal()
 	au, _ = newAcctUpdates(t, ml2, conf)
-	defer au.close()
+	// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 
 	// make sure the deltas array end up containing only the most recent 320 rounds.
 	require.Equal(t, int(conf.MaxAcctLookback), len(au.deltas))
@@ -1641,7 +1639,7 @@ func TestAcctUpdatesSplittingConsensusVersionCommits(t *testing.T) {
 
 	conf := config.GetDefaultLocal()
 	au, _ := newAcctUpdates(t, ml, conf)
-	defer au.close()
+	// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 
 	// cover initialRounds genesis blocks
 	rewardLevel := uint64(0)
@@ -1746,7 +1744,7 @@ func TestAcctUpdatesSplittingConsensusVersionCommitsBoundary(t *testing.T) {
 
 	conf := config.GetDefaultLocal()
 	au, _ := newAcctUpdates(t, ml, conf)
-	defer au.close()
+	// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 
 	// cover initialRounds genesis blocks
 	rewardLevel := uint64(0)
@@ -1881,7 +1879,7 @@ func TestAcctUpdatesResources(t *testing.T) {
 
 	conf := config.GetDefaultLocal()
 	au, _ := newAcctUpdates(t, ml, conf)
-	defer au.close()
+	// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 
 	var addr1 basics.Address
 	var addr2 basics.Address
@@ -2088,7 +2086,7 @@ func TestAcctUpdatesLookupLatest(t *testing.T) {
 
 	conf := config.GetDefaultLocal()
 	au, _ := newAcctUpdates(t, ml, conf)
-	defer au.close()
+	// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 	for addr, acct := range accts {
 		acctData, validThrough, withoutRewards, err := au.lookupLatest(addr)
 		require.NoError(t, err)
@@ -2124,8 +2122,7 @@ func testAcctUpdatesLookupRetry(t *testing.T, assertFn func(au *accountUpdates,
 	defer ml.Close()
 
 	au, ao := newAcctUpdates(t, ml, conf)
-	defer au.close()
-	defer ao.close()
+	// au and ao are closed via ml.Close() -> ml.trackers.close()
 
 	// cover 10 genesis blocks
 	rewardLevel := uint64(0)
@@ -2367,7 +2364,7 @@ func TestAcctUpdatesLookupLatestCacheRetry(t *testing.T) {
 
 	conf := config.GetDefaultLocal()
 	au, _ := newAcctUpdates(t, ml, conf)
-	defer au.close()
+	// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 
 	var addr1 basics.Address
 	for addr := range accts[0] {
@@ -2496,7 +2493,7 @@ func TestAcctUpdatesLookupResources(t *testing.T) {
 
 	conf := config.GetDefaultLocal()
 	au, _ := newAcctUpdates(t, ml, conf)
-	defer au.close()
+	// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 
 	var addr1 basics.Address
 	for addr := range accts[0] {
@@ -2576,7 +2573,7 @@ func TestAcctUpdatesLookupStateDelta(t *testing.T) {
 
 	conf := config.GetDefaultLocal()
 	au, _ := newAcctUpdates(t, ml, conf)
-	defer au.close()
+	// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 
 	knownCreatables := make(map[basics.CreatableIndex]bool)
 
```

### ledger/catchpointfilewriter_test.go
```diff
@@ -132,7 +132,7 @@ func verifyStateProofVerificationContextWrite(t *testing.T, data []ledgercore.St
 	au, _ := newAcctUpdates(t, ml, conf)
 	err := au.loadFromDisk(ml, 0)
 	require.NoError(t, err)
-	au.close()
+	au.close() // it is OK to close it here - no data race since commitSyncer is not active
 	fileName := filepath.Join(temporaryDirectory, "15.data")
 
 	mockCommitData := make([]verificationCommitContext, 0)
@@ -258,7 +258,7 @@ func TestBasicCatchpointWriter(t *testing.T) {
 	au, _ := newAcctUpdates(t, ml, conf)
 	err := au.loadFromDisk(ml, 0)
 	require.NoError(t, err)
-	au.close()
+	au.close() // it is OK to close it here - no data race since commitSyncer is not active
 	fileName := filepath.Join(temporaryDirectory, "15.data")
 
 	err = ml.trackerDB().Transaction(func(ctx context.Context, tx trackerdb.TransactionScope) (err error) {
@@ -425,7 +425,7 @@ func TestCatchpointReadDatabaseOverflowSingleAccount(t *testing.T) {
 	au, _ := newAcctUpdates(t, ml, conf)
 	err := au.loadFromDisk(ml, 0)
 	require.NoError(t, err)
-	au.close()
+	au.close() // it is OK to close it here - no data race since commitSyncer is not active
 	catchpointDataFilePath := filepath.Join(temporaryDirectory, "15.data")
 
 	err = ml.trackerDB().Transaction(func(ctx context.Context, tx trackerdb.TransactionScope) (err error) {
```

### ledger/voters_test.go
```diff
@@ -122,9 +122,8 @@ func TestVoterTrackerDeleteVotersAfterStateproofConfirmed(t *testing.T) {
 	conf := config.GetDefaultLocal()
 	// To cause all blocks to be committed, for easier processing by the voters tracker.
 	conf.MaxAcctLookback = 0
-	au, ao := newAcctUpdates(t, ml, conf)
-	defer au.close()
-	defer ao.close()
+	_, ao := newAcctUpdates(t, ml, conf)
+	// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 
 	i := uint64(1)
 	// adding blocks to the voterstracker (in order to pass the numOfIntervals*stateproofInterval we add 1)
@@ -177,9 +176,8 @@ func TestLimitVoterTracker(t *testing.T) {
 	conf := config.GetDefaultLocal()
 	// To cause all blocks to be committed, for easier processing by the voters tracker.
 	conf.MaxAcctLookback = 0
-	au, ao := newAcctUpdates(t, ml, conf)
-	defer au.close()
-	defer ao.close()
+	_, ao := newAcctUpdates(t, ml, conf)
+	// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 
 	i := uint64(1)
 
@@ -261,9 +259,8 @@ func TestTopNAccountsThatHaveNoMssKeys(t *testing.T) {
 	defer ml.Close()
 
 	conf := config.GetDefaultLocal()
-	au, ao := newAcctUpdates(t, ml, conf)
-	defer au.close()
-	defer ao.close()
+	_, ao := newAcctUpdates(t, ml, conf)
+	// accountUpdates and onlineAccounts are closed via: ml.Close() -> ml.trackers.close()
 
 	i := uint64(1)
 	for ; i < (intervalForTest)+1; i++ {
```
