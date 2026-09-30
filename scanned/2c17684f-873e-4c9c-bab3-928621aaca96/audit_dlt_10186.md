# [?] Merge pull request #5438 from oasisprotocol/kostko/fix/rt-sandbox-deadlock

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2023-11-13
Source: https://github.com/oasisprotocol/oasis-core/commit/12a5d629c9a6e021c20efda231bfa1aff4d5ef50
Type: security-commit

## Details
Merge pull request #5438 from oasisprotocol/kostko/fix/rt-sandbox-deadlock

go/runtime/host/sandbox: Release lock before calling into runtime

## Patch
### .changelog/5438.bugfix.2.md
```diff
@@ -0,0 +1 @@
+go/worker/compute: Bound batch execution time
```

### .changelog/5438.bugfix.md
```diff
@@ -0,0 +1,5 @@
+go/runtime/host/sandbox: Release lock before calling into runtime
+
+Similar to how this is handled in the multi runtime host, we need to
+release the lock before calling into the runtime as otherwise this could
+lead to a deadlock in certain situations.
```

### go/runtime/host/sandbox/sandbox.go
```diff
@@ -136,21 +136,13 @@ func (r *sandboxedRuntime) ID() common.Namespace {
 }
 
 // Implements host.Runtime.
-func (r *sandboxedRuntime) GetInfo(ctx context.Context) (rsp *protocol.RuntimeInfoResponse, err error) {
-	callFn := func() error {
-		r.RLock()
-		defer r.RUnlock()
-
-		if r.conn == nil {
-			return errRuntimeNotReady
-		}
-		rsp, err = r.conn.GetInfo()
-		return err
+func (r *sandboxedRuntime) GetInfo(ctx context.Context) (*protocol.RuntimeInfoResponse, error) {
+	conn, err := r.getConnection(ctx)
+	if err != nil {
+		return nil, err
 	}
 
-	// Retry call in case the runtime is not yet ready.
-	err = backoff.Retry(callFn, backoff.WithContext(cmnBackoff.NewExponentialBackOff(), ctx))
-	return
+	return conn.GetInfo()
 }
 
 // Implements host.Runtime.
@@ -165,25 +157,39 @@ func (r *sandboxedRuntime) GetCapabilityTEE() (*node.CapabilityTEE, error) {
 }
 
 // Implements host.Runtime.
-func (r *sandboxedRuntime) Call(ctx context.Context, body *protocol.Body) (rsp *protocol.Body, err error) {
-	callFn := func() error {
+func (r *sandboxedRuntime) Call(ctx context.Context, body *protocol.Body) (*protocol.Body, error) {
+	conn, err := r.getConnection(ctx)
+	if err != nil {
+		return nil, err
+	}
+
+	// Take care to release lock before calling into the runtime as otherwise this could lead to a
+	// deadlock in case the runtime makes a call that acquires the cross node lock and at the same
+	// time SetVersion is being called to update the version with the cross node lock acquired.
+
+	return conn.Call(ctx, body)
+}
+
+func (r *sandboxedRuntime) getConnection(ctx context.Context) (protocol.Connection, error) {
+	var conn protocol.Connection
+	getConnFn := func() error {
 		r.RLock()
 		defer r.RUnlock()
 
 		if r.conn == nil {
 			return errRuntimeNotReady
 		}
-		rsp, err = r.conn.Call(ctx, body)
-		if err != nil {
-			// All protocol-level errors are permanent.
-			return backoff.Permanent(err)
-		}
+		conn = r.conn
+
 		return nil
 	}
-
 	// Retry call in case the runtime is not yet ready.
-	err = backoff.Retry(callFn, backoff.WithContext(cmnBackoff.NewExponentialBackOff(), ctx))
-	return
+	err := backoff.Retry(getConnFn, backoff.WithContext(cmnBackoff.NewExponentialBackOff(), ctx))
+	if err != nil {
+		return nil, err
+	}
+
+	return conn, nil
 }
 
 // Implements host.Runtime.
@@ -421,8 +427,8 @@ func (r *sandboxedRuntime) startProcess() (err error) {
 	}
 
 	ok = true
-	r.Lock()
 	r.process = p
+	r.Lock()
 	r.conn = pc
 	r.capabilityTEE = ev.CapabilityTEE
 	r.Unlock()
@@ -464,9 +470,9 @@ func (r *sandboxedRuntime) handleAbortRequest(rq *abortRequest) error {
 
 	// Remove the process so it will be respanwed (it would be respawned either way, but with an
 	// additional "unexpected termination" message).
-	r.Lock()
 	r.conn.Close()
 	r.process = nil
+	r.Lock()
 	r.conn = nil
 	r.capabilityTEE = nil
 	r.Unlock()
@@ -580,9 +586,9 @@ func (r *sandboxedRuntime) manager() {
 				"err", r.process.Error(),
 			)
 
-			r.Lock()
 			r.conn.Close()
 			r.process = nil
+			r.Lock()
 			r.conn = nil
 			r.capabilityTEE = nil
 			r.Unlock()
```

