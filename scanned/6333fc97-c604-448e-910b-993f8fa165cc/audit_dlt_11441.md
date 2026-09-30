# [?] Fix panic on mercury server error (#13231)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2024-05-17
Source: https://github.com/smartcontractkit/ccip/commit/c4ef6c6398149a85b7a9aef24309c4da46a82282
Type: security-commit

## Details
Fix panic on mercury server error (#13231)

* Fix panic on mercury server error

* Changelog

* Remove newline

* Fix changelog

* changelog

## Patch
### .changeset/eighty-hotels-sit.md
```diff
@@ -0,0 +1,5 @@
+---
+"chainlink": patch
+---
+
+Fix panic if mercury server returns error #bugfix
```

### CHANGELOG.md
```diff
@@ -189,7 +189,7 @@
   You may disable if this results in excessive log volume. Disable like so:
 
   ```
-  [Pipeline]
+  [JobPipeline]
   VerboseLogging = false
   ```
 
@@ -219,7 +219,7 @@
 
 - [#12404](https://github.com/smartcontractkit/chainlink/pull/12404) [`b74079b672`](https://github.com/smartcontractkit/chainlink/commit/b74079b672f36fb0c241f90ea1e875ea3a9524da) Thanks [@HenryNguyen5](https://github.com/HenryNguyen5)! - Add OCR3 capability contract wrapper
 
-- [#12498](https://github.com/smartcontractkit/chainlink/pull/12498) [`1c576d0e34`](https://github.com/smartcontractkit/chainlink/commit/1c576d0e34d93a6298ddcb662ee89fd04eeda53e) Thanks [@samsondav](https://github.com/samsondav)! - Add new config option Pipeline.VerboseLogging
+- [#12498](https://github.com/smartcontractkit/chainlink/pull/12498) [`1c576d0e34`](https://github.com/smartcontractkit/chainlink/commit/1c576d0e34d93a6298ddcb662ee89fd04eeda53e) Thanks [@samsondav](https://github.com/samsondav)! - Add new config option JobPipeline.VerboseLogging
 
   VerboseLogging enables detailed logging of pipeline execution steps. This is
   disabled by default because it increases log volume for pipeline runs, but can
@@ -230,7 +230,7 @@
   Set it like the following example:
 
   ```
-  [Pipeline]
+  [JobPipeline]
   VerboseLogging = true
   ```
 
```

### core/services/relay/evm/mercury/queue.go
```diff
@@ -25,7 +25,7 @@ type asyncDeleter interface {
 	AsyncDelete(req *pb.TransmitRequest)
 }
 
-var _ services.Service = (*TransmitQueue)(nil)
+var _ services.Service = (*transmitQueue)(nil)
 
 var transmitQueueLoad = promauto.NewGaugeVec(prometheus.GaugeOpts{
 	Name: "mercury_transmit_queue_load",
@@ -40,7 +40,7 @@ const promInterval = 6500 * time.Millisecond
 
 // TransmitQueue is the high-level package that everything outside of this file should be using
 // It stores pending transmissions, yielding the latest (highest priority) first to the caller
-type TransmitQueue struct {
+type transmitQueue struct {
 	services.StateMachine
 
 	cond         sync.Cond
@@ -62,11 +62,20 @@ type Transmission struct {
 	ReportCtx ocrtypes.ReportContext // contains priority information (latest epoch/round wins)
 }
 
+type TransmitQueue interface {
+	services.Service
+
+	BlockingPop() (t *Transmission)
+	Push(req *pb.TransmitRequest, reportCtx ocrtypes.ReportContext) (ok bool)
+	Init(transmissions []*Transmission)
+	IsEmpty() bool
+}
+
 // maxlen controls how many items will be stored in the queue
 // 0 means unlimited - be careful, this can cause memory leaks
-func NewTransmitQueue(lggr logger.Logger, serverURL, feedID string, maxlen int, asyncDeleter asyncDeleter) *TransmitQueue {
+func NewTransmitQueue(lggr logger.Logger, serverURL, feedID string, maxlen int, asyncDeleter asyncDeleter) TransmitQueue {
 	mu := new(sync.RWMutex)
-	return &TransmitQueue{
+	return &transmitQueue{
 		services.StateMachine{},
 		sync.Cond{L: mu},
 		lggr.Named("TransmitQueue"),
@@ -80,13 +89,13 @@ func NewTransmitQueue(lggr logger.Logger, serverURL, feedID string, maxlen int,
 	}
 }
 
-func (tq *TransmitQueue) Init(transmissions []*Transmission) {
+func (tq *transmitQueue) Init(transmissions []*Transmission) {
 	pq := priorityQueue(transmissions)
 	heap.Init(&pq) // ensure the heap is ordered
 	tq.pq = &pq
 }
 
-func (tq *TransmitQueue) Push(req *pb.TransmitRequest, reportCtx ocrtypes.ReportContext) (ok bool) {
+func (tq *transmitQueue) Push(req *pb.TransmitRequest, reportCtx ocrtypes.ReportContext) (ok bool) {
 	tq.cond.L.Lock()
 	defer tq.cond.L.Unlock()
 
@@ -111,7 +120,7 @@ func (tq *TransmitQueue) Push(req *pb.TransmitRequest, reportCtx ocrtypes.Report
 
 // BlockingPop will block until at least one item is in the heap, and then return it
 // If the queue is closed, it will immediately return nil
-func (tq *TransmitQueue) BlockingPop() (t *Transmission) {
+func (tq *transmitQueue) BlockingPop() (t *Transmission) {
 	tq.cond.L.Lock()
 	defer tq.cond.L.Unlock()
 	if tq.closed {
@@ -126,13 +135,13 @@ func (tq *TransmitQueue) BlockingPop() (t *Transmission) {
 	return t
 }
 
-func (tq *TransmitQueue) IsEmpty() bool {
+func (tq *transmitQueue) IsEmpty() bool {
 	tq.mu.RLock()
 	defer tq.mu.RUnlock()
 	return tq.pq.Len() == 0
 }
 
-func (tq *TransmitQueue) Start(context.Context) error {
+func (tq *transmitQueue) Start(context.Context) error {
 	return tq.StartOnce("TransmitQueue", func() error {
 		t := time.NewTicker(utils.WithJitter(promInterval))
 		wg := new(sync.WaitGroup)
@@ -148,7 +157,7 @@ func (tq *TransmitQueue) Start(context.Context) error {
 	})
 }
 
-func (tq *TransmitQueue) Close() error {
+func (tq *transmitQueue) Close() error {
 	return tq.StopOnce("TransmitQueue", func() error {
 		tq.cond.L.Lock()
 		tq.closed = true
@@ -159,7 +168,7 @@ func (tq *TransmitQueue) Close() error {
 	})
 }
 
-func (tq *TransmitQueue) monitorLoop(c <-chan time.Time, chStop <-chan struct{}, wg *sync.WaitGroup) {
+func (tq *transmitQueue) monitorLoop(c <-chan time.Time, chStop <-chan struct{}, wg *sync.WaitGroup) {
 	defer wg.Done()
 
 	for {
@@ -172,25 +181,25 @@ func (tq *TransmitQueue) monitorLoop(c <-chan time.Time, chStop <-chan struct{},
 	}
 }
 
-func (tq *TransmitQueue) report() {
+func (tq *transmitQueue) report() {
 	tq.mu.RLock()
 	length := tq.pq.Len()
 	tq.mu.RUnlock()
 	tq.transmitQueueLoad.Set(float64(length))
 }
 
-func (tq *TransmitQueue) Ready() error {
+func (tq *transmitQueue) Ready() error {
 	return nil
 }
-func (tq *TransmitQueue) Name() string { return tq.lggr.Name() }
-func (tq *TransmitQueue) HealthReport() map[string]error {
+func (tq *transmitQueue) Name() string { return tq.lggr.Name() }
+func (tq *transmitQueue) HealthReport() map[string]error {
 	report := map[string]error{tq.Name(): errors.Join(
 		tq.status(),
 	)}
 	return report
 }
 
-func (tq *TransmitQueue) status() (merr error) {
+func (tq *transmitQueue) status() (merr error) {
 	tq.mu.RLock()
 	length := tq.pq.Len()
 	closed := tq.closed
@@ -206,7 +215,7 @@ func (tq *TransmitQueue) status() (merr error) {
 
 // pop latest Transmission from the heap
 // Not thread-safe
-func (tq *TransmitQueue) pop() *Transmission {
+func (tq *transmitQueue) pop() *Transmission {
 	if tq.pq.Len() == 0 {
 		return nil
 	}
```

### core/services/relay/evm/mercury/transmitter.go
```diff
@@ -153,10 +153,12 @@ type server struct {
 
 	c  wsrpc.Client
 	pm *PersistenceManager
-	q  *TransmitQueue
+	q  TransmitQueue
 
 	deleteQueue chan *pb.TransmitRequest
 
+	url string
+
 	transmitSuccessCount          prometheus.Counter
 	transmitDuplicateCount        prometheus.Counter
 	transmitConnectionErrorCount  prometheus.Counter
@@ -268,7 +270,7 @@ func (s *server) runQueueLoop(stopCh services.StopChan, wg *sync.WaitGroup, feed
 				s.transmitDuplicateCount.Inc()
 				s.lggr.Debugw("Transmit report success; duplicate report", "payload", hexutil.Encode(t.Req.Payload), "response", res, "repts", t.ReportCtx.ReportTimestamp)
 			default:
-				transmitServerErrorCount.WithLabelValues(feedIDHex, fmt.Sprintf("%d", res.Code)).Inc()
+				transmitServerErrorCount.WithLabelValues(feedIDHex, s.url, fmt.Sprintf("%d", res.Code)).Inc()
 				s.lggr.Errorw("Transmit report failed; mercury server returned error", "response", res, "reportCtx", t.ReportCtx, "err", res.Error, "code", res.Code)
 			}
 		}
@@ -281,26 +283,31 @@ func (s *server) runQueueLoop(stopCh services.StopChan, wg *sync.WaitGroup, feed
 	}
 }
 
+func newServer(lggr logger.Logger, cfg TransmitterConfig, client wsrpc.Client, pm *PersistenceManager, serverURL, feedIDHex string) *server {
+	return &server{
+		lggr,
+		cfg.TransmitTimeout().Duration(),
+		client,
+		pm,
+		NewTransmitQueue(lggr, serverURL, feedIDHex, int(cfg.TransmitQueueMaxSize()), pm),
+		make(chan *pb.TransmitRequest, int(cfg.TransmitQueueMaxSize())),
+		serverURL,
+		transmitSuccessCount.WithLabelValues(feedIDHex, serverURL),
+		transmitDuplicateCount.WithLabelValues(feedIDHex, serverURL),
+		transmitConnectionErrorCount.WithLabelValues(feedIDHex, serverURL),
+		transmitQueueDeleteErrorCount.WithLabelValues(feedIDHex, serverURL),
+		transmitQueueInsertErrorCount.WithLabelValues(feedIDHex, serverURL),
+		transmitQueuePushErrorCount.WithLabelValues(feedIDHex, serverURL),
+	}
+}
+
 func NewTransmitter(lggr logger.Logger, cfg TransmitterConfig, clients map[string]wsrpc.Client, fromAccount ed25519.PublicKey, jobID int32, feedID [32]byte, orm ORM, codec TransmitterReportDecoder, triggerCapability *triggers.MercuryTriggerService) *mercuryTransmitter {
 	feedIDHex := fmt.Sprintf("0x%x", feedID[:])
 	servers := make(map[string]*server, len(clients))
 	for serverURL, client := range clients {
 		cLggr := lggr.Named(serverURL).With("serverURL", serverURL)
 		pm := NewPersistenceManager(cLggr, serverURL, orm, jobID, int(cfg.TransmitQueueMaxSize()), flushDeletesFrequency, pruneFrequency)
-		servers[serverURL] = &server{
-			cLggr,
-			cfg.TransmitTimeout().Duration(),
-			client,
-			pm,
-			NewTransmitQueue(cLggr, serverURL, feedIDHex, int(cfg.TransmitQueueMaxSize()), pm),
-			make(chan *pb.TransmitRequest, int(cfg.TransmitQueueMaxSize())),
-			transmitSuccessCount.WithLabelValues(feedIDHex, serverURL),
-			transmitDuplicateCount.WithLabelValues(feedIDHex, serverURL),
-			transmitConnectionErrorCount.WithLabelValues(feedIDHex, serverURL),
-			transmitQueueDeleteErrorCount.WithLabelValues(feedIDHex, serverURL),
-			transmitQueueInsertErrorCount.WithLabelValues(feedIDHex, serverURL),
-			transmitQueuePushErrorCount.WithLabelValues(feedIDHex, serverURL),
-		}
+		servers[serverURL] = newServer(cLggr, cfg, client, pm, serverURL, feedIDHex)
 	}
 	return &mercuryTransmitter{
 		services.StateMachine{},
```

### core/services/relay/evm/mercury/transmitter_test.go
```diff
@@ -3,6 +3,7 @@ package mercury
 import (
 	"context"
 	"math/big"
+	"sync"
 	"testing"
 	"time"
 
@@ -15,6 +16,7 @@ import (
 
 	"github.com/smartcontractkit/chainlink-common/pkg/capabilities/triggers"
 	commonconfig "github.com/smartcontractkit/chainlink-common/pkg/config"
+	"github.com/smartcontractkit/chainlink/v2/core/chains/evm/utils"
 	"github.com/smartcontractkit/chainlink/v2/core/internal/testutils"
 	"github.com/smartcontractkit/chainlink/v2/core/internal/testutils/pgtest"
 	"github.com/smartcontractkit/chainlink/v2/core/logger"
@@ -56,8 +58,8 @@ func Test_MercuryTransmitter_Transmit(t *testing.T) {
 			require.NoError(t, err)
 
 			// ensure it was added to the queue
-			require.Equal(t, mt.servers[sURL].q.pq.Len(), 1)
-			assert.Subset(t, mt.servers[sURL].q.pq.Pop().(*Transmission).Req.Payload, report)
+			require.Equal(t, mt.servers[sURL].q.(*transmitQueue).pq.Len(), 1)
+			assert.Subset(t, mt.servers[sURL].q.(*transmitQueue).pq.Pop().(*Transmission).Req.Payload, report)
 		})
 		t.Run("v2 report transmission successfully enqueued", func(t *testing.T) {
 			report := sampleV2Report
@@ -70,8 +72,8 @@ func Test_MercuryTransmitter_Transmit(t *testing.T) {
 			require.NoError(t, err)
 
 			// ensure it was added to the queue
-			require.Equal(t, mt.servers[sURL].q.pq.Len(), 1)
-			assert.Subset(t, mt.servers[sURL].q.pq.Pop().(*Transmission).Req.Payload, report)
+			require.Equal(t, mt.servers[sURL].q.(*transmitQueue).pq.Len(), 1)
+			assert.Subset(t, mt.servers[sURL].q.(*transmitQueue).pq.Pop().(*Transmission).Req.Payload, report)
 		})
 		t.Run("v3 report transmission successfully enqueued", func(t *testing.T) {
 			report := sampleV3Report
@@ -84,8 +86,8 @@ func Test_MercuryTransmitter_Transmit(t *testing.T) {
 			require.NoError(t, err)
 
 			// ensure it was added to the queue
-			require.Equal(t, mt.servers[sURL].q.pq.Len(), 1)
-			assert.Subset(t, mt.servers[sURL].q.pq.Pop().(*Transmission).Req.Payload, report)
+			require.Equal(t, mt.servers[sURL].q.(*transmitQueue).pq.Len(), 1)
+			assert.Subset(t, mt.servers[sURL].q.(*transmitQueue).pq.Pop().(*Transmission).Req.Payload, report)
 		})
 		t.Run("v3 report transmission sent only to trigger service", func(t *testing.T) {
 			report := sampleV3Report
@@ -98,7 +100,7 @@ func Test_MercuryTransmitter_Transmit(t *testing.T) {
 			err := mt.Transmit(testutils.Context(t), sampleReportContext, report, sampleSigs)
 			require.NoError(t, err)
 			// queue is empty
-			require.Equal(t, mt.servers[sURL].q.pq.Len(), 0)
+			require.Equal(t, mt.servers[sURL].q.(*transmitQueue).pq.Len(), 0)
 		})
 	})
 
@@ -119,12 +121,12 @@ func Test_MercuryTransmitter_Transmit(t *testing.T) {
 		require.NoError(t, err)
 
 		// ensure it was added to the queue
-		require.Equal(t, mt.servers[sURL].q.pq.Len(), 1)
-		assert.Subset(t, mt.servers[sURL].q.pq.Pop().(*Transmission).Req.Payload, report)
-		require.Equal(t, mt.servers[sURL2].q.pq.Len(), 1)
-		assert.Subset(t, mt.servers[sURL2].q.pq.Pop().(*Transmission).Req.Payload, report)
-		require.Equal(t, mt.servers[sURL3].q.pq.Len(), 1)
-		assert.Subset(t, mt.servers[sURL3].q.pq.Pop().(*Transmission).Req.Payload, report)
+		require.Equal(t, mt.servers[sURL].q.(*transmitQueue).pq.Len(), 1)
+		assert.Subset(t, mt.servers[sURL].q.(*transmitQueue).pq.Pop().(*Transmission).Req.Payload, report)
+		require.Equal(t, mt.servers[sURL2].q.(*transmitQueue).pq.Len(), 1)
+		assert.Subset(t, mt.servers[sURL2].q.(*transmitQueue).pq.Pop().(*Transmission).Req.Payload, report)
+		require.Equal(t, mt.servers[sURL3].q.(*transmitQueue).pq.Len(), 1)
+		assert.Subset(t, mt.servers[sURL3].q.(*transmitQueue).pq.Pop().(*Transmission).Req.Payload, report)
 	})
 }
 
@@ -413,3 +415,166 @@ func Test_sortReportsLatestFirst(t *testing.T) {
 	assert.Nil(t, reports[6])
 	assert.Nil(t, reports[7])
 }
+
+type mockQ struct {
+	ch chan *Transmission
+}
+
+func newMockQ() *mockQ {
+	return &mockQ{make(chan *Transmission, 100)}
+}
+
+func (m *mockQ) Start(context.Context) error { return nil }
+func (m *mockQ) Close() error {
+	m.ch <- nil
+	return nil
+}
+func (m *mockQ) Ready() error                   { return nil }
+func (m *mockQ) HealthReport() map[string]error { return nil }
+func (m *mockQ) Name() string                   { return "" }
+func (m *mockQ) BlockingPop() (t *Transmission) {
+	val := <-m.ch
+	return val
+}
+func (m *mockQ) Push(req *pb.TransmitRequest, reportCtx ocrtypes.ReportContext) (ok bool) {
+	m.ch <- &Transmission{Req: req, ReportCtx: reportCtx}
+	return true
+}
+func (m *mockQ) Init(transmissions []*Transmission) {}
+func (m *mockQ) IsEmpty() bool                      { return false }
+
+func Test_MercuryTransmitter_runQueueLoop(t *testing.T) {
+	feedIDHex := utils.NewHash().Hex()
+	lggr := logger.TestLogger(t)
+	c := &mocks.MockWSRPCClient{}
+	db := pgtest.NewSqlxDB(t)
+	orm := NewORM(db)
+	pm := NewPersistenceManager(lggr, sURL, orm, 0, 0, 0, 0)
+	cfg := mockCfg{}
+
+	s := newServer(lggr, cfg, c, pm, sURL, feedIDHex)
+
+	req := &pb.TransmitRequest{
+		Payload:      []byte{1, 2, 3},
+		ReportFormat: 32,
+	}
+
+	t.Run("pulls from queue and transmits successfully", func(t *testing.T) {
+		transmit := make(chan *pb.TransmitRequest, 1)
+		c.TransmitF = func(ctx context.Context, in *pb.TransmitRequest) (*pb.TransmitResponse, error) {
+			transmit <- in
+			return &pb.TransmitResponse{Code: 0, Error: ""}, nil
+		}
+		q := newMockQ()
+		s.q = q
+		wg := &sync.WaitGroup{}
+		wg.Add(1)
+
+		go s.runQueueLoop(nil, wg, feedIDHex)
+
+		q.Push(req, sampleReportContext)
+
+		select {
+		case tr := <-transmit:
+			assert.Equal(t, []byte{1, 2, 3}, tr.Payload)
+			assert.Equal(t, 32, int(tr.ReportFormat))
+			// case <-time.After(testutils.WaitTimeout(t)):
+		case <-time.After(1 * time.Second):
+			t.Fatal("expected a transmit request to be sent")
+		}
+
+		q.Close()
+		wg.Wait()
+	})
+
+	t.Run("on duplicate, success", func(t *testing.T) {
+		transmit := make(chan *pb.TransmitRequest, 1)
+		c.TransmitF = func(ctx context.Context, in *pb.TransmitRequest) (*pb.TransmitResponse, error) {
+			transmit <- in
+			return &pb.TransmitResponse{Code: DuplicateReport, Error: ""}, nil
+		}
+		q := newMockQ()
+		s.q = q
+		wg := &sync.WaitGroup{}
+		wg.Add(1)
+
+		go s.runQueueLoop(nil, wg, feedIDHex)
+
+		q.Push(req, sampleReportContext)
+
+		select {
+		case tr := <-transmit:
+			assert.Equal(t, []byte{1, 2, 3}, tr.Payload)
+			assert.Equal(t, 32, int(tr.ReportFormat))
+			// case <-time.After(testutils.WaitTimeout(t)):
+		case <-time.After(1 * time.Second):
+			t.Fatal("expected a transmit request to be sent")
+		}
+
+		q.Close()
+		wg.Wait()
+	})
+	t.Run("on server-side error, does not retry", func(t *testing.T) {
+		transmit := make(chan *pb.TransmitRequest, 1)
+		c.TransmitF = func(ctx context.Context, in *pb.TransmitRequest) (*pb.TransmitResponse, error) {
+			transmit <- in
+			return &pb.TransmitResponse{Code: DuplicateReport, Error: ""}, nil
+		}
+		q := newMockQ()
+		s.q = q
+		wg := &sync.WaitGroup{}
+		wg.Add(1)
+
+		go s.runQueueLoop(nil, wg, feedIDHex)
+
+		q.Push(req, sampleReportContext)
+
+		select {
+		case tr := <-transmit:
+			assert.Equal(t, []byte{1, 2, 3}, tr.Payload)
+			assert.Equal(t, 32, int(tr.ReportFormat))
+			// case <-time.After(testutils.WaitTimeout(t)):
+		case <-time.After(1 * time.Second):
+			t.Fatal("expected a transmit request to be sent")
+		}
+
+		q.Close()
+		wg.Wait()
+	})
+	t.Run("on transmit error, retries", func(t *testing.T) {
+		transmit := make(chan *pb.TransmitRequest, 1)
+		c.TransmitF = func(ctx context.Context, in *pb.TransmitRequest) (*pb.TransmitResponse, error) {
+			transmit <- in
+			return &pb.TransmitResponse{}, errors.New("transmission error")
+		}
+		q := newMockQ()
+		s.q = q
+		wg := &sync.WaitGroup{}
+		wg.Add(1)
+		stopCh := make(chan struct{}, 1)
+
+		go s.runQueueLoop(stopCh, wg, feedIDHex)
+
+		q.Push(req, sampleReportContext)
+
+		cnt := 0
+	Loop:
+		for {
+			select {
+			case tr := <-transmit:
+				assert.Equal(t, []byte{1, 2, 3}, tr.Payload)
+				assert.Equal(t, 32, int(tr.ReportFormat))
+				if cnt > 2 {
+					break Loop
+				}
+				cnt++
+				// case <-time.After(testutils.WaitTimeout(t)):
+			case <-time.After(1 * time.Second):
+				t.Fatal("expected 3 transmit requests to be sent")
+			}
+		}
+
+		close(stopCh)
+		wg.Wait()
+	})
+}
```
