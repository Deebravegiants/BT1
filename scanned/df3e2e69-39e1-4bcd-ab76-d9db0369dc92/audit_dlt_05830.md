# [?] tests: fix logged panics in reproducible labels test (#4446)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2022-08-23
Source: https://github.com/algorand/go-algorand/commit/924d2fbb4872f136c0f5fb545ca5addb50efa774
Type: security-commit

## Details
tests: fix logged panics in reproducible labels test (#4446)

Fix an issue with consensus params not saved in forked ledgers.
Set logging level=info in tests that produce to much debug output while adding thousands of blocks.

## Patch
### ledger/acctupdates_test.go
```diff
@@ -120,12 +120,14 @@ func (ml *mockLedgerForTracker) fork(t testing.TB) *mockLedgerForTracker {
 	dblogger := logging.TestingLog(t)
 	dblogger.SetLevel(logging.Info)
 	newLedgerTracker := &mockLedgerForTracker{
-		inMemory: false,
-		log:      dblogger,
-		blocks:   make([]blockEntry, len(ml.blocks)),
-		deltas:   make([]ledgercore.StateDelta, len(ml.deltas)),
-		accts:    make(map[basics.Address]basics.AccountData),
-		filename: fn,
+		inMemory:         false,
+		log:              dblogger,
+		blocks:           make([]blockEntry, len(ml.blocks)),
+		deltas:           make([]ledgercore.StateDelta, len(ml.deltas)),
+		accts:            make(map[basics.Address]basics.AccountData),
+		filename:         fn,
+		consensusParams:  ml.consensusParams,
+		consensusVersion: ml.consensusVersion,
 	}
 	for k, v := range ml.accts {
 		newLedgerTracker.accts[k] = v
@@ -289,7 +291,7 @@ func checkAcctUpdates(t *testing.T, au *accountUpdates, ao *onlineAccounts, base
 	require.Error(t, err)
 	require.Equal(t, basics.Round(0), validThrough)
 
-	if base > 0 {
+	if base > 0 && base >= basics.Round(ao.maxBalLookback()) {
 		_, err := ao.onlineTotals(base - basics.Round(ao.maxBalLookback()))
 		require.Error(t, err)
 
```

### ledger/archival_test.go
```diff
@@ -143,6 +143,7 @@ func TestArchival(t *testing.T) {
 	cfg := config.GetDefaultLocal()
 	cfg.Archival = true
 	log := logging.TestingLog(t)
+	log.SetLevel(logging.Info)
 	l, err := OpenLedger(log, dbName, inMem, genesisInitState, cfg)
 	require.NoError(t, err)
 	defer l.Close()
@@ -720,6 +721,7 @@ func TestArchivalFromNonArchival(t *testing.T) {
 	cfg.Archival = false
 
 	log := logging.TestingLog(t)
+	log.SetLevel(logging.Info)
 	l, err := OpenLedger(log, dbPrefix, inMem, genesisInitState, cfg)
 	require.NoError(t, err)
 	blk := genesisInitState.Block
```

### ledger/ledger_test.go
```diff
@@ -1388,6 +1388,7 @@ func TestLedgerBlockHdrCaching(t *testing.T) {
 	cfg := config.GetDefaultLocal()
 	cfg.Archival = true
 	log := logging.TestingLog(t)
+	log.SetLevel(logging.Info)
 	l, err := OpenLedger(log, dbName, inMem, genesisInitState, cfg)
 	a.NoError(err)
 	defer l.Close()
@@ -1484,6 +1485,7 @@ func TestLedgerReload(t *testing.T) {
 	cfg := config.GetDefaultLocal()
 	cfg.Archival = true
 	log := logging.TestingLog(t)
+	log.SetLevel(logging.Info)
 	l, err := OpenLedger(log, dbName, inMem, genesisInitState, cfg)
 	require.NoError(t, err)
 	defer l.Close()
@@ -1682,11 +1684,13 @@ func TestLedgerKeepsOldBlocksForStateProof(t *testing.T) {
 	cfg := config.GetDefaultLocal()
 	cfg.Archival = false
 	log := logging.TestingLog(t)
+	log.SetLevel(logging.Info)
 	l, err := OpenLedger(log, dbName, inMem, genesisInitState, cfg)
 	require.NoError(t, err)
 	defer l.Close()
 
 	lastBlock, err := l.Block(l.Latest())
+	require.NoError(t, err)
 	proto := config.Consensus[lastBlock.CurrentProtocol]
 	accounts := make(map[basics.Address]basics.AccountData, len(genesisInitState.Accounts)+maxBlocks)
 	keys := make(map[basics.Address]*crypto.SignatureSecrets, len(initKeys)+maxBlocks)
@@ -2665,6 +2669,7 @@ func TestVotersReloadFromDisk(t *testing.T) {
 	cfg.Archival = false
 	cfg.MaxAcctLookback = proto.StateProofInterval - proto.StateProofVotersLookback - 10
 	log := logging.TestingLog(t)
+	log.SetLevel(logging.Info)
 	l, err := OpenLedger(log, dbName, inMem, genesisInitState, cfg)
 	require.NoError(t, err)
 	defer l.Close()
@@ -2712,6 +2717,7 @@ func TestVotersReloadFromDiskAfterOneStateProofCommitted(t *testing.T) {
 	cfg.Archival = false
 	cfg.MaxAcctLookback = proto.StateProofInterval - proto.StateProofVotersLookback - 10
 	log := logging.TestingLog(t)
+	log.SetLevel(logging.Info)
 	l, err := OpenLedger(log, dbName, inMem, genesisInitState, cfg)
 	require.NoError(t, err)
 	defer l.Close()
@@ -2771,6 +2777,7 @@ func TestVotersReloadFromDiskPassRecoveryPeriod(t *testing.T) {
 	cfg.Archival = false
 	cfg.MaxAcctLookback = proto.StateProofInterval - proto.StateProofVotersLookback - 10
 	log := logging.TestingLog(t)
+	log.SetLevel(logging.Info)
 	l, err := OpenLedger(log, dbName, inMem, genesisInitState, cfg)
 	require.NoError(t, err)
 	defer l.Close()
```
