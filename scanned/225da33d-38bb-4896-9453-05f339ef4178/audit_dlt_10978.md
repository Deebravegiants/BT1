# [?] fix: splicing deadlock  (#932)

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2025-11-06
Source: https://github.com/succinctlabs/sp1/commit/a4da1fb350015f5b6e1704a4b856430343913369
Type: security-commit

## Details
fix: splicing deadlock  (#932)

* try to catch panic

* spans

* logs

* set err

* try fix

* unblock

* log

* forgot to loop

* better logs

* fmt

* fmt again

## Patch
### crates/prover/src/worker/controller/core.rs
```diff
@@ -160,12 +160,15 @@ where
         // Initialize the final vm state.
         let final_vm_state = FinalVmStateLock::new();
 
+        // Create the channel to send the splicing tasks to the splicing pipeline spawner task.
+        // This is a bounded channel in order to create a backpressure mechanism for the minimal
+        // executor chunk producer.
+        let (splicing_task_tx, mut splicing_task_rx) = mpsc::channel(2);
         // Start the minimal executor.
         let parent = tracing::Span::current();
         // TODO: think about cancellation handling
         let minimal_executor_handle = tokio::task::spawn_blocking({
             let program = program.clone();
-            let splicing_engine = self.splicing_engine.clone();
             let elf = self.elf.clone();
             let common_input_artifact = self.common_input.clone();
             let proof_id = self.proof_id.clone();
@@ -178,25 +181,22 @@ where
             let opts = opts.clone();
             move || {
                 let _guard = parent.enter();
-
-                let _minimal_exec_span = tracing::debug_span!("minimal executor task").entered();
                 let max_trace_size = opts.minimal_trace_chunk_threshold;
-                let mut minimal_executor =
-                    MinimalExecutor::tracing(program.clone(), max_trace_size);
-
+                let mut minimal_executor = tracing::info_span!("minimal executor initialization")
+                    .in_scope(|| MinimalExecutor::tracing(program.clone(), max_trace_size));
                 // Write input to the minimal executor.
                 for buf in stdin.buffer.iter() {
                     minimal_executor.with_input(buf);
                 }
-
-                let splicing_handles = FuturesUnordered::new();
                 tracing::info!("Starting minimal executor");
                 let now = std::time::Instant::now();
+                let mut chunk_count = 0;
                 while let Some(chunk) = minimal_executor.execute_chunk() {
-                    tracing::trace!("program is done?: {}", minimal_executor.is_done());
-                    tracing::trace!(
-                        "mem reads chunk size bytes {}",
-                        chunk.num_mem_reads() * std::mem::size_of::<sp1_jit::MemValue>() as u64
+                    tracing::info!(
+                        trace_chunk = chunk_count,
+                        "mem reads chunk size bytes {}, program is done?: {}",
+                        chunk.num_mem_reads() * std::mem::size_of::<sp1_jit::MemValue>() as u64,
+                        minimal_executor.is_done()
                     );
 
                     // Create a splicing task
@@ -215,46 +215,95 @@ where
                         requester_id: requester_id.clone(),
                         opts: opts.clone(),
                     };
+                    // Send the splicing task to the splicing pipeline spawner task.
+                    splicing_task_tx
+                        .blocking_send((chunk_count, task))
+                        .map_err(|e| anyhow::anyhow!("failed to send splicing task: {}", e))?;
 
-                    let splicing_handle = splicing_engine
-                        .blocking_submit(task)
-                        .expect("failed to submit splicing task");
-
-                    splicing_handles.push(splicing_handle);
+                    chunk_count += 1;
                 }
                 let elapsed = now.elapsed().as_secs_f64();
                 tracing::info!(
                     "executor finished. elapsed: {}s, mhz: {}",
                     elapsed,
                     minimal_executor.global_clk() as f64 / (elapsed * 1e6)
                 );
-                (minimal_executor, splicing_handles)
+                Ok::<_, TaskError>(minimal_executor)
             }
         });
 
-        let (minimal_executor, splicing_handles) =
-            minimal_executor_handle.await.expect("executor task panicked");
-
-        // Wait for splicing tasks to finish, catch any potential errors
-        splicing_handles
-            .map(|nested| {
-                let result = nested.map_err(|e| anyhow::anyhow!("splicing task panicked: {}", e));
-                let result =
-                    result.and_then(|r| r.map_err(|e| anyhow::anyhow!("execution error: {}", e)));
-                result
-            })
-            .try_collect::<Vec<()>>()
-            .await?;
-        tracing::trace!("splicing tasks finished");
+        let (splicing_submit_tx, mut splicing_submit_rx) = mpsc::unbounded_channel();
+        let submit_splicers_handle = tokio::task::spawn({
+            let splicing_engine = self.splicing_engine.clone();
+            async move {
+                while let Some((chunk_count, task)) = splicing_task_rx.recv().await {
+                    tracing::info!(idx = chunk_count, "Submitting splicing task");
+                    let time = std::time::Instant::now();
+                    let splicing_handle = splicing_engine
+                        .submit(task)
+                        .await
+                        .map_err(|e| anyhow::anyhow!("failed to submit splicing task: {}", e))?;
+                    let elapsed = time.elapsed().as_secs_f64();
+                    tracing::info!(
+                        trace_chunk = chunk_count,
+                        wait_time = elapsed,
+                        "Splicing task submitted"
+                    );
+                    splicing_submit_tx
+                        .send((chunk_count, splicing_handle))
+                        .map_err(|e| anyhow::anyhow!("failed to send splicing handle: {}", e))?;
+                }
+
+                Ok::<_, TaskError>(())
+            }
+        });
+        let wait_for_splicers_handle = tokio::task::spawn({
+            async move {
+                let mut splicing_handles = FuturesUnordered::new();
+                loop {
+                    tokio::select! {
+                        Some((chunk_count, splicing_handle)) = splicing_submit_rx.recv() => {
+                            tracing::info!(chunk_count = chunk_count, "Received splicing handle");
+                            let handle = splicing_handle.map_ok(move |_| chunk_count);
+                            splicing_handles.push(handle);
+                        }
+                        Some(result) = splicing_handles.next() => {
+                            let chunk_count = result.map_err(|e| anyhow::anyhow!("splicing task panicked: {}", e))?;
+                            tracing::info!(chunk_count = chunk_count, "Splicing task finished");
+                        }
+                        else => {
+                            tracing::info!("No more splicing handles to receive");
+                            break;
+                        }
+                    }
+                }
+                Ok::<_, TaskError>(())
+            }
+        });
+        // Wait for the minimal executor to finish
+        let minimal_executor = minimal_executor_handle
+            .await
+            .map_err(|e| anyhow::anyhow!("minimal executor failed: {}", e))??;
+        // Wait for the splicer tasks to be submitted to the pipeline
+        submit_splicers_handle
+            .await
+            .map_err(|e| anyhow::anyhow!("failed to submit splicers: {}", e))??;
+        // Wait for the splicers to finish
+        wait_for_splicers_handle
+            .await
+            .map_err(|e| anyhow::anyhow!("failed to wait for splicer tasks: {}", e))??;
 
         let touched_addresses = all_touched_addresses.take();
-        let final_state = *final_vm_state.get().expect("final vm state not set");
+        let final_state = *final_vm_state
+            .get()
+            .ok_or(TaskError::Fatal(anyhow::anyhow!("final vm state not set")))?;
 
         let cycles = minimal_executor.global_clk();
         let public_value_stream = minimal_executor.public_values_stream().clone();
 
         let output = ExecutionOutput { cycles, public_value_stream };
 
+        tracing::info!("emitting global memory shards");
         self.emit_global_memory_shards(
             minimal_executor,
             program,
@@ -280,10 +329,9 @@ where
 
         let (shard_data_tx, mut shard_data_rx) = mpsc::channel(1);
 
-        let mut join_set = JoinSet::new();
-
+        let mut join_set = JoinSet::<anyhow::Result<()>>::new();
         // Spawn the task that creates the memory shards
-        let span = tracing::debug_span!("create global memory shards");
+        let span = tracing::info_span!("create global memory shards");
         join_set.spawn_blocking({
             let threshold = split_opts.memory;
             move || {
@@ -305,26 +353,32 @@ where
                         itertools::EitherOrBoth::Left(initialize_events) => {
                             let initialize_events =
                                 initialize_events.into_iter().collect::<Vec<_>>();
-                            shard_data_tx
-                                .blocking_send((initialize_events, vec![]))
-                                .expect("failed to send initialize events");
+                            shard_data_tx.blocking_send((initialize_events, vec![])).map_err(
+                                |e| anyhow::anyhow!("failed to send initialize events: {}", e),
+                            )?;
                         }
                         itertools::EitherOrBoth::Right(finalize_events) => {
                             let finalize_events = finalize_events.into_iter().collect::<Vec<_>>();
-                            shard_data_tx
-                                .blocking_send((vec![], finalize_events))
-                                .expect("failed to send finalize events");
+                            shard_data_tx.blocking_send((vec![], finalize_events)).map_err(
+                                |e| anyhow::anyhow!("failed to send finalize events: {}", e),
+                            )?;
                         }
                         itertools::EitherOrBoth::Both(initialize_events, finalize_events) => {
                             let initialize_events =
                                 initialize_events.into_iter().collect::<Vec<_>>();
                             let finalize_events = finalize_events.into_iter().collect::<Vec<_>>();
                             shard_data_tx
                                 .blocking_send((initialize_events, finalize_events))
-                                .expect("failed to send events");
+                                .map_err(|e| {
+                                    anyhow::anyhow!(
+                                        "failed to send initialize and finalize events: {}",
+                                        e
+                                    )
+                                })?;
                         }
                     }
                 }
+                Ok(())
             }
         });
 
@@ -348,7 +402,7 @@ where
                 let mut previous_init_page_idx = 0;
                 let mut previous_finalize_page_idx = 0;
                 while let Some((initialize_events, finalize_events)) = shard_data_rx.recv().await {
-                    tracing::trace!("Got global memory shard number {counter}");
+                    tracing::info!("Got global memory shard number {counter}");
                     let last_init_addr = initialize_events
                         .last()
                         .map(|event| event.addr)
@@ -394,19 +448,17 @@ where
 
                     // Upload the data
                     let data_artifact = artifact_client
-                        .create_artifact()
-                        .expect("failed to create record artifact");
+                        .create_artifact()?;
                     artifact_client
                         .upload(&data_artifact, data)
-                        .await
-                        .expect("failed to upload record");
+                        .await?;
 
                     let deferred_marker_artifact =
                         Artifact::from("global memory dummy artifact".to_string());
 
                     // Allocate an artifact for the proof
                     let proof_artifact =
-                        artifact_client.create_artifact().expect("failed to create proof artifact");
+                        artifact_client.create_artifact().map_err(|e| anyhow::anyhow!("failed to create proof artifact: {}", e))?;
 
                     let dummy_output_artifact =
                         Artifact::from("dummy global memory deferred output artifact".to_string());
@@ -423,30 +475,35 @@ where
                         parent_context: parent_context.clone(),
                         requester_id: requester_id.clone(),
                     };
-                    let task = request.into_raw().expect("failed to convert to raw task request");
+                    let task = request.into_raw().map_err(|e| anyhow::anyhow!("failed to convert to raw task request: {}", e))?;
 
                     // Send the task to the worker.
+                    tracing::info!("Submitting prove shard task");
                     let task_id = worker_client
                         .submit_task(TaskType::ProveShard, task)
+                        .instrument(tracing::info_span!("submit prove shard task"))
                         .await
-                        .expect("failed to send task");
+                        .map_err(|e| anyhow::anyhow!("failed to send task: {}", e))?;
 
                     // Send the task data
                     let proof_data = ProofData { task_id, range, proof: proof_artifact };
-                    prove_shard_tx.send(proof_data).expect("failed to send task id");
-                    tracing::debug!("Submitted memory global shard {counter}");
+                    prove_shard_tx.send(proof_data).map_err(|e| anyhow::anyhow!("failed to send task id: {}", e))?;
+                    tracing::info!("Submitted memory global shard {counter}");
                     counter += 1;
                     previous_init_addr = last_init_addr;
                     previous_finalize_addr = last_finalize_addr;
                     previous_init_page_idx = last_init_page_idx;
                     previous_finalize_page_idx = last_finalize_page_idx;
                 }
+                Ok(())
             }
-            .instrument(tracing::debug_span!("Global memory shards"))
+            .instrument(tracing::info_span!("Global memory shards"))
         });
 
-        // Wait for the tasks to finish
-        join_set.join_all().await;
+        // Wait for the tasks to finish and collect the errors.
+        while let Some(result) = join_set.join_next().await {
+            result.map_err(|e| anyhow::anyhow!("global memory shards task panicked: {}", e))??;
+        }
 
         Ok(())
     }
@@ -570,8 +627,10 @@ impl FinalVmStateLock {
         Self { inner: Arc::new(OnceLock::new()) }
     }
 
-    pub fn set(&self, state: FinalVmState) {
-        self.inner.set(state).expect("final vm state already set");
+    pub fn set(&self, state: FinalVmState) -> Result<(), TaskError> {
+        self.inner
+            .set(state)
+            .map_err(|_| TaskError::Fatal(anyhow::anyhow!("final vm state already set")))
     }
 
     pub fn get(&self) -> Option<&FinalVmState> {
```

### crates/prover/src/worker/controller/splicing.rs
```diff
@@ -187,62 +187,65 @@ where
             mpsc::unbounded_channel::<DeferredMessage>();
 
         let mut join_set = JoinSet::<Result<(), ExecutionError>>::new();
-
         // Spawn the task to spawn the prove shard tasks.
-        let parent = tracing::Span::current();
-        join_set.spawn({
-            let self_clone = self.clone();
-            let elf_artifact = elf_artifact.clone();
-            let common_input_artifact = common_input_artifact.clone();
-            let proof_id = proof_id.clone();
-            let requester_id = requester_id.clone();
-            let parent_id_clone = parent_id.clone();
-            let parent_context_clone = parent_context.clone();
-            let prove_shard_tx = prove_shard_tx.clone();
-            async move {
-                let _guard = parent.enter();
-                while let Some(task) = splicing_rx.recv().await {
-                    let SendSpliceTask { chunk, range } = task;
-                    let chunk_bytes = bincode::serialize(&chunk)
-                        .map_err(|e| ExecutionError::Other(e.to_string()))?;
-                    let data = TraceData::Core(chunk_bytes);
-
-                    let SpawnProveOutput { deferred_message, proof_data } = self_clone
-                        .create_core_proving_task(
-                            elf_artifact.clone(),
-                            common_input_artifact.clone(),
-                            proof_id.clone(),
-                            requester_id.clone(),
-                            parent_id_clone.clone(),
-                            parent_context_clone.clone(),
-                            range,
-                            data,
-                        )
-                        .await
-                        .map_err(|e| {
-                            ExecutionError::Other(format!(
-                                "error in create_core_proving_task: {}",
-                                e
-                            ))
-                        })?;
-
-                    prove_shard_tx.send(proof_data).map_err(|e| {
-                        ExecutionError::Other(format!("error in send proof data: {}", e))
-                    })?;
-                    // Send the deferred message to the deferred marker receiver.
-                    if let Some(deferred_message) = deferred_message {
-                        deferred_marker_tx.send(deferred_message).map_err(|e| {
-                            ExecutionError::Other(format!("error in send deferred message: {}", e))
+        join_set.spawn(
+            {
+                let self_clone = self.clone();
+                let elf_artifact = elf_artifact.clone();
+                let common_input_artifact = common_input_artifact.clone();
+                let proof_id = proof_id.clone();
+                let requester_id = requester_id.clone();
+                let parent_id_clone = parent_id.clone();
+                let parent_context_clone = parent_context.clone();
+                let prove_shard_tx = prove_shard_tx.clone();
+                async move {
+                    while let Some(task) = splicing_rx.recv().await {
+                        let SendSpliceTask { chunk, range } = task;
+                        let chunk_bytes = bincode::serialize(&chunk)
+                            .map_err(|e| ExecutionError::Other(e.to_string()))?;
+                        let data = TraceData::Core(chunk_bytes);
+
+                        let SpawnProveOutput { deferred_message, proof_data } = self_clone
+                            .create_core_proving_task(
+                                elf_artifact.clone(),
+                                common_input_artifact.clone(),
+                                proof_id.clone(),
+                                requester_id.clone(),
+                                parent_id_clone.clone(),
+                                parent_context_clone.clone(),
+                                range,
+                                data,
+                            )
+                            .await
+                            .map_err(|e| {
+                                ExecutionError::Other(format!(
+                                    "error in create_core_proving_task: {}",
+                                    e
+                                ))
+                            })?;
+
+                        prove_shard_tx.send(proof_data).map_err(|e| {
+                            ExecutionError::Other(format!("error in send proof data: {}", e))
                         })?;
+                        // Send the deferred message to the deferred marker receiver.
+                        if let Some(deferred_message) = deferred_message {
+                            deferred_marker_tx.send(deferred_message).map_err(|e| {
+                                ExecutionError::Other(format!(
+                                    "error in send deferred message: {}",
+                                    e
+                                ))
+                            })?;
+                        }
                     }
-                }
 
-                Ok(())
+                    Ok(())
+                }
             }
-        });
+            .in_current_span(),
+        );
 
         // Spawn the task that splices the trace.
-        let span = tracing::debug_span!("splicing trace");
+        let span = tracing::info_span!("splicing trace chunk");
         join_set.spawn_blocking(move || {
             let _guard = span.enter();
             let mut touched_addresses = CompressedMemory::new();
@@ -259,18 +262,12 @@ where
                     deferred_proof: num_deferred_proofs as u64,
                 };
             loop {
-                tracing::debug!("starting new shard at clk: {} at pc: {}", vm.core.clk(), vm.core.pc());
+                tracing::info!("starting new shard at clk: {} at pc: {}", vm.core.clk(), vm.core.pc());
                 match vm.execute()? {
                     CycleResult::ShardBoundry => {
                         // Note: Chunk implentations should always be cheap to clone.
                         if let Some(spliced) = vm.splice(chunk.clone()) {
-                            tracing::trace!("shard ended at clk: {}", vm.core.clk());
-                            tracing::trace!("shard ended at pc: {}", vm.core.pc());
-                            tracing::trace!("shard ended at global clk: {}", vm.core.global_clk());
-                            tracing::trace!(
-                                "shard ended with {} mem reads left ",
-                                vm.core.mem_reads.len()
-                            );
+                            tracing::info!(global_clk = vm.core.global_clk(), pc = vm.core.pc(), num_mem_reads_left = vm.core.mem_reads.len(), clk = vm.core.clk(), "shard boundary");
                             // Get the end boundary of the shard.
                             let end = ShardBoundary {
                                 timestamp: vm.core.clk(),
@@ -291,18 +288,12 @@ where
                                 start_num_mem_reads as usize - vm.core.mem_reads.len(),
                             );
                             let splice_to_send = std::mem::replace(&mut last_splice, spliced);
-
-                            // TODO: handle errors.
+                            tracing::info!(global_clk = vm.core.global_clk(), "sending spliced trace to splicing tx");
                             splicing_tx.blocking_send(SendSpliceTask { chunk: splice_to_send, range })
                                 .map_err(|e| ExecutionError::Other(format!("error sending to splicing tx: {}", e)))?;
+                            tracing::info!(global_clk = vm.core.global_clk(), "spliced trace sent to splicing tx");
                         } else {
-                            tracing::trace!("trace ended at clk: {}", vm.core.clk());
-                            tracing::trace!("trace ended at pc: {}", vm.core.pc());
-                            tracing::trace!("trace ended at global clk: {}", vm.core.global_clk());
-                            tracing::trace!(
-                                "trace ended with {} mem reads left ",
-                                vm.core.mem_reads.len()
-                            );
+                            tracing::info!(global_clk = vm.core.global_clk(), pc = vm.core.pc(), num_mem_reads_left = vm.core.mem_reads.len(), "trace ended");
                             // Get the end boundary of the shard.
                             let end = ShardBoundary {
                                 timestamp: vm.core.clk(),
@@ -319,14 +310,15 @@ where
                             last_splice.set_last_mem_reads_idx(
                                 start_num_mem_reads as usize - vm.core.mem_reads.len(),
                             );
-
+                            tracing::info!(global_clk = vm.core.global_clk(), "sending last splice to splicing tx");
                             splicing_tx.blocking_send(SendSpliceTask { chunk: last_splice, range })
                                 .map_err(|e| ExecutionError::Other(format!("error sending to splicing tx: {}", e)))?;
-
+                            tracing::info!(global_clk = vm.core.global_clk(), "last splice sent to splicing tx");
                             break;
                         }
                     }
                     CycleResult::Done(true) => {
+                        tracing::info!(global_clk = vm.core.global_clk(), "done cycle result");
                         last_splice.set_last_clk(vm.core.clk());
                         last_splice.set_last_mem_reads_idx(chunk.num_mem_reads() as usize);
 
@@ -345,12 +337,13 @@ where
                         // Get the last state of the vm execution and set the global final vm state to
                         // this value.
                         let final_state = FinalVmState::new(&vm.core);
-                        final_vm_state.set(final_state);
+                        final_vm_state.set(final_state).map_err(|e| ExecutionError::Other(e.to_string()))?;
 
+                        tracing::info!(global_clk = vm.core.global_clk(), "sending last splice to splicing tx");
                         // Send the last splice.
                         splicing_tx.blocking_send(SendSpliceTask { chunk: last_splice, range })
                             .map_err(|e| ExecutionError::Other(format!("error sending to splicing tx: {}", e)))?;
-
+                        tracing::info!(global_clk = vm.core.global_clk(), "last splice sent to splicing tx");
                         break;
                     }
                     CycleResult::Done(false) | CycleResult::TraceEnd => {
@@ -397,7 +390,7 @@ where
                         let task_data_map = task_data_map.clone();
                         async move {
                             while let Some(deferred_message) = deferred_marker_rx.recv().await {
-                                tracing::trace!(
+                                tracing::info!(
                                     "received deferred message with task id {:?}",
                                     deferred_message.task_id
                                 );
@@ -422,6 +415,11 @@ where
                         async move {
                             let mut deferred_accumulator = DeferredEvents::empty();
                             while let Some((task_id, status)) = event_stream.next().await {
+                                tracing::info!(
+                                    task_id = task_id.to_string(),
+                                    "received deferred marker task status: {:?}",
+                                    status
+                                );
                                 if status != TaskStatus::Succeeded {
                                     return Err(ExecutionError::Other(format!(
                                         "deferred marker task failed: {}",
@@ -507,18 +505,27 @@ where
                                     ))
                                 })?;
                             }
+                            tracing::info!("deferred listener task finished");
                             Ok::<_, ExecutionError>(())
                         }
                     }
                     .instrument(inner_span.clone()),
                 );
 
-                join_set.join_all().await.into_iter().collect::<Result<(), ExecutionError>>()?;
+                while let Some(result) = join_set.join_next().await {
+                    result.map_err(|e| {
+                        ExecutionError::Other(format!("deferred listener task panicked: {}", e))
+                    })??;
+                }
                 Ok::<(), ExecutionError>(())
             }
         });
         // Wait for the tasks to finish and collect the errors.
-        join_set.join_all().await.into_iter().collect::<Result<(), ExecutionError>>()?;
+        while let Some(result) = join_set.join_next().await {
+            result.map_err(|e| {
+                ExecutionError::Other(format!("deferred listener task panicked: {}", e))
+            })??;
+        }
 
         Ok(())
     }
```
