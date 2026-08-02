No vulnerability found for this question.

The premise misreads how the cache works. The `None` key in `ShardedJmtMerkleDb.version_caches` (a `HashMap<Option<usize>, VersionedNodeCache>`) just selects *which* `VersionedNodeCache` instance to use — the one for the top (non-sharded) levels vs. the ones per shard [1](#0-0) . It is not a per-version key that could be overwritten across versions.

Inside `VersionedNodeCache` itself, entries are stored in a `VecDeque<(Version, Arc<NodeCache>)>`, and `add_version` pushes a new `(version, nodes)` tuple onto the back rather than replacing anything keyed by a shared identifier [2](#0-1) . `add_version` also asserts that the incoming version is strictly greater than the last cached version, which would panic (not silently corrupt) if a stale/out-of-order call arrived [3](#0-2) . Lookups via `get_version` scan for an exact match on `version`, so a lookup for `V` can never return nodes that were stored under `V+1` [4](#0-3) .

In `calculate_top_levels`, the top-level nodes produced by `put_top_levels_nodes(shard_root_nodes, base_version, version)` are added via `self.version_caches.get(&None).unwrap().add_version(version, ...)`, with `version` and the corresponding `tree_update_batch` always paired together as a single call — there's no intermediate shared mutable slot where one call's nodes could be attributed to another call's version [5](#0-4) . The actual node keys embed the version (`NodeKey`), and `get_node_option`/`get_root_hash` resolve strictly through `JellyfishMerkleTree::new(self).get_root_hash(version)`, which reads root nodes keyed to that exact version, not through some hash-map slot that could be raced across versions [6](#0-5) .

Since the cache structurally cannot associate one version's data with another version's key (asserted ordering + exact-match lookup by version, not by a shared `None`/single-slot key), the described interleaving cannot cause `get_root_hash(V)` to return a root mixing shard roots from `V` and `V+1`. This does not cross a custody boundary or affect asset/ownership control even hypothetically, since the mechanism described does not exist in the code.

### Citations

**File:** storage/aptosdb/src/sharded_jmt_merkle_db.rs (L64-83)
```rust
    /// shard_id -> cache. `None` key is the top-levels cache.
    version_caches: HashMap<Option<usize>, VersionedNodeCache>,
    /// `None` means the LRU cache is disabled.
    lru_cache: Option<LruNodeCache>,
    /// Metrics tag for per-tree timer labels (e.g. `"hot"`, `"cold"`, `"position"`).
    db_tag: &'static str,
}

impl ShardedJmtMerkleDb {
    pub(crate) fn new(
        metadata_db: Arc<DB>,
        shards: [Arc<DB>; NUM_STATE_SHARDS],
        max_nodes_per_lru_cache_shard: usize,
        db_tag: &'static str,
    ) -> Self {
        let mut version_caches = HashMap::with_capacity(NUM_STATE_SHARDS + 1);
        version_caches.insert(None, VersionedNodeCache::new());
        for i in 0..NUM_STATE_SHARDS {
            version_caches.insert(Some(i), VersionedNodeCache::new());
        }
```

**File:** storage/aptosdb/src/sharded_jmt_merkle_db.rs (L220-222)
```rust
    pub fn get_root_hash(&self, version: Version) -> Result<HashValue> {
        JellyfishMerkleTree::new(self).get_root_hash(version)
    }
```

**File:** storage/aptosdb/src/sharded_jmt_merkle_db.rs (L418-440)
```rust
    pub fn calculate_top_levels(
        &self,
        shard_root_nodes: Vec<Node>,
        version: Version,
        base_version: Option<Version>,
        previous_epoch_ending_version: Option<Version>,
    ) -> Result<(HashValue, usize, RawBatch)> {
        assert!(shard_root_nodes.len() == 16);

        let (root_hash, leaf_count, tree_update_batch) = JellyfishMerkleTree::new(self)
            .put_top_levels_nodes(shard_root_nodes, base_version, version)?;

        if self.cache_enabled() {
            self.version_caches.get(&None).unwrap().add_version(
                version,
                tree_update_batch
                    .node_batch
                    .iter()
                    .flatten()
                    .cloned()
                    .collect(),
            );
        }
```

**File:** storage/aptosdb/src/versioned_node_cache.rs (L43-57)
```rust
    pub fn add_version(&self, version: Version, nodes: NodeCache) {
        let _timer = OTHER_TIMERS_SECONDS.timer_with(&["version_cache_add"]);

        let mut locked = self.inner.write();
        if !locked.is_empty() {
            let (last_version, _) = locked.back().unwrap();
            assert!(
                *last_version < version,
                "Updating older version. {} vs latest:{} ",
                version,
                *last_version,
            );
        }
        locked.push_back((version, Arc::new(nodes)));
    }
```

**File:** storage/aptosdb/src/versioned_node_cache.rs (L90-97)
```rust
    pub fn get_version(&self, version: Version) -> Option<Arc<NodeCache>> {
        self.inner
            .read()
            .iter()
            .rev()
            .find(|(ver, _nodes)| *ver == version)
            .map(|(_ver, nodes)| nodes.clone())
    }
```
