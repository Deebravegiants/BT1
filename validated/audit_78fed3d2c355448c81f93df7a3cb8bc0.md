Confirmed: only `RequestBodyLimitLayer` (10MB body size) and CORS middleware are applied to the JSON-RPC HTTP endpoint — there is no concurrency limiter or per-client rate limiter on the `/` route itself. Combined with the unbounded `crossbeam_channel::unbounded` queue backing `RpcHandlerActor`, this confirms the attack path is real and unmitigated at both the HTTP layer and the actor-mailbox layer.

### Title
Unbounded resource use via unrate-limited `send_tx`/`broadcast_tx_async` fire-and-forget path into unbounded `RpcHandlerActor` queue - ([File: chain/jsonrpc/src/lib.rs, chain/client/src/rpc_handler.rs, core/async/src/multithread/runtime_handle.rs])

### Summary
`send_tx` with `wait_until: TxExecutionStatus::None` and `broadcast_tx_async` both invoke `send_tx_async()`, which fires a non-blocking `ProcessTxRequest` into `RpcHandlerActor` via a `crossbeam_channel::unbounded` mailbox with no caller-side backpressure. An unprivileged client can submit an unbounded stream of syntactically-valid-but-state-invalid transactions faster than the fixed-size `handler_threads` pool can perform the trie lookups in `can_verify_and_charge_tx`/`get_signer_and_access_key`, growing the in-memory queue and consuming CPU cycles on doomed validations, with no HTTP-level concurrency or rate limiting to stop it.

