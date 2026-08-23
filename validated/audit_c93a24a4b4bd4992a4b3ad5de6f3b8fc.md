## Title
Unrecoverable actor halt on panic in per-message/per-timer closures — no reschedule of block-production, sync, catchup, or GC triggers ([File: core/async/src/tokio/runtime_handle.rs])

### Summary
The DFINITY IC fix (commit `0831b63`) addresses a class of bug where a panic inside a scheduled task's closure prevents that task from ever being rescheduled, silently stopping periodic canister work. Nearcore's `TokioRuntimeHandle`-based actor runtime has the same structural weakness, but in an even more severe form: the entire actor's message/timer-processing loop — not just one periodic job — is a single `tokio::spawn`ed task with no panic isolation around each dispatched closure.

### Finding Description
The actor loop that drives all `TokioRuntimeHandle<A>`-based actors (including `ClientActor`, `GCActor`, `ShardsManagerActor`, etc.) executes every queued message and every `run_later` delayed closure directly inline, with no `catch_unwind` boundary: [1](#0-0) 

Both regular messages and delayed actions (`run_later_boxed`) are delivered through the same `TokioRuntimeMessage.function` closure and executed at line 193: `(message.function)(&mut actor.actor, &mut runtime_handle);` with no wrapping in `std::panic::catch_unwind`.

Critical node-liveness loops are implemented as *self-rescheduling* closures exactly like the IC pattern being fixed — they call `ctx.run_later(...)` to schedule their own next invocation only *after* their body completes: [2](#0-1) [3](#0-2) [4](#0-3) 

If `check_triggers` (called from `schedule_triggers`), `Client::run_catchup` (called from `catchup`), or `GCActor::gc`/`clear_data` (called from `gc_loop`) panics for any reason, the subsequent `ctx.run_later(...)` call that reschedules the loop is never reached — exactly the bug class described in the report ("sync task not being rescheduled due to possible panic in closure").

However, because there is no `catch_unwind` isolation at the dispatch site (`runtime_handle.rs:193`), the consequence in nearcore is strictly worse than in the IC canister case: the panic unwinds out of the entire `inner_runtime_handle.spawn(async move { ... loop { tokio::select! ... } ... })` task. Tokio's task-poll wrapper catches this at the task boundary (turning it into a `JoinError`) rather than crashing the process, but the practical effect is that the *entire actor's event loop terminates permanently* — not just the one periodic trigger. For `ClientActor`, this means block production, header/state/block sync (`check_triggers`), doomslug voting, catchup, and log summary all stop simultaneously and forever, and no further network/actor messages of any kind are processed by that actor for the lifetime of the process.

### Impact Explanation
A single panic anywhere inside `check_triggers`, `run_catchup`, `gc_loop`/`clear_data`, or any other message handler dispatched through this same actor loop causes silent, permanent cessation of that actor's work with no automatic recovery or reschedule — the actor is not restarted, and the surrounding node process keeps running otherwise, giving no indication (short of the tracing panic log and a stalled join handle) that consensus-critical duties (block production, sync, catchup, GC) have stopped. This is a chain-liveness impact ("node panic ... or chain stall") consistent with the accepted impact classes: the affected node silently falls out of consensus participation and stops progressing/catching up.

### Likelihood Explanation
Likelihood depends entirely on whether an unwrap()/expect()/indexing panic is reachable inside one of these self-rescheduling bodies (`check_triggers` → sync/doomslug/block-production paths, or `run_catchup` → catchup/state-sync/block-processing paths) from externally-influenced data (blocks, chunks, state parts, or transactions flowing through the client). Nearcore's block/chunk/receipt processing paths are large and have historically contained panics reachable from malformed-but-schema-valid network data; the report itself is only a hint that this bug *class* (reschedule lost on panic) exists and was worth a dedicated fix upstream. No specific external trigger for a panic inside these functions was identified in this pass, so this should be treated as an architectural gap (missing panic-isolation in the shared actor dispatch loop) rather than a proven, immediately-triggerable exploit.

### Recommendation
Wrap dispatch of both `TokioRuntimeMessage.function` invocations and `run_later` closures in `std::panic::catch_unwind` (as is already done, for a similar reason, in `chain/chain/src/pending_shard_jobs.rs`'s `PendingShardJobs::run`), log the panic, and — for the self-rescheduling triggers specifically (`schedule_triggers`, `catchup`, `gc_loop`) — ensure the reschedule (`ctx.run_later`) is guaranteed to run even if the task body panics, e.g. via a recovery/backstop timer analogous to the one introduced by the referenced IC fix, or by restructuring these loops so `run_later` is registered before executing the task body.

### Proof of Concept
Not independently reproduced with a concrete transaction/block trigger; the finding is based on static analysis of the shared dispatch path (`core/async/src/tokio/runtime_handle.rs:159-201`) showing the absence of a panic boundary around per-message and per-timer closures, combined with the self-rescheduling pattern in `ClientActor::schedule_triggers`/`catchup` and `GCActor::gc_loop`, which reproduces the exact "panic prevents reschedule" defect class described in the referenced commit — with a wider blast radius (whole-actor halt) due to the missing `catch_unwind`.

### Citations

**File:** core/async/src/tokio/runtime_handle.rs (L159-201)
```rust
    pub fn spawn_tokio_actor(mut self, mut actor: A) {
        let mut runtime_handle = self.handle.clone();
        let inner_runtime_handle = runtime_handle.runtime_handle.clone();
        let runtime = self.runtime.take().unwrap();
        let mut receiver = self.receiver.take().unwrap();
        let shared_instrumentation = self.shared_instrumentation.clone();
        let actor_name = pretty_type_name::<A>();
        inner_runtime_handle.spawn(async move {
            actor.start_actor(&mut runtime_handle);
            // The runtime gets dropped as soon as this loop exits, cancelling all other futures on
            // the same tokio runtime.
            let _runtime = AsyncDroppableRuntime::new(runtime);
            let mut actor = CallStopWhenDropping { actor };
            let mut window_update_timer = tokio::time::interval(Duration::from_secs(1));
            loop {
                tokio::select! {
                    _ = self.system_cancellation_signal.cancelled() => {
                        tracing::debug!(target: "tokio_runtime", actor_name, "shutting down tokio runtime due to actor system shutdown");
                        break;
                    }
                    _ = runtime_handle.cancel.cancelled() => {
                        tracing::debug!(target: "tokio_runtime", actor_name, "shutting down tokio runtime due to targeted cancellation");
                        break;
                    }
                    _ = window_update_timer.tick() => {
                        tracing::trace!(target: "tokio_runtime", "advancing instrumentation window");
                        shared_instrumentation.with_thread_local_writer(|writer| writer.advance_window_if_needed());
                    }
                    Some(message) = receiver.recv() => {
                        let seq = message.seq;
                        shared_instrumentation.queue().dequeue(message.name);
                        tracing::trace!(target: "tokio_runtime", seq, actor_name, "executing message");
                        let dequeue_time_ns = shared_instrumentation.current_time().saturating_sub(message.enqueued_time_ns);
                        shared_instrumentation.with_thread_local_writer(|writer| writer.start_event(message.name, dequeue_time_ns));
                        (message.function)(&mut actor.actor, &mut runtime_handle);
                        shared_instrumentation.with_thread_local_writer(|writer| writer.end_event(message.name));
                    }
                    // Note: If the sender is closed, that stops being a selectable option.
                    // This is valid: we can spawn a tokio runtime without a handle, just to keep
                    // some futures running.
                }
            }
        });
```

**File:** chain/client/src/client_actor.rs (L1310-1316)
```rust
    fn schedule_triggers(&mut self, ctx: &mut dyn DelayedActionRunner<Self>) {
        let wait = self.check_triggers(ctx);

        ctx.run_later("ClientActor schedule_triggers", wait, move |act, ctx| {
            act.schedule_triggers(ctx);
        });
    }
```

**File:** chain/client/src/client_actor.rs (L1857-1878)
```rust
    /// Runs catchup on repeat, if this client is a validator.
    /// Schedules itself again if it was not ran as response to state parts job result
    fn catchup(&mut self, ctx: &mut dyn DelayedActionRunner<Self>) {
        {
            // An extra scope to limit the lifetime of the span.
            let _span = tracing::debug_span!(target: "client", "catchup").entered();
            if let Err(err) = self.client.run_catchup(
                &self.sync_jobs_sender.block_catch_up,
                Some(self.client.myself_sender.apply_chunks_done.clone()),
            ) {
                tracing::error!(target: "client", ?err, "error occurred during catchup for the next epoch");
            }
        }

        ctx.run_later(
            "ClientActor catchup",
            self.client.config.catchup_step_period,
            move |act, ctx| {
                act.catchup(ctx);
            },
        );
    }
```

**File:** chain/client/src/gc_actor.rs (L100-105)
```rust
    fn gc_loop(&mut self, ctx: &mut dyn DelayedActionRunner<Self>) {
        self.gc();
        ctx.run_later("garbage collection", self.gc_config.gc_step_period, move |act, ctx| {
            act.gc_loop(ctx);
        });
    }
```
