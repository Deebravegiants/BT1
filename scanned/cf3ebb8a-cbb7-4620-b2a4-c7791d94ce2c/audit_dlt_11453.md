# [?] Fix data race in PersistenceManager tests (#10394)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2023-09-07
Source: https://github.com/smartcontractkit/ccip/commit/8f61ff24248cad930bd393ef949e45c9c0e6be96
Type: security-commit

## Details
Fix data race in PersistenceManager tests (#10394)

* Fix data race in PersistenceManager tests

* Fix import order

## Patch
### core/services/relay/evm/mercury/persistence_manager.go
```diff
@@ -30,14 +30,21 @@ type PersistenceManager struct {
 	deleteQueue []*pb.TransmitRequest
 
 	jobID int32
+
+	maxTransmitQueueSize  int
+	flushDeletesFrequency time.Duration
+	pruneFrequency        time.Duration
 }
 
-func NewPersistenceManager(lggr logger.Logger, orm ORM, jobID int32) *PersistenceManager {
+func NewPersistenceManager(lggr logger.Logger, orm ORM, jobID int32, maxTransmitQueueSize int, flushDeletesFrequency, pruneFrequency time.Duration) *PersistenceManager {
 	return &PersistenceManager{
-		lggr:   lggr.Named("MercuryPersistenceManager"),
-		orm:    orm,
-		stopCh: make(chan struct{}),
-		jobID:  jobID,
+		lggr:                  lggr.Named("MercuryPersistenceManager"),
+		orm:                   orm,
+		stopCh:                make(chan struct{}),
+		jobID:                 jobID,
+		maxTransmitQueueSize:  maxTransmitQueueSize,
+		flushDeletesFrequency: flushDeletesFrequency,
+		pruneFrequency:        pruneFrequency,
 	}
 }
 
@@ -80,7 +87,7 @@ func (pm *PersistenceManager) runFlushDeletesLoop() {
 	ctx, cancel := pm.stopCh.Ctx(context.Background())
 	defer cancel()
 
-	ticker := time.NewTicker(utils.WithJitter(flushDeletesFrequency))
+	ticker := time.NewTicker(utils.WithJitter(pm.flushDeletesFrequency))
 	for {
 		select {
 		case <-ctx.Done():
@@ -103,15 +110,15 @@ func (pm *PersistenceManager) runPruneLoop() {
 	ctx, cancel := pm.stopCh.Ctx(context.Background())
 	defer cancel()
 
-	ticker := time.NewTicker(utils.WithJitter(pruneFrequency))
+	ticker := time.NewTicker(utils.WithJitter(pm.pruneFrequency))
 	for {
 		select {
 		case <-ctx.Done():
 			ticker.Stop()
 			return
 		case <-ticker.C:
 			pm.lggr.Trace("Pruning transmit requests table")
-			if err := pm.orm.PruneTransmitRequests(maxTransmitQueueSize, pg.WithParentCtx(ctx), pg.WithLongQueryTimeout()); err != nil {
+			if err := pm.orm.PruneTransmitRequests(pm.maxTransmitQueueSize, pg.WithParentCtx(ctx), pg.WithLongQueryTimeout()); err != nil {
 				pm.lggr.Errorw("Failed to prune transmit requests table", "err", err)
 			}
 		}
```

### core/services/relay/evm/mercury/persistence_manager_test.go
```diff
@@ -14,12 +14,13 @@ import (
 )
 
 func bootstrapPersistenceManager(t *testing.T) *PersistenceManager {
+	t.Helper()
 	db := pgtest.NewSqlxDB(t)
 	pgtest.MustExec(t, db, `SET CONSTRAINTS mercury_transmit_requests_job_id_fkey DEFERRED`)
 	pgtest.MustExec(t, db, `SET CONSTRAINTS feed_latest_reports_job_id_fkey DEFERRED`)
 	lggr := logger.TestLogger(t)
 	orm := NewORM(db, lggr, pgtest.NewQConfig(true))
-	return NewPersistenceManager(lggr, orm, 0)
+	return NewPersistenceManager(lggr, orm, 0, 2, 10*time.Millisecond, 10*time.Millisecond)
 }
 
 func TestPersistenceManager(t *testing.T) {
@@ -61,7 +62,6 @@ func TestPersistenceManagerAsyncDelete(t *testing.T) {
 	err = pm.Insert(ctx, &pb.TransmitRequest{Payload: reports[1]}, ocrtypes.ReportContext{})
 	require.NoError(t, err)
 
-	flushDeletesFrequency = 10 * time.Millisecond
 	err = pm.Start(ctx)
 	require.NoError(t, err)
 
@@ -103,8 +103,6 @@ func TestPersistenceManagerPrune(t *testing.T) {
 	err = pm.Insert(ctx, &pb.TransmitRequest{Payload: reports[2]}, ocrtypes.ReportContext{ReportTimestamp: ocrtypes.ReportTimestamp{Epoch: 3}})
 	require.NoError(t, err)
 
-	maxTransmitQueueSize = 2
-	pruneFrequency = 10 * time.Millisecond
 	err = pm.Start(ctx)
 	require.NoError(t, err)
 
```

### core/services/relay/evm/mercury/transmitter.go
```diff
@@ -15,19 +15,16 @@ import (
 	pkgerrors "github.com/pkg/errors"
 	"github.com/prometheus/client_golang/prometheus"
 	"github.com/prometheus/client_golang/prometheus/promauto"
-	"golang.org/x/exp/maps"
-
 	"github.com/smartcontractkit/libocr/offchainreporting2plus/chains/evmutil"
 	ocrtypes "github.com/smartcontractkit/libocr/offchainreporting2plus/types"
 	"github.com/smartcontractkit/sqlx"
+	"golang.org/x/exp/maps"
 
 	relaymercury "github.com/smartcontractkit/chainlink-relay/pkg/reportingplugins/mercury"
-	mercuryutils "github.com/smartcontractkit/chainlink/v2/core/services/relay/evm/mercury/utils"
-
 	"github.com/smartcontractkit/chainlink/v2/core/logger"
 	"github.com/smartcontractkit/chainlink/v2/core/services"
-
 	"github.com/smartcontractkit/chainlink/v2/core/services/pg"
+	mercuryutils "github.com/smartcontractkit/chainlink/v2/core/services/relay/evm/mercury/utils"
 	"github.com/smartcontractkit/chainlink/v2/core/services/relay/evm/mercury/wsrpc"
 	"github.com/smartcontractkit/chainlink/v2/core/services/relay/evm/mercury/wsrpc/pb"
 	"github.com/smartcontractkit/chainlink/v2/core/utils"
@@ -122,7 +119,7 @@ func getPayloadTypes() abi.Arguments {
 
 func NewTransmitter(lggr logger.Logger, cfgTracker ConfigTracker, rpcClient wsrpc.Client, fromAccount ed25519.PublicKey, jobID int32, feedID [32]byte, db *sqlx.DB, cfg pg.QConfig) *mercuryTransmitter {
 	feedIDHex := fmt.Sprintf("0x%x", feedID[:])
-	persistenceManager := NewPersistenceManager(lggr, NewORM(db, lggr, cfg), jobID)
+	persistenceManager := NewPersistenceManager(lggr, NewORM(db, lggr, cfg), jobID, maxTransmitQueueSize, flushDeletesFrequency, pruneFrequency)
 	return &mercuryTransmitter{
 		utils.StartStopOnce{},
 		lggr.Named("MercuryTransmitter").With("feedID", feedIDHex),
```
