## Analysis

The Linux UBI bug is a class of "unbounded retry loop that never removes or otherwise makes progress on the stuck queue entry, because the exit condition can never become true." The closest analog in this codebase is in `BeefyHost::start_consensus`'s mandatory-proof drain loop.

`InMemoryProofBackend::receive_mandatory_proof` only **peeks** the front of the per-counterparty mandatory queue (`q.front()`), it never pops it: [1](#0-0) 

The consumer loop in `host.rs` relies on `delete_message` to advance past the head item. But on the "future handover" branch — when the queued proof's `set_id` is greater than `consensus_state.next_authorities.id` — the code only logs and does `continue`, without calling `delete_message` and without any `sleep`/backoff: [2](#0-1) 

Since the message is never deleted and `consensus_state` is only advanced by the counterparty (external state, not touched by this loop), `receive_mandatory_proof` will keep returning the exact same head-of-queue item, hit the same `set_id != next_authorities.id` branch, and `continue` again — with no `.await` between the peek and the `continue`. This is a genuinely tight busy loop (unlike the sibling submit-failure retry at line 234-247, which at least awaits an RPC call each iteration), and it will spin forever on a single-threaded/limited-worker tokio runtime, starving every other task scheduled on that worker, including delivery of subsequent BEEFY/messages proofs for that counterparty.

For comparison, the newer `admin-relayer/src/task.rs` rewrite of the same mandatory-queue-drain logic explicitly sleeps on every retry path, including the analogous "future handover" case, showing this was recognized as a required fix elsewhere but not applied to `beefy/src/host.rs`: [3](#0-2) 

### Title
Infinite tight loop in BeefyHost mandatory-proof consumer on future-handover set_id, halting BEEFY relaying - (File: tesseract/consensus/beefy/src/host.rs)

### Summary
`BeefyHost::start_consensus`'s inner loop that drains the mandatory (authority-set handover) queue peeks the queue head via `receive_mandatory_proof` without removing it, and on the "future handover" sanity check (`set_id != consensus_state.next_authorities.id` after already ruling out `set_id < next_authorities.id`) it neither deletes the stuck message nor sleeps before retrying.

### Finding Description
`InMemoryProofBackend::receive_mandatory_proof` (and the analogous Redis/on-chain backends) return the front of the queue without dequeuing it — dequeue only happens through an explicit `delete_message` call. In the mandatory-queue loop of `start_consensus`, the branch handling a future authority-set-handover proof (`set_id` ahead of the counterparty's `next_authorities.id`) logs an error and does `continue` with no `delete_message` call and no `tokio::time::sleep`. Because `consensus_state` is only re-queried from the counterparty at the top of each iteration and does not change as a result of this branch executing, the loop will observe the exact same message and the exact same mismatch on every subsequent iteration. With no `.await` point between the queue peek and the `continue`, the task spins in a tight CPU loop indefinitely. [4](#0-3) [1](#0-0) 

This mirrors the root cause of CVE-2023-53481: a worker retries against a queue/table entry whose state was never mutated by the failure path, so the loop's exit condition can never be satisfied, and it spins forever instead of making progress or backing off.

### Impact Explanation
A relayer process running `BeefyHost::start_consensus` for a given counterparty state machine that busy-loops on this branch consumes a worker thread/task slot continuously and never reaches the code path that submits or deletes the mandatory proof, nor the code path below it that drains the `NewMessages` queue for the same counterparty. Practically, this permanently stalls consensus-state (authority-set handover) delivery and, transitively, all subsequent message relaying to that counterparty through this host instance — matching the accepted "route unable to deliver messages" impact category.

### Likelihood Explanation
A future-handover proof (queued `set_id` ahead of the counterparty's on-chain `next_authorities.id`) is a normal, easily reachable race: it occurs whenever the prover enqueues a handover proof for a newer authority-set epoch before the counterparty chain has finished applying an earlier one, or when queue ordering/delivery lag lets a later epoch's proof be inspected first. No signature forgery or privileged access is required to reach this branch — it is a routine timing condition in the consensus pipeline that any relayer instance running this loop will encounter.

### Recommendation
Do not `continue` on the future-handover branch without either (a) sleeping with a backoff before retrying (as `admin-relayer/src/task.rs`'s `RETRY_SLEEP` does for the analogous case) so the loop yields and eventually re-observes updated counterparty state, or (b) breaking out of the inner loop back to the outer `while let Some(item) = notifications.next().await` so the task naturally suspends until a new notification arrives. Also ensure every `continue` in this loop passes through at least one `.await` point so the executor can preempt the task.

### Proof of Concept
1. Configure `BeefyHost` against a counterparty whose `next_authorities.id` is behind the epoch encoded in a mandatory proof already sitting at the head of the backend's mandatory queue for that state machine (e.g., two epoch transitions queued in quick succession while the counterparty is still catching up to the first).
2. Call `start_consensus`; the loop pulls the head proof, queries the counterparty's consensus state, finds `set_id > next_authorities.id`, logs the warning, and hits `continue` at line 231 without deleting the message or sleeping.
3. Observe the task spin: `receive_mandatory_proof` returns the identical `QueueMessage` every iteration (nothing dequeued it), `query_consensus_state` keeps returning the same stale state (nothing advanced it on the counterparty), and the branch is taken again indefinitely — a CPU-bound infinite loop with no yield point, blocking all other work scheduled on that async worker.

### Citations

**File:** tesseract/consensus/beefy/src/backend/memory.rs (L145-158)
```rust
	async fn receive_mandatory_proof(
		&self,
		state_machine: &StateMachine,
	) -> Result<Option<QueueMessage>, anyhow::Error> {
		let queues = self.mandatory_queues.read().await;
		let queue = queues.get(state_machine);

		Ok(queue.and_then(|q| {
			q.front().map(|proof| QueueMessage {
				id: format!("mandatory-{}-{}", state_machine, proof.finalized_height),
				proof: proof.clone(),
			})
		}))
	}
```

**File:** tesseract/consensus/beefy/src/host.rs (L180-232)
```rust
			if *message == StreamMessage::EpochChanged {
				// try to consume all mandatory updates
				loop {
					let item =
						self.backend.receive_mandatory_proof(&counterparty_state_machine).await;

					let QueueMessage { id, proof: ConsensusProof { message, set_id, .. } } =
						match item {
							Ok(Some(message)) => message,
							// no new items in the queue, continue to process messages queue
							Ok(None) => break,
							Err(err) => {
								tracing::error!(
									target: crate::LOG_TARGET, "{counterparty_state_machine} error pulling from mandatory queue: {err:?}"
								);
								// non-fatal error, keep trying
								continue;
							},
						};

					tracing::info!(target: crate::LOG_TARGET, "{counterparty_state_machine} got authority set handover proof for {set_id}");
					let encoded = counterparty
						.query_consensus_state(None, self.config.consensus_state_id)
						.await
						.context("Could not fetch consenus state")?; // somewhat fatal
					let consensus_state = ConsensusState::decode(&mut &encoded[..])
						.expect("Infallible, consensus state was encoded correctly");

					// just some sanity checks
					if set_id < consensus_state.next_authorities.id {
						tracing::error!(
							target: crate::LOG_TARGET, "{counterparty_state_machine} got proof with set_id: {set_id} < next_set_id:{}",
							consensus_state.next_authorities.id
						);
						self.backend
							.delete_message(
								&counterparty_state_machine,
								&id,
								StreamMessage::EpochChanged,
							)
							.await?; // this would be a fatal error
						continue;
					}

					// just some sanity checks
					if set_id != consensus_state.next_authorities.id {
						tracing::error!(
							target: crate::LOG_TARGET, "{counterparty_state_machine} consensus proof with set_id: {set_id} does not match next_set_id: {}",
							consensus_state.next_authorities.id
						);
						// try to pull something else
						continue;
					}
```

**File:** tesseract/consensus/admin-relayer/src/task.rs (L146-156)
```rust
			if set_id != state.next_authorities.id {
				// Future handover — can't apply it yet. Sleep and retry so
				// we pick up the matching proof once the chain catches up.
				log::warn!(
					"[{chain}] future handover set_id={set_id} != expected next={}; sleeping {}s before retry",
					state.next_authorities.id,
					RETRY_SLEEP.as_secs()
				);
				tokio::time::sleep(RETRY_SLEEP).await;
				continue;
			}
```
