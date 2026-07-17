### Title
Unauthenticated `X-Near-Pool-Coordinator-Query` Header Accepted from Public Internet Bypasses Scatter-Gather Protocol and Corrupts RPC State-Change Results - (File: `chain/jsonrpc/src/lib.rs`)

### Summary

The `X-Near-Pool-Coordinator-Query` HTTP header is an internal trust signal used between sharded-RPC pool coordinator nodes to prevent forwarding loops. The JSON-RPC server accepts this header from **any external client** on the public-facing port (`0.0.0.0:3030`) without authentication, IP restriction, or any other access control. An unprivileged external user who includes this header causes the node to skip scatter-gather and serve only local shard data, producing a concretely corrupted (incomplete) `changes` / `block_effects` RPC result and forcing `UNAVAILABLE_SHARD` / `UNKNOWN_CHUNK` errors on `query` and `chunk` methods that would otherwise succeed via forwarding.

### Finding Description

In `chain/jsonrpc/src/lib.rs`, the `rpc_handler()` function reads the coordinator header from the incoming HTTP request and unconditionally promotes the request to `RequestSource::Coordinator` if the header is present:

```rust
// chain/jsonrpc/src/lib.rs  lines 2716-2720
let source = if headers.contains_key(SHARDED_RPC_COORDINATOR_HEADER) {
    RequestSource::Coordinator
} else {
    RequestSource::User
};
``` [1](#0-0) 

The header name is the public constant `"X-Near-Pool-Coordinator-Query"`: [2](#0-1) 

There is no IP allowlist, shared secret, HMAC, or any other verification. The server is bound to `0.0.0.0:3030` by default: [3](#0-2) 

`RequestSource::Coordinator` changes the behavior of four method families:

**`block_effects` / `EXPERIMENTAL_changes_in_block`** — `changes_in_block()` skips scatter-gather and serves only local shard data. It also calls `ensure_chunks_applied()`, which returns `SHARD_NOT_APPLIED` if any tracked shard's chunk is not yet applied: [4](#0-3) 

**`changes` / `EXPERIMENTAL_changes`** — `changes_in_block_by_type()` similarly skips scatter-gather and calls `ensure_chunks_applied()` for the target shards: [5](#0-4) 

**`query`** — processed locally without forwarding; returns `UNAVAILABLE_SHARD` if the node does not track the account's shard: [6](#0-5) 

**`chunk`** — served locally; returns `UNKNOWN_CHUNK` if the node does not track the shard: [7](#0-6) 

The `RequestSource` enum and its intended semantics are defined in `chain/jsonrpc/src/sharded_rpc.rs`: [8](#0-7) 

### Impact Explanation

The concrete corrupted RPC result is the `changes` array in `RpcStateChangesInBlockByTypeResponse` / `RpcStateChangesInBlockResponse`. When an external attacker sends the coordinator header to a multi-shard RPC node, the node returns only the state changes for shards it locally tracks, silently omitting changes from all other shards. A client (indexer, explorer, bridge relayer) that trusts this response receives an incomplete set of state changes for the queried block — missing account balance changes, access-key changes, contract-data changes, etc. — for every shard the node does not track.

For `query` and `chunk`, the attacker forces `UNAVAILABLE_SHARD` / `UNKNOWN_CHUNK` errors on requests that would otherwise succeed via the scatter-gather forwarding path, making those methods non-functional for cross-shard queries from the attacker's session.

### Likelihood Explanation

The public RPC port (`0.0.0.0:3030`) is the standard endpoint documented for all NEAR node operators. The header name `X-Near-Pool-Coordinator-Query` is a public constant in the open-source client library. Any external HTTP client can set arbitrary headers. No special knowledge, credentials, or network position is required.

### Recommendation

Restrict acceptance of the `X-Near-Pool-Coordinator-Query` header to requests originating from the configured sharded-RPC pool peers (e.g., by IP allowlist derived from `sharded_rpc.nodes[*].address`) or replace the unauthenticated header with a shared secret / HMAC that pool nodes include and the server verifies before promoting `RequestSource::Coordinator`. Alternatively, expose the coordinator-only endpoint on a separate, non-public listener address (analogous to the `prometheus_addr` split already present in `RpcConfig`). [9](#0-8) 

### Proof of Concept

```bash
# Against any nearcore node with sharded_rpc configured, bound on 0.0.0.0:3030
# Step 1: normal user request — triggers scatter-gather, returns changes from ALL shards
curl -s http://<node>:3030 \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"changes",
       "params":{"block_id":"<block_hash>",
                 "changes_type":"account_changes",
                 "account_ids":["alice.near","zoe.near"]}}'
# → full cross-shard changes array

# Step 2: same request with coordinator header — skips scatter-gather
curl -s http://<node>:3030 \
  -H 'Content-Type: application/json' \
  -H 'X-Near-Pool-Coordinator-Query: 1' \
  -d '{"jsonrpc":"2.0","id":1,"method":"changes",
       "params":{"block_id":"<block_hash>",
                 "changes_type":"account_changes",
                 "account_ids":["alice.near","zoe.near"]}}'
# → either SHARD_NOT_APPLIED error (if chunk not yet applied locally)
#   or partial changes array missing entries for shards this node does not track
```

The test `test_rpc_coordinator_header_bypass` in `test-loop-tests/src/tests/sharded_rpc_reliability.rs` confirms that sending the coordinator header from an external client causes the node to process the request locally and return `UNAVAILABLE_SHARD` instead of forwarding — demonstrating the behavioral divergence is reachable and observable: [10](#0-9)

### Citations

**File:** chain/jsonrpc/src/lib.rs (L167-185)
```rust
pub struct RpcConfig {
    pub addr: tcp::ListenerAddr,
    // If provided, will start an http server exporting only Prometheus metrics on that address.
    pub prometheus_addr: Option<String>,
    pub cors_allowed_origins: Vec<String>,
    pub polling_config: RpcPollingConfig,
    #[serde(default)]
    pub limits_config: RpcLimitsConfig,
    // If true, enable some debug RPC endpoints (like one to get the latest block).
    // We disable it by default, as some of those endpoints might be quite CPU heavy.
    #[serde(default = "default_enable_debug_rpc")]
    pub enable_debug_rpc: bool,
    // For node developers only: if specified, the HTML files used to serve the debug pages will
    // be read from this directory, instead of the contents compiled into the binary. This allows
    // for quick iterative development.
    pub experimental_debug_pages_src_path: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub sharded_rpc: Option<ShardedRpcConfig>,
}
```

**File:** chain/jsonrpc/src/lib.rs (L339-342)
```rust
    match source {
        RequestSource::User => sharded_handler(request).await,
        RequestSource::Coordinator => serialize_response(local_handler(request).await?),
    }
```

**File:** chain/jsonrpc/src/lib.rs (L577-581)
```rust
                let result = match source {
                    RequestSource::User => self.query_sharded(params).await,
                    RequestSource::Coordinator => process_query_response(self.query(params).await),
                };
                (metrics_name.to_string(), result)
```

**File:** chain/jsonrpc/src/lib.rs (L1980-1991)
```rust
        if source == RequestSource::Coordinator {
            let epoch_id = EpochId(block.header.epoch_id);
            let shard_layout =
                self.shard_layout_for_epoch(&epoch_id).map_err(to_state_changes_internal)?;
            let required = self.tracked_shard_uids_at_epoch(&shard_layout, &epoch_id)?;
            self.ensure_chunks_applied(&block_hash, &required).await?;
        }

        let changes = self.view_client_send(GetStateChangesInBlock { block_hash }).await?;

        Ok(RpcStateChangesInBlockByTypeResponse { block_hash: block.header.hash, changes })
    }
```

**File:** chain/jsonrpc/src/lib.rs (L2003-2015)
```rust
        if source == RequestSource::Coordinator {
            let epoch_id = EpochId(block.header.epoch_id);
            let shard_layout =
                self.shard_layout_for_epoch(&epoch_id).map_err(to_state_changes_internal)?;
            let required: Vec<ShardUId> =
                extract_target_shards(&request.state_changes_request, &shard_layout)
                    .into_iter()
                    .map(|shard_id| ShardUId::from_shard_id_and_layout(shard_id, &shard_layout))
                    .collect();
            if !required.is_empty() {
                self.ensure_chunks_applied(&block_hash, &required).await?;
            }
        }
```

**File:** chain/jsonrpc/src/lib.rs (L2716-2720)
```rust
    let source = if headers.contains_key(SHARDED_RPC_COORDINATOR_HEADER) {
        RequestSource::Coordinator
    } else {
        RequestSource::User
    };
```

**File:** chain/jsonrpc/client/src/lib.rs (L44-45)
```rust
/// This HTTP header indicates that a jsonrpc query is coming from the coordinator.
pub const SHARDED_RPC_COORDINATOR_HEADER: &'static str = "X-Near-Pool-Coordinator-Query";
```

**File:** nearcore/res/example-config-gc.json (L6-8)
```json
    "rpc": {
        "addr": "0.0.0.0:3030",
        "cors_allowed_origins": [
```

**File:** chain/jsonrpc/src/sharded_rpc.rs (L17-25)
```rust
/// Indicates the origin of a jsonrpc request.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RequestSource {
    /// The request came directly from a user.
    User,
    /// The request was internally forwarded by a pool coordinator.
    /// Indicated by the `X-Near-Pool-Coordinator-Query` HTTP header.
    Coordinator,
}
```

**File:** test-loop-tests/src/tests/sharded_rpc_reliability.rs (L54-103)
```rust
#[test]
fn test_rpc_coordinator_header_bypass() {
    init_test_logger();
    let mut h = TwoShardHarness::new();

    let alice = h.alice.clone();
    let zoe_node = h.zoe_node.clone();

    // First, verify the baseline: a normal (non-coordinator) request for alice's
    // account from zoe's node succeeds because it gets forwarded to alice's node.
    let normal_result = h.env.runner_for_account(&zoe_node).run_jsonrpc_query(
        RpcQueryRequest {
            block_reference: BlockReference::Finality(Finality::None),
            request: QueryRequest::ViewAccount { account_id: alice.clone() },
        },
        Duration::seconds(5),
    );
    assert!(normal_result.is_ok(), "baseline cross-shard query should succeed via forwarding");

    // Now send the SAME query with the coordinator header. Zoe's node doesn't
    // track alice's shard, so without forwarding it must fail with UnavailableShard.
    let request = Message::request(
        "query".to_string(),
        serde_json::to_value(RpcQueryRequest {
            block_reference: BlockReference::Finality(Finality::None),
            request: QueryRequest::ViewAccount { account_id: alice },
        })
        .unwrap(),
    );

    let response = h
        .env
        .runner_for_account(&zoe_node)
        .run_with_jsonrpc_client(
            |client| client.transport.send_jsonrpc_request(request, true),
            Duration::seconds(5),
        )
        .unwrap();

    // The coordinator-flagged request was processed locally on zoe's node.
    // Since zoe's node doesn't track alice's shard, it must return UnavailableShard.
    match response {
        Message::Response(resp) => {
            let err =
                resp.result.expect_err("coordinator request should fail locally (no forwarding)");
            assert_rpc_error(&err, "UNAVAILABLE_SHARD");
        }
        other => panic!("expected Response, got: {other:?}"),
    }
}
```