### Finding Description
`send_tx()` in [1](#0-0)  short-circuits for `wait_until == TxExecutionStatus::None` by calling `self.send_tx_async(request_data)` and immediately returning, without waiting on any response. `send_tx_async()` itself does a fire-and-forget send: [2](#0-1) . This is the same code path as `broadcast_tx_async`, registered directly in the method dispatcher: [3](#0-2) .

The `ProcessTxRequest` is delivered to `RpcHandlerActor`, a multithreaded actor spawned with `spawn_multithread_actor`, whose underlying mailbox is created with `crossbeam_channel::unbounded::<MultithreadRuntimeMessage<A>>()`: [4](#0-3) . Sending to this channel (`send_message`) never blocks and never fails due to capacity — only a fixed number of `handler_threads` OS threads drain it. Each dequeued message runs `process_tx()` → `process_tx_internal()` → `can_verify_and_charge_tx()`, which performs a trie lookup (`get_signer_and_access_key`) before any balance/nonce check can reject the transaction: [5](#0-4) .

At the HTTP layer, the only middleware applied to the JSON-RPC endpoint is CORS and a 10MB `RequestBodyLimitLayer` — confirmed by the imports and architecture doc: [6](#0-5) [7](#0-6) . There is no request-rate or concurrency limiter guarding `broadcast_tx_async`/`send_tx(wait_until:None)`. The only downstream backpressure is `ShardedTransactionPool::insert_transaction` returning `NoSpaceLeft` — [8](#0-7)  — but that check happens only *after* the expensive `can_verify_and_charge_tx` trie lookup has already run, so it protects pool memory, not CPU/queue growth.

Because attackers only need valid signatures (verified cheaply, before the trie lookup, in `ValidatedTransaction::new`) and can target accounts/shards not already cached, each submitted transaction forces a genuine trie read in `get_signer_and_access_key` on the `RpcHandlerActor` thread pool: [9](#0-8) . A flood of such transactions, submitted faster than `handler_threads` can drain the unbounded queue, causes unbounded growth of `MultithreadRuntimeMessage<RpcHandlerActor>` in memory and sustained CPU consumption on trie lookups for transactions that will ultimately be rejected as invalid.

### Impact Explanation
This matches the "node panic or unbounded resource use" bounty impact class, scoped to RPC-node/validator resource exhaustion (CPU and memory) rather than consensus or fund-safety compromise. An attacker can degrade or potentially crash (via OOM) a public RPC node, or slow down legitimate transaction processing on that node, without needing any elevated privileges — just an account able to sign transactions and network access to the RPC endpoint.

### Likelihood Explanation
Highly feasible and repeatable: the attacker needs only a funded-or-unfunded signer account and a script that repeatedly calls `broadcast_tx_async` (or `send_tx` with `wait_until: None`) with distinct nonces/signer accounts to defeat caching. No rate limiting or concurrency cap exists on this specific HTTP route beyond body size, and the mailbox is explicitly unbounded by design (`crossbeam_channel::unbounded`), so the only natural throttle is the finite number of `handler_threads` competing against an attacker who can generate requests far faster than trie lookups can be resolved.

### Recommendation
Add explicit backpressure/rate limiting to the fire-and-forget transaction submission path: e.g., bound the `RpcHandlerActor` mailbox (or add a semaphore-based admission limit sized to a bounded multiple of `handler_threads`) and reject/drop new `ProcessTxRequest`s once the queue depth exceeds a configurable threshold, returning an RPC error (e.g., HTTP 503/`RpcError`) to the caller instead of silently queuing indefinitely. Additionally consider per-IP/per-account request-rate limiting at the Axum layer for `send_tx`/`broadcast_tx_async`, mirroring the token-bucket `Limit`/rate limiter already used for P2P messages (`chain/network/src/concurrency/rate.rs`).

### Proof of Concept
Integration test plan (in `chain/jsonrpc/jsonrpc-tests/tests/rpc_transactions.rs` style):
1. Start a test RPC node with a small `handler_threads` count (e.g., 1) and a moderate genesis with several funded signer accounts but many transactions using distinct nonexistent/low-balance signer accounts (to force `SignerDoesNotExist`/`NotEnoughBalance` failures only after the trie lookup).
2. Fire N (e.g., 50,000) `broadcast_tx_async` calls back-to-back from an unthrottled client loop, each with a valid signature but targeting distinct new/low-balance accounts across different shards to avoid state caching.
3. Instrument `MultithreadRuntimeHandle<RpcHandlerActor>`'s `InstrumentedQueue` (already exposed via `all_actor_instrumentations_view`) to sample queue depth over time.
4. Assert that queue depth grows unbounded/proportionally to N rather than being capped, and that P99 latency for a concurrently-submitted legitimate `send_tx(wait_until: Included)` request from another account grows substantially during the flood (demonstrating degraded liveness for legitimate users), with no `RpcError`/rejection ever returned by the node for exceeding a queue-depth limit (since none exists).

### Citations

**File:** chain/jsonrpc/src/lib.rs (L117-118)
```rust
use tower_http::cors::CorsLayer;
use tower_http::limit::RequestBodyLimitLayer;
```

**File:** chain/jsonrpc/src/lib.rs (L632-638)
```rust
            "broadcast_tx_async" => {
                process_method_call(request, |params| async {
                    let tx = self.send_tx_async(params).to_string();
                    Result::<_, std::convert::Infallible>::Ok(tx)
                })
                .await
            }
```

**File:** chain/jsonrpc/src/lib.rs (L902-911)
```rust
    fn send_tx_async(&self, request_data: RpcSendTransactionRequest) -> CryptoHash {
        let tx = request_data.signed_transaction;
        let hash = tx.get_hash();
        self.process_tx_sender.send(ProcessTxRequest {
            transaction: tx,
            is_forwarded: false,
            check_only: false, // if we set true here it will not actually send the transaction
        });
        hash
    }
```

**File:** chain/jsonrpc/src/lib.rs (L1133-1148)
```rust
    async fn send_tx(
        &self,
        request_data: near_jsonrpc_primitives::types::transactions::RpcSendTransactionRequest,
    ) -> Result<
        near_jsonrpc_primitives::types::transactions::RpcTransactionResponse,
        near_jsonrpc_primitives::types::transactions::RpcTransactionError,
    > {
        metrics::report_wait_until_metric("send_tx", &request_data.wait_until);

        if request_data.wait_until == TxExecutionStatus::None {
            self.send_tx_async(request_data);
            return Ok(RpcTransactionResponse {
                final_execution_outcome: None,
                final_execution_status: TxExecutionStatus::None,
            });
        }
```

**File:** core/async/src/multithread/runtime_handle.rs (L82-90)
```rust
    let (sender, receiver) = crossbeam_channel::unbounded::<MultithreadRuntimeMessage<A>>();
    let instrumented_queue = InstrumentedQueue::new(actor_name);
    let shared_instrumentation =
        InstrumentedThreadWriterSharedPart::new(actor_name.to_string(), instrumented_queue.clone());
    let handle = MultithreadRuntimeHandle {
        sender,
        cancellation_signal_holder,
        instrumentation: shared_instrumentation,
    };
```

**File:** chain/chain/src/runtime/mod.rs (L770-774)
```rust
        let cost = tx_cost(runtime_config, &tx, gas_price)?;
        let shard_uid = shard_layout
            .account_id_to_shard_uid(validated_tx.to_signed_tx().transaction.signer_id());
        let trie = self.tries.get_trie_for_shard(shard_uid, state_root);
        let (signer, access_key) = get_signer_and_access_key(&trie, &validated_tx)?;
```

**File:** chain/jsonrpc/RPC_ARCHITECTURE.md (L93-95)
```markdown
When `enable_debug_rpc` is true, additional routes under `/debug` and `/debug/api/` are registered.

Middleware: CORS (configurable via `cors_allowed_origins`) and request body size limit (default 10MB).
```

**File:** chain/client/src/rpc_handler.rs (L280-298)
```rust
            if self.is_chunk_producer_for_transaction(&head, signed_tx.transaction.signer_id())? {
                let mut pool = self.tx_pool.lock();
                match pool.insert_transaction(shard_uid, validated_tx) {
                    InsertTransactionResult::Success => {
                        tracing::trace!(target: "client", ?shard_uid, tx_hash = ?signed_tx.get_hash(), "recorded a transaction");
                    }
                    InsertTransactionResult::Duplicate => {
                        tracing::trace!(target: "client", ?shard_uid, tx_hash = ?signed_tx.get_hash(), "duplicate transaction, not forwarding it");
                        return Ok(ProcessTxResponse::ValidTx);
                    }
                    InsertTransactionResult::NoSpaceLeft => {
                        if is_forwarded {
                            tracing::trace!(target: "client", ?shard_uid, tx_hash = ?signed_tx.get_hash(), "transaction pool is full, dropping the transaction");
                        } else {
                            tracing::trace!(target: "client", ?shard_uid, tx_hash = ?signed_tx.get_hash(), "transaction pool is full, trying to forward the transaction");
                        }
                    }
                }
            }
```

**File:** runtime/runtime/src/verifier.rs (L133-158)
```rust
pub fn get_signer_and_access_key(
    state_update: &dyn near_store::TrieAccess,
    validated_tx: &ValidatedTransaction,
) -> Result<(Account, AccessKey), InvalidTxError> {
    let signer_id = validated_tx.signer_id();

    let signer = match get_account(state_update, signer_id)? {
        Some(signer) => signer,
        None => {
            return Err(InvalidTxError::SignerDoesNotExist { signer_id: signer_id.clone() });
        }
    };

    let access_key = match get_access_key(state_update, signer_id, validated_tx.public_key())? {
        Some(access_key) => access_key,
        None => {
            return Err(InvalidTxError::InvalidAccessKeyError(
                InvalidAccessKeyError::AccessKeyNotFound {
                    account_id: signer_id.clone(),
                    public_key: validated_tx.public_key().clone().into(),
                },
            )
            .into());
        }
    };
    Ok((signer, access_key))
```
