## Analysis Result

### Title
Unbounded `account_ids` / `keys` array in `changes` (`EXPERIMENTAL_changes`) RPC state-changes query enables RPC-node DoS via unbounded trie/store scans - (File: `chain/chain/src/store/mod.rs`)

### Summary
The `changes` / `EXPERIMENTAL_changes` JSON-RPC endpoint accepts a `StateChangesRequestView` whose `account_ids` (or `keys`) field is an arbitrary-length array supplied directly by an unauthenticated RPC caller. Unlike the analogous `ViewAccessKeyList` query, which enforces an early, configurable cap (`view_access_keys_limit`) before iterating the trie, the state-changes request path performs no size/limit check on the incoming array before looping over every element and issuing one RocksDB range-scan per entry. This mirrors the reported eth/filters `FilterCriteria.Topics` bug class: an unbounded, attacker-controlled collection is fully processed before any resource limit is applied.

### Finding Description
`get_state_changes` in `chain/chain/src/store/mod.rs` iterates every element of `account_ids` (or `keys`) and performs a `KeyForStateChanges::from_trie_key`/`from_raw_key` lookup plus a RocksDB iterator scan (`find_iter` / `find_exact_iter`) for each one, with no bound on the number of iterations: [1](#0-0) 

The request type carrying these arrays, `StateChangesRequest` (and its RPC-facing counterpart `StateChangesRequestView`), places no limit on vector length: [2](#0-1) 

This is reachable directly from the public JSON-RPC surface via the `changes`/`EXPERIMENTAL_changes` methods, which forward the caller-supplied `RpcStateChangesInBlockByTypeRequest` (containing the unbounded array) straight into `changes_in_block_by_type` / `changes_in_block_by_type_sharded` without any array-size validation — the only pre-check performed is whether the request is *empty*, not whether it is *too large*: [3](#0-2) 

For comparison, the codebase already demonstrates the correct mitigation pattern elsewhere: `view_access_keys` in `runtime/runtime/src/state_viewer/mod.rs` enforces `access_keys_limit` and rejects unpaginated requests exceeding it via `TooManyAccessKeys` before doing unbounded trie iteration: [4](#0-3) [5](#0-4) 

No equivalent cap exists for the `account_ids`/`keys` arrays consumed by `get_state_changes`.

### Impact Explanation
A single unauthenticated RPC request to `changes` (or its deprecated alias `EXPERIMENTAL_changes`) with a very large `account_ids` array (bounded only by the JSON body size limit, default 10MB per `chain/jsonrpc/RPC_ARCHITECTURE.md`) forces the node to perform one RocksDB range-scan per array entry — potentially tens of thousands of scans from one request. This can degrade RPC/view-client responsiveness or exhaust CPU/I/O resources on the node serving the request, a resource-exhaustion/DoS impact on the unprivileged RPC surface, directly analogous to the reported `FilterCriteria.Topics` issue.

### Likelihood Explanation
The endpoint is unauthenticated and reachable by any client able to send a JSON-RPC request to the node's public port; only the overall JSON payload size (10MB default) constrains array length, which still permits a very large number of short account IDs. No transaction, gas payment, or special privilege is required to trigger the loop.

### Recommendation
Enforce an explicit, configurable maximum on the number of `account_ids` / `keys` entries in `StateChangesRequest`/`StateChangesRequestView` at parse/validation time (mirroring the `TooManyAccessKeys` / `view_access_keys_limit` pattern already used for `ViewAccessKeyList`), rejecting oversized requests in `chain/jsonrpc/src/lib.rs::changes_in_block_by_type` (or earlier, at RPC parameter parsing) before any trie/store iteration begins in `chain/chain/src/store/mod.rs::get_state_changes`.

### Proof of Concept
Send a JSON-RPC `changes` request with `changes_type: "account_changes"` and an `account_ids` array containing tens of thousands of syntactically valid account IDs (e.g., `"a0.near"`, `"a1.near"`, ...), staying under the 10MB body limit. Each entry causes a separate `KeyForStateChanges::from_trie_key` construction and RocksDB scan in `get_state_changes`, multiplying per-request I/O/CPU cost linearly with array size with no server-side cap, as shown in [6](#0-5) .

### Citations

**File:** chain/chain/src/store/mod.rs (L686-740)
```rust
        match state_changes_request {
            StateChangesRequest::AccountChanges { account_ids } => {
                let mut changes = StateChanges::new();
                for account_id in account_ids {
                    let data_key = TrieKey::Account { account_id: account_id.clone() };
                    let storage_key = KeyForStateChanges::from_trie_key(block_hash, &data_key);
                    let changes_per_key = storage_key.find_exact_iter(&store);
                    changes.extend(StateChanges::from_account_changes(changes_per_key));
                }
                changes
            }
            StateChangesRequest::SingleAccessKeyChanges { keys } => {
                let mut changes = StateChanges::new();
                for key in keys {
                    let data_key = TrieKey::access_key(key.account_id.clone(), &key.public_key);
                    let storage_key = KeyForStateChanges::from_trie_key(block_hash, &data_key);
                    let changes_per_key = storage_key.find_iter(&store);
                    changes.extend(StateChanges::from_access_key_changes(changes_per_key));
                }
                changes
            }
            StateChangesRequest::AllAccessKeyChanges { account_ids } => {
                let mut changes = StateChanges::new();
                for account_id in account_ids {
                    let data_key = trie_key_parsers::get_raw_prefix_for_access_keys(account_id);
                    let storage_key = KeyForStateChanges::from_raw_key(block_hash, &data_key);
                    let changes_per_key_prefix = storage_key.find_iter(&store);
                    changes.extend(StateChanges::from_access_key_changes(changes_per_key_prefix));
                }
                changes
            }
            StateChangesRequest::ContractCodeChanges { account_ids } => {
                let mut changes = StateChanges::new();
                for account_id in account_ids {
                    let data_key = TrieKey::ContractCode { account_id: account_id.clone() };
                    let storage_key = KeyForStateChanges::from_trie_key(block_hash, &data_key);
                    let changes_per_key = storage_key.find_exact_iter(&store);
                    changes.extend(StateChanges::from_contract_code_changes(changes_per_key));
                }
                changes
            }
            StateChangesRequest::DataChanges { account_ids, key_prefix } => {
                let mut changes = StateChanges::new();
                for account_id in account_ids {
                    let data_key = trie_key_parsers::get_raw_prefix_for_contract_data(
                        account_id,
                        key_prefix.as_ref(),
                    );
                    let storage_key = KeyForStateChanges::from_raw_key(block_hash, &data_key);
                    let changes_per_key_prefix = storage_key.find_iter(&store);
                    changes.extend(StateChanges::from_data_changes(changes_per_key_prefix));
                }
                changes
            }
        }
```

**File:** core/primitives/src/types.rs (L244-251)
```rust
#[derive(Debug)]
pub enum StateChangesRequest {
    AccountChanges { account_ids: Vec<AccountId> },
    SingleAccessKeyChanges { keys: Vec<AccountWithPublicKey> },
    AllAccessKeyChanges { account_ids: Vec<AccountId> },
    ContractCodeChanges { account_ids: Vec<AccountId> },
    DataChanges { account_ids: Vec<AccountId>, key_prefix: StoreKey },
}
```

**File:** chain/jsonrpc/src/lib.rs (L2263-2274)
```rust
        // Short-circuit requests with no target accounts/keys *before* the
        // local view client lookup. Under spice, a non-validator RPC node may
        // see the block header before its chunks are applied, making
        // `GetBlock(BlockId::Height(h))` transiently return `UNKNOWN_BLOCK`.
        // With nothing to fan out there is no reason to resolve the block.
        if state_changes_request_is_empty(&request.state_changes_request) {
            return serialize_response(RpcStateChangesInBlockResponse {
                block_hash: CryptoHash::default(),
                changes: vec![],
            });
        }

```

**File:** runtime/runtime/src/state_viewer/mod.rs (L195-258)
```rust
        let max = self.access_keys_limit;
        let paginated = after.is_some() || limit.is_some();

        let item_cap: Option<u32> = if paginated {
            // An explicit page size larger than the configured maximum is
            // clamped down rather than rejected; with no explicit page size we
            // fall back to the configured maximum.
            Some(limit.map_or(max, |requested| requested.get().min(max)))
        } else {
            None
        };

        let prefix = trie_key_parsers::get_raw_prefix_for_access_keys(account_id);
        // Bound iteration to this account's access-key range with a prune
        // condition. Unlike the per-node seek boundary, a prune condition
        // survives `seek`, so it keeps enforcing the range across the seeks we
        // use below to skip gas-key nonce blocks.
        let prefix_nibbles: Vec<u8> = prefix.iter().flat_map(|&b| [b >> 4, b & 0x0f]).collect();
        let mut iter =
            trie.disk_iter_with_prune_condition(Some(Box::new(move |key_nibbles: &Vec<u8>| {
                !nibbles_within_prefix(&prefix_nibbles, key_nibbles)
            })))?;

        match after {
            Some(handle) => {
                let after_key = TrieKey::access_key(account_id.clone(), handle.clone()).to_vec();
                match prefix_successor(&after_key) {
                    Some(next) => iter.seek(Bound::Included(next.as_slice()))?,
                    // Unreachable: access-key keys start with `col::ACCESS_KEY`,
                    // so they are never all-0xFF.
                    None => iter.seek(Bound::Excluded(after_key.as_slice()))?,
                }
            }
            None => iter.seek(Bound::Included(prefix.as_slice()))?,
        }

        let mut keys = Vec::new();
        let mut last_key = None;

        while let Some(item) = iter.next() {
            let (raw_key, _value) = item?;
            let key_handle =
                parse_key_handle_from_access_key_key(&raw_key, account_id).map_err(|_| {
                    errors::ViewAccessKeyError::InternalError {
                        error_message: "unexpected invalid access key from iterator".to_string(),
                    }
                })?;
            // A genuine access key beyond what we've already kept.
            if let Some(cap) = item_cap {
                if keys.len() as u64 >= u64::from(cap) {
                    // Page is full and at least one more key exists: emit a cursor
                    // at the last kept key so the caller can resume.
                    last_key = keys
                        .last()
                        .map(|(handle, _): &(PublicKeyHandle, AccessKey)| handle.clone());
                    break;
                }
            } else if keys.len() as u64 >= u64::from(max) {
                // Unpaginated request that exceeds the configured limit.
                return Err(errors::ViewAccessKeyError::TooManyAccessKeys {
                    requested_account_id: account_id.clone(),
                    limit: max,
                });
            }
```

**File:** runtime/runtime/src/state_viewer/errors.rs (L25-37)
```rust
#[derive(thiserror::Error, Debug)]
pub enum ViewAccessKeyError {
    #[error("Account ID \"{requested_account_id}\" is invalid")]
    InvalidAccountId { requested_account_id: near_primitives::types::AccountId },
    #[error("Access key for public key #{public_key} does not exist")]
    AccessKeyDoesNotExist { public_key: near_crypto::PublicKey },
    #[error(
        "Account {requested_account_id} has more than {limit} access keys; use a paginated view_access_key_list request"
    )]
    TooManyAccessKeys { requested_account_id: near_primitives::types::AccountId, limit: u32 },
    #[error("Internal error: #{error_message}")]
    InternalError { error_message: String },
}
```