### go/worker/compute/executor/committee/node.go
```diff
@@ -45,6 +45,10 @@ var (
 	getInfoTimeout = 5 * time.Second
 )
 
+// executeBatchTimeoutFactor is the factor F in calculation of the batch execution timeout using
+// the formula F * ProposerTimeout to ensure that a broken runtime doesn't block forever.
+const executeBatchTimeoutFactor = 3
+
 // Node is a committee node.
 type Node struct { // nolint: maligned
 	runtimeReady         bool
@@ -186,7 +190,7 @@ func (n *Node) transitionState(state NodeState) {
 }
 
 func (n *Node) transitionStateToProcessing(ctx context.Context, proposal *commitment.Proposal, rank uint64, batch transaction.RawBatch) {
-	ctx, cancel := context.WithCancel(ctx)
+	ctx, cancel := context.WithCancelCause(ctx)
 	done := make(chan struct{})
 
 	n.transitionState(StateProcessingBatch{
@@ -220,7 +224,7 @@ func (n *Node) transitionStateToProcessingFailure(
 		"max_batch_size", maxBatchSize,
 	)
 
-	cancel := func() {}
+	cancel := func(_ error) {}
 	done := make(chan struct{})
 	close(done)
 
@@ -415,7 +419,7 @@ func (n *Node) scheduleBatch(ctx context.Context, round uint64, force bool) {
 		return
 	}
 
-	ctx, cancel := context.WithCancel(ctx)
+	ctx, cancel := context.WithCancelCause(ctx)
 	done := make(chan struct{})
 
 	n.transitionState(StateProcessingBatch{
@@ -686,15 +690,26 @@ func (n *Node) runtimeExecuteTxBatch(
 		batchRuntimeProcessingTime.With(n.getMetricLabels()).Observe(time.Since(rtStartTime).Seconds())
 	}()
 
-	rsp, err := rt.Call(ctx, rq)
+	// Ensure batch execution is bounded.
+	proposerTimeout := state.Runtime.TxnScheduler.ProposerTimeout
+	callCtx, cancelCallFn := context.WithTimeoutCause(
+		ctx,
+		executeBatchTimeoutFactor*proposerTimeout,
+		errors.New("proposer timeout expired"),
+	)
+	defer cancelCallFn()
+
+	rsp, err := rt.Call(callCtx, rq)
 	switch {
 	case err == nil:
 	case errors.Is(err, context.Canceled):
 		// Context was canceled while the runtime was processing a request.
-		n.logger.Error("batch processing aborted by context, restarting runtime")
+		n.logger.Error("batch processing aborted by context, restarting runtime",
+			"cause", context.Cause(callCtx),
+		)
 
 		// Abort the runtime, so we can start processing the next batch.
-		abortCtx, cancel := context.WithTimeout(n.ctx, abortTimeout)
+		abortCtx, cancel := context.WithTimeout(ctx, abortTimeout)
 		defer cancel()
 
 		if err = rt.Abort(abortCtx, false); err != nil {
@@ -778,7 +793,7 @@ func (n *Node) abortBatch(state *StateProcessingBatch) {
 	n.logger.Warn("aborting processing batch")
 
 	// Stop processing.
-	state.Cancel()
+	state.Cancel(errors.New("batch aborted"))
 
 	// Discard the result if there was any.
 	select {
@@ -1500,8 +1515,8 @@ func (n *Node) worker() {
 			var wg sync.WaitGroup
 			defer wg.Wait()
 
-			ctx, cancel := context.WithCancel(n.ctx)
-			defer cancel()
+			ctx, cancel := context.WithCancelCause(n.ctx)
+			defer cancel(errors.New("round finished"))
 
 			wg.Add(1)
 			go func() {
```

