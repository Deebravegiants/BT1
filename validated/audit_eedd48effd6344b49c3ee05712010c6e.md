### Title
`state_size_limit` account-storage gate is bypassable via paginated `view_state` requests, enabling unbounded read amplification - (File: runtime/runtime/src/state_viewer/mod.rs)

### Summary
`TrieViewer::view_state` only enforces the `state_size_limit` gate when `paginated` is `false`; the check is explicitly skipped whenever a caller supplies `limit` or `after_key`. An unprivileged RPC caller can therefore always set `limit=Some(1)` (or any non-`None` `after_key`) to bypass the intended per-account storage cap and crawl an entire account's state via a scripted sequence of single-item paginated calls, with no aggregate cap across pages.

### Finding Description
In `TrieViewer::view_state` [1](#0-0) , `paginated` is computed as `limit.is_some() || after_key.is_some()` [2](#0-1) , and the `state_size_limit` check comparing `account.storage_usage() - code_len` against the configured limit is guarded by `if !paginated` [3](#0-2) . This means any request that sets `limit` (even `Some(1)`) or provides `after_key` skips the gate entirely, regardless of how large the account's storage actually is.

Once past the gate, the only remaining limits are per-page caps (`MAX_VIEW_STATE_PAGE_ITEMS = 10_000`, `MAX_VIEW_STATE_PAGE_BYTES = 50_000`) [4](#0-3) , which bound a single page but impose no aggregate/session-wide cap. An attacker can repeatedly call `view_state` with `after_key` set to the previously returned `last_key`, paging through the account's entire trie state indefinitely, effectively reconstructing the full storage that the `state_size_limit` config was meant to keep un-viewable in one shot.

### Impact Explanation
This falls under "node panic or unbounded resource use": an operator who deliberately configures `state_size_limit` to protect RPC nodes from expensive full-state reads on accounts with very large storage can have that protection completely negated by trivial pagination, allowing unbounded read amplification (disk iteration cost across the whole account trie) against public RPC nodes, one cheap request at a time.

### Likelihood Explanation
Highly likely/trivial to exploit: requires only that `state_size_limit` is configured (`Some(limit)`) and a target account whose storage exceeds it — both realistic in production RPC deployments. No special privileges, keys, or protocol version gating are needed; `view_state` is a public, unauthenticated view/query RPC endpoint. The attack is a simple scripted loop of paginated queries.

### Recommendation
Do not skip the `state_size_limit` check for paginated requests. Instead, always validate the account's `storage_usage()` (minus code length) against `state_size_limit` regardless of `paginated`, independent of the per-page item/byte caps, so pagination only affects how a permitted amount of state is chunked into responses rather than whether the account is viewable at all. If pagination of large accounts must be supported for legitimate operational reasons, introduce a separate, explicitly larger paginated-only limit rather than removing the check entirely.

### Proof of Concept
Integration test outline:
1. Set up a node/runtime with `state_size_limit = Some(N)` where `N` is small.
2. Create an account whose contract storage (`storage_usage() - code_len`) exceeds `N` (e.g., write many key/value pairs via contract calls).
3. Call `TrieViewer::view_state(account_id, prefix=[], after_key=None, limit=None, include_proof=false)` and assert it returns `Err(ViewStateError::AccountStateTooLarge { .. })`.
4. Call `view_state(account_id, prefix=[], after_key=None, limit=Some(NonZeroU32::new(1).unwrap()), include_proof=false)` and assert it succeeds (no `AccountStateTooLarge` error), returning one item and a `last_key`.
5. Loop: repeatedly call `view_state` with `after_key = last_key` and `limit = Some(1)` until `last_key` is `None`, accumulating all returned `StateItem`s.
6. Assert the total number/bytes of accumulated items equals the full account storage content (i.e., the entire state that the non-paginated call was blocked from returning), demonstrating the gate provides no real protection under pagination.

### Citations

**File:** runtime/runtime/src/state_viewer/mod.rs (L224-264)
```rust
    pub fn view_state(
        &self,
        state_update: &TrieUpdate,
        account_id: &AccountId,
        prefix: &[u8],
        after_key: Option<&[u8]>,
        limit: Option<NonZeroU32>,
        include_proof: bool,
    ) -> Result<ViewStateResult, errors::ViewStateError> {
        let paginated = limit.is_some() || after_key.is_some();
        if paginated && include_proof {
            return Err(errors::ViewStateError::ProofUnsupportedWithPagination);
        }
        if let Some(after_key) = after_key {
            if !after_key.starts_with(prefix) {
                return Err(errors::ViewStateError::AfterKeyOutsidePrefix);
            }
        }

        let Some(account) = get_account(state_update, account_id)? else {
            return Err(errors::ViewStateError::AccountDoesNotExist {
                requested_account_id: account_id.clone(),
            });
        };

        // Legacy per-account gate — paginated callers opt out of it.
        if !paginated {
            let code_len = state_update
                .get_code_len(
                    account_id.clone(),
                    account.local_contract_hash().unwrap_or_default(),
                )?
                .unwrap_or_default() as u64;
            if let Some(limit) = self.state_size_limit {
                if account.storage_usage().saturating_sub(code_len) > limit {
                    return Err(errors::ViewStateError::AccountStateTooLarge {
                        requested_account_id: account_id.clone(),
                    });
                }
            }
        }
```

**File:** runtime/runtime/src/state_viewer/mod.rs (L280-317)
```rust
        // Per-page caps, separate from the `trie_viewer_state_size_limit` that pagination skips.
        // The byte cap is soft: it's checked before each append, so a page can run one item over.
        const MAX_VIEW_STATE_PAGE_ITEMS: u32 = 10_000;
        const MAX_VIEW_STATE_PAGE_BYTES: u64 = 50_000;

        let (item_cap, byte_cap) = if paginated {
            let items = limit
                .map_or(MAX_VIEW_STATE_PAGE_ITEMS, NonZeroU32::get)
                .min(MAX_VIEW_STATE_PAGE_ITEMS);
            (Some(items), Some(MAX_VIEW_STATE_PAGE_BYTES))
        } else {
            (None, None)
        };

        // Pre-allocate only for an explicit `limit`; the default page size is too big to assume.
        let mut values = match (limit, item_cap) {
            (Some(_), Some(cap)) => Vec::with_capacity(cap as usize),
            _ => Vec::new(),
        };
        let mut used_bytes: u64 = 0;
        let mut last_key = None;

        for item in &mut iter {
            let (key, value) = item?;
            // `seek` (resumed pages) is not prefix-bounded — stop at the account edge.
            if !key.starts_with(&query) {
                break;
            }
            let hit_items = item_cap.is_some_and(|cap| values.len() as u64 >= u64::from(cap));
            let hit_bytes = byte_cap.is_some_and(|cap| used_bytes >= cap);
            if hit_items || hit_bytes {
                // At least one more item exists; resume after the last we kept.
                last_key = values.last().map(|it: &StateItem| it.key.clone());
                break;
            }
            used_bytes += (key.len() + value.len()) as u64;
            values.push(StateItem { key: key[acc_sep_len..].to_vec().into(), value: value.into() });
        }
```
