# [?] Fix race condition in shutdown:

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2019-08-06
Source: https://github.com/cometbft/cometbft/commit/e4913f533a390117086879bbaa09f48115a0d925
Type: security-commit

## Details
Fix race condition in shutdown:

    + ensure that we stop accepting messages once `stop` has been called
      to avoid the case in which we attempt to write to a channel which
      has already been closed

## Patch
### blockchain/v2/reactor.go
```diff
@@ -3,8 +3,6 @@ package v2
 import (
 	"fmt"
 	"time"
-
-	"github.com/tendermint/tendermint/libs/log"
 )
 
 func schedulerHandle(event Event) (Events, error) {
@@ -40,14 +38,11 @@ type Reactor struct {
 	tickerStopped chan struct{}
 }
 
+// TODO: setLogger should set loggers of the routines
 func (r *Reactor) Start() {
-	logger := log.TestingLogger()
-
 	// what is the best way to get the events out of the routine
 	r.scheduler = newRoutine("scheduler", schedulerHandle)
-	r.scheduler.setLogger(logger)
 	r.processor = newRoutine("processor", processorHandle)
-	r.processor.setLogger(logger)
 	// so actually the demuxer only needs to read from events
 	r.demuxer = newDemuxer(r.scheduler, r.processor)
 	r.tickerStopped = make(chan struct{})
```

### blockchain/v2/routine.go
```diff
@@ -26,6 +26,7 @@ type Routine struct {
 	handle   handleFunc
 	logger   log.Logger
 	metrics  *Metrics
+	stopping *uint32
 }
 
 func newRoutine(name string, handleFunc handleFunc) *Routine {
@@ -38,6 +39,7 @@ func newRoutine(name string, handleFunc handleFunc) *Routine {
 		stopped:  make(chan struct{}, 1),
 		finished: make(chan error, 1),
 		running:  new(uint32),
+		stopping: new(uint32),
 		logger:   log.NewNopLogger(),
 		metrics:  NopMetrics(),
 	}
@@ -60,13 +62,16 @@ func (rt *Routine) run() {
 	errorsDrained := false
 	for {
 		if !rt.isRunning() {
+			rt.logger.Info(fmt.Sprintf("%s: breaking because not running\n", rt.name))
 			break
 		}
 		select {
 		case iEvent, ok := <-rt.input:
 			rt.metrics.EventsIn.With("routine", rt.name).Add(1)
 			if !ok {
 				if !errorsDrained {
+					rt.logger.Info(fmt.Sprintf("%s: waiting for errors to drain\n", rt.name))
+
 					continue // wait for errors to be drainned
 				}
 				rt.logger.Info(fmt.Sprintf("%s: stopping\n", rt.name))
@@ -112,11 +117,11 @@ func (rt *Routine) feedback() {
 	}
 }
 
-// XXX: this should be called trySend for consistency
 func (rt *Routine) send(event Event) bool {
-	if !rt.isRunning() {
+	if !rt.isRunning() || rt.isStopping() {
 		return false
 	}
+
 	rt.logger.Info(fmt.Sprintf("%s: sending %+v", rt.name, event))
 	if err, ok := event.(error); ok {
 		select {
@@ -145,6 +150,10 @@ func (rt *Routine) isRunning() bool {
 	return atomic.LoadUint32(rt.running) == 1
 }
 
+func (rt *Routine) isStopping() bool {
+	return atomic.LoadUint32(rt.stopping) == 1
+}
+
 func (rt *Routine) output() chan Event {
 	return rt.out
 }
@@ -153,7 +162,13 @@ func (rt *Routine) stop() {
 	if !rt.isRunning() {
 		return
 	}
+
 	rt.logger.Info(fmt.Sprintf("%s: stop\n", rt.name))
+	stopping := atomic.CompareAndSwapUint32(rt.stopping, uint32(0), uint32(1))
+	if !stopping {
+		panic("Routine has already stopped")
+	}
+
 	close(rt.input)
 	close(rt.errors)
 	<-rt.stopped
@@ -172,3 +187,8 @@ func (rt *Routine) terminate(reason error) {
 func (rt *Routine) wait() error {
 	return <-rt.finished
 }
+
+/*
+	Problem:
+		We can't write to channels from one thread and close channels from another thread
+*/
```

### blockchain/v2/routine_test.go
```diff
@@ -6,6 +6,7 @@ import (
 	"time"
 
 	"github.com/stretchr/testify/assert"
+	"github.com/tendermint/tendermint/libs/log"
 )
 
 type eventA struct{}
@@ -86,6 +87,7 @@ func genStatefulHandler(maxCount int) handleFunc {
 func TestStatefulRoutine(t *testing.T) {
 	handler := genStatefulHandler(10)
 	routine := newRoutine("statefulRoutine", handler)
+	routine.setLogger(log.TestingLogger())
 
 	go routine.run()
 	go routine.feedback()
@@ -97,7 +99,7 @@ func TestStatefulRoutine(t *testing.T) {
 		time.Sleep(10 * time.Millisecond)
 	}
 
-	go routine.send(eventA{})
+	routine.send(eventA{})
 
 	routine.stop()
 }
@@ -114,7 +116,6 @@ func handleWithErrors(event Event) (Events, error) {
 
 func TestErrorSaturation(t *testing.T) {
 	routine := newRoutine("errorRoutine", handleWithErrors)
-
 	go routine.run()
 	go func() {
 		for {
```