### go/worker/compute/executor/committee/state.go
```diff
@@ -141,7 +141,7 @@ type StateProcessingBatch struct {
 	// Timing for this batch.
 	batchStartTime time.Time
 	// Function for cancelling batch processing.
-	cancelFn context.CancelFunc
+	cancelFn context.CancelCauseFunc
 	// Channel which will provide the result.
 	done chan struct{}
 }
@@ -157,8 +157,8 @@ func (s StateProcessingBatch) String() string {
 }
 
 // Cancel invokes the cancellation function and waits for the processing to actually stop.
-func (s *StateProcessingBatch) Cancel() {
-	s.cancelFn()
+func (s *StateProcessingBatch) Cancel(cause error) {
+	s.cancelFn(cause)
 	<-s.done
 }
 
```

### runtime/Cargo.toml
```diff
@@ -70,6 +70,11 @@ jsonrpc = { version = "0.13.0", features = ["simple_uds"] }
 tempfile = "3.4.0"
 tendermint-testgen = "0.30.0"
 
+[features]
+default = []
+# Enables debug-level logging in release builds.
+debug-logging = ["slog/max_level_debug", "slog/release_max_level_debug"]
+
 [[bin]]
 name = "fuzz-mkvs-proof"
 path = "fuzz/mkvs_proof.rs"
```

### runtime/src/dispatcher.rs
```diff
@@ -1,10 +1,7 @@
 //! Runtime call dispatcher.
 use std::{
     convert::TryInto,
-    sync::{
-        atomic::{AtomicBool, Ordering},
-        Arc, Condvar, Mutex,
-    },
+    sync::{Arc, Condvar, Mutex},
     thread,
 };
 
@@ -150,15 +147,13 @@ struct State {
 #[derive(Debug)]
 enum Command {
     Request(u64, Body),
-    Abort(mpsc::Sender<()>),
 }
 
 /// Runtime call dispatcher.
 pub struct Dispatcher {
     logger: Logger,
     queue_tx: mpsc::Sender<Command>,
     identity: Arc<Identity>,
-    abort_batch: Arc<AtomicBool>,
 
     state: Mutex<Option<ProtocolState>>,
     state_cond: Condvar,
@@ -179,7 +174,6 @@ impl Dispatcher {
             logger: get_logger("runtime/dispatcher"),
             queue_tx: tx,
             identity,
-            abort_batch: Arc::new(AtomicBool::new(false)),
             state: Mutex::new(None),
             state_cond: Condvar::new(),
             tokio_runtime,
@@ -212,17 +206,6 @@ impl Dispatcher {
         Ok(())
     }
 
-    /// Signals to dispatcher that it should abort and waits for the abort to
-    /// complete.
-    pub fn abort_and_wait(&self) -> AnyResult<()> {
-        self.abort_batch.store(true, Ordering::SeqCst);
-        // Queue an abort command and wait for it to be processed.
-        let (tx, mut rx) = mpsc::channel(1);
-        self.queue_tx.blocking_send(Command::Abort(tx))?;
-        rx.blocking_recv();
-        Ok(())
-    }
-
     fn run(self: &Arc<Self>, initializer: Box<dyn Initializer>, mut rx: mpsc::Receiver<Command>) {
         // Wait for the state to be available.
         let ProtocolState {
@@ -249,10 +232,9 @@ impl Dispatcher {
             consensus_verifier: &consensus_verifier,
         };
         let post_init_state = initializer.init(pre_init_state);
-        let mut txn_dispatcher = post_init_state
+        let txn_dispatcher = post_init_state
             .txn_dispatcher
             .unwrap_or_else(|| Box::<TxnNoopDispatcher>::default());
-        txn_dispatcher.set_abort_batch_flag(self.abort_batch.clone());
 
         let state = State {
             protocol: protocol.clone(),
@@ -294,10 +276,6 @@ impl Dispatcher {
                             protocol.send_response(id, response).unwrap();
                         });
                     }
-                    Command::Abort(tx) => {
-                        // Request to abort processing.
-                        tx.send(()).await.unwrap();
-                    }
                 }
             }
         });
```

### runtime/src/protocol.rs
```diff
@@ -367,10 +367,7 @@ impl Protocol {
             }
             Body::RuntimeAbortRequest {} => {
                 info!(self.logger, "Received worker abort request");
-                self.ensure_initialized()?;
-                self.dispatcher.abort_and_wait()?;
-                info!(self.logger, "Handled worker abort request");
-                Ok(Some(Body::RuntimeAbortResponse {}))
+                Err(ProtocolError::MethodNotSupported.into())
             }
 
             // Attestation-related requests.
```
