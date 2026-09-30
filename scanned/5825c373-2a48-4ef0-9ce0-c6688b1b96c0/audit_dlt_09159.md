# [?] fix: Fix panic on first startup when mixing firehose and rpc (#4680)

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2023-06-07
Source: https://github.com/graphprotocol/graph-node/commit/01f36a13a249f5e78967bf5c335c0b08614d2e63
Type: security-commit

## Details
fix: Fix panic on first startup when mixing firehose and rpc (#4680)

## Patch
### graph/src/blockchain/types.rs
```diff
@@ -280,3 +280,13 @@ pub struct ChainIdentifier {
     pub net_version: String,
     pub genesis_block_hash: BlockHash,
 }
+
+impl fmt::Display for ChainIdentifier {
+    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
+        write!(
+            f,
+            "net_version: {}, genesis_block_hash: {}",
+            self.net_version, self.genesis_block_hash
+        )
+    }
+}
```

### node/src/bin/manager.rs
```diff
@@ -31,6 +31,7 @@ use graph_store_postgres::{
     SubscriptionManager, PRIMARY_SHARD,
 };
 use lazy_static::lazy_static;
+use std::collections::BTreeMap;
 use std::{collections::HashMap, env, num::ParseIntError, sync::Arc, time::Duration};
 const VERSION_LABEL_KEY: &str = "version";
 
@@ -892,7 +893,7 @@ impl Context {
             pools.clone(),
             subgraph_store,
             HashMap::default(),
-            vec![],
+            BTreeMap::new(),
             self.registry,
         );
 
```

### node/src/chain.rs
```diff
@@ -14,7 +14,7 @@ use graph::slog::{debug, error, info, o, Logger};
 use graph::url::Url;
 use graph::util::security::SafeDisplay;
 use graph_chain_ethereum::{self as ethereum, EthereumAdapterTrait, Transport};
-use std::collections::{BTreeMap, HashMap};
+use std::collections::{btree_map, BTreeMap};
 use std::sync::Arc;
 use std::time::Duration;
 
@@ -220,7 +220,7 @@ pub fn create_firehose_networks(
 pub async fn connect_ethereum_networks(
     logger: &Logger,
     mut eth_networks: EthereumNetworks,
-) -> (EthereumNetworks, Vec<(String, Vec<ChainIdentifier>)>) {
+) -> Result<(EthereumNetworks, BTreeMap<String, ChainIdentifier>), anyhow::Error> {
     // This has one entry for each provider, and therefore multiple entries
     // for each network
     let statuses = join_all(
@@ -268,10 +268,10 @@ pub async fn connect_ethereum_networks(
     .await;
 
     // Group identifiers by network name
-    let idents: HashMap<String, Vec<ChainIdentifier>> =
+    let idents: BTreeMap<String, ChainIdentifier> =
         statuses
             .into_iter()
-            .fold(HashMap::new(), |mut networks, status| {
+            .try_fold(BTreeMap::new(), |mut networks, status| {
                 match status {
                     ProviderNetworkStatus::Broken {
                         chain_id: network,
@@ -280,12 +280,25 @@ pub async fn connect_ethereum_networks(
                     ProviderNetworkStatus::Version {
                         chain_id: network,
                         ident,
-                    } => networks.entry(network).or_default().push(ident),
+                    } => match networks.entry(network.clone()) {
+                        btree_map::Entry::Vacant(entry) => {
+                            entry.insert(ident);
+                        }
+                        btree_map::Entry::Occupied(entry) => {
+                            if &ident != entry.get() {
+                                return Err(anyhow!(
+                                    "conflicting network identifiers for chain {}: `{}` != `{}`",
+                                    network,
+                                    ident,
+                                    entry.get()
+                                ));
+                            }
+                        }
+                    },
                 }
-                networks
-            });
-    let idents: Vec<_> = idents.into_iter().collect();
-    (eth_networks, idents)
+                Ok(networks)
+            })?;
+    Ok((eth_networks, idents))
 }
 
 /// Try to connect to all the providers in `firehose_networks` and get their net
@@ -299,7 +312,7 @@ pub async fn connect_ethereum_networks(
 pub async fn connect_firehose_networks<M>(
     logger: &Logger,
     mut firehose_networks: FirehoseNetworks,
-) -> (FirehoseNetworks, Vec<(String, Vec<ChainIdentifier>)>)
+) -> Result<(FirehoseNetworks, BTreeMap<String, ChainIdentifier>), Error>
 where
     M: prost::Message + BlockchainBlock + Default + 'static,
 {
@@ -341,6 +354,8 @@ where
                             "genesis_block" => format_args!("{}", &ptr),
                         );
 
+                        // BUG: Firehose doesn't provide the net_version.
+                        // See also: firehose-no-net-version
                         let ident = ChainIdentifier {
                             net_version: "0".to_string(),
                             genesis_block_hash: ptr.hash,
@@ -354,20 +369,34 @@ where
     .await;
 
     // Group identifiers by chain id
-    let idents: HashMap<String, Vec<ChainIdentifier>> =
+    let idents: BTreeMap<String, ChainIdentifier> =
         statuses
             .into_iter()
-            .fold(HashMap::new(), |mut networks, status| {
+            .try_fold(BTreeMap::new(), |mut networks, status| {
                 match status {
                     ProviderNetworkStatus::Broken { chain_id, provider } => {
                         firehose_networks.remove(&chain_id, &provider)
                     }
                     ProviderNetworkStatus::Version { chain_id, ident } => {
-                        networks.entry(chain_id).or_default().push(ident)
+                        match networks.entry(chain_id.clone()) {
+                            btree_map::Entry::Vacant(entry) => {
+                                entry.insert(ident);
+                            }
+                            btree_map::Entry::Occupied(entry) => {
+                                if &ident != entry.get() {
+                                    return Err(anyhow!(
+                                    "conflicting network identifiers for chain {}: `{}` != `{}`",
+                                    chain_id,
+                                    ident,
+                                    entry.get()
+                                ));
+                                }
+                            }
+                        }
                     }
                 }
-                networks
-            });
+                Ok(networks)
+            })?;
 
     // Clean-up chains with 0 provider
     firehose_networks.networks.retain(|chain_id, endpoints| {
@@ -381,8 +410,7 @@ where
         endpoints.len() > 0
     });
 
-    let idents: Vec<_> = idents.into_iter().collect();
-    (firehose_networks, idents)
+    Ok((firehose_networks, idents))
 }
 
 /// Parses all Ethereum connection strings and returns their network names and
```

### node/src/main.rs
```diff
@@ -305,17 +305,22 @@ async fn main() {
         // `blockchain_map`.
         let mut blockchain_map = BlockchainMap::new();
 
+        // Unwraps: `connect_ethereum_networks` and `connect_firehose_networks` only fail if
+        // mismatching chain identifiers are returned for a same network, which indicates a serious
+        // inconsistency between providers.
         let (arweave_networks, arweave_idents) = connect_firehose_networks::<ArweaveBlock>(
             &logger,
             firehose_networks_by_kind
                 .remove(&BlockchainKind::Arweave)
                 .unwrap_or_else(FirehoseNetworks::new),
         )
-        .await;
+        .await
+        .unwrap();
 
         // This only has idents for chains with rpc adapters.
-        let (eth_networks, ethereum_idents) =
-            connect_ethereum_networks(&logger, eth_networks).await;
+        let (eth_networks, ethereum_idents) = connect_ethereum_networks(&logger, eth_networks)
+            .await
+            .unwrap();
 
         let (eth_firehose_only_networks, eth_firehose_only_idents) =
             connect_firehose_networks::<HeaderOnlyBlock>(
@@ -324,7 +329,8 @@ async fn main() {
                     .remove(&BlockchainKind::Ethereum)
                     .unwrap_or_else(FirehoseNetworks::new),
             )
-            .await;
+            .await
+            .unwrap();
 
         let (near_networks, near_idents) =
             connect_firehose_networks::<NearFirehoseHeaderOnlyBlock>(
@@ -333,23 +339,27 @@ async fn main() {
                     .remove(&BlockchainKind::Near)
                     .unwrap_or_else(FirehoseNetworks::new),
             )
-            .await;
+            .await
+            .unwrap();
 
         let (cosmos_networks, cosmos_idents) = connect_firehose_networks::<CosmosFirehoseBlock>(
             &logger,
             firehose_networks_by_kind
                 .remove(&BlockchainKind::Cosmos)
                 .unwrap_or_else(FirehoseNetworks::new),
         )
-        .await;
-
-        let network_identifiers = ethereum_idents
-            .into_iter()
-            .chain(eth_firehose_only_idents)
-            .chain(arweave_idents)
-            .chain(near_idents)
-            .chain(cosmos_idents)
-            .collect();
+        .await
+        .unwrap();
+
+        // Note that both `eth_firehose_only_idents` and `ethereum_idents` contain Ethereum
+        // networks. If the same network is configured in both RPC and Firehose, the RPC ident takes
+        // precedence. This is necessary because Firehose endpoints currently have no `net_version`.
+        // See also: firehose-no-net-version.
+        let mut network_identifiers = eth_firehose_only_idents;
+        network_identifiers.extend(ethereum_idents);
+        network_identifiers.extend(arweave_idents);
+        network_identifiers.extend(near_idents);
+        network_identifiers.extend(cosmos_idents);
 
         let network_store = store_builder.network_store(network_identifiers);
 
```

### node/src/manager/commands/run.rs
```diff
@@ -111,7 +111,7 @@ pub async fn run(
 
     let eth_adapters2 = eth_adapters.clone();
 
-    let (_, ethereum_idents) = connect_ethereum_networks(&logger, eth_networks).await;
+    let (_, ethereum_idents) = connect_ethereum_networks(&logger, eth_networks).await?;
     // let (near_networks, near_idents) = connect_firehose_networks::<NearFirehoseHeaderOnlyBlock>(
     //     &logger,
     //     firehose_networks_by_kind
```

### node/src/store_builder.rs
```diff
@@ -1,3 +1,4 @@
+use std::collections::BTreeMap;
 use std::iter::FromIterator;
 use std::{collections::HashMap, sync::Arc};
 
@@ -166,7 +167,7 @@ impl StoreBuilder {
         pools: HashMap<ShardName, ConnectionPool>,
         subgraph_store: Arc<SubgraphStore>,
         chains: HashMap<String, ShardName>,
-        networks: Vec<(String, Vec<ChainIdentifier>)>,
+        networks: BTreeMap<String, ChainIdentifier>,
         registry: Arc<MetricsRegistry>,
     ) -> Arc<DieselStore> {
         let networks = networks
@@ -280,7 +281,7 @@ impl StoreBuilder {
 
     /// Return a store that combines both a `Store` for subgraph data
     /// and a `BlockStore` for all chain related data
-    pub fn network_store(self, networks: Vec<(String, Vec<ChainIdentifier>)>) -> Arc<DieselStore> {
+    pub fn network_store(self, networks: BTreeMap<String, ChainIdentifier>) -> Arc<DieselStore> {
         Self::make_store(
             &self.logger,
             self.pools,
```

### store/postgres/src/block_store.rs
```diff
@@ -1,19 +1,15 @@
 use std::{
-    collections::{HashMap, HashSet},
-    iter::FromIterator,
+    collections::HashMap,
     sync::{Arc, RwLock},
     time::Duration,
 };
 
 use graph::{
     blockchain::ChainIdentifier,
     components::store::BlockStore as BlockStoreTrait,
-    prelude::{error, warn, BlockNumber, BlockPtr, Logger, ENV_VARS},
-};
-use graph::{
-    constraint_violation,
-    prelude::{anyhow, CheapClone},
+    prelude::{error, BlockNumber, BlockPtr, Logger, ENV_VARS},
 };
+use graph::{constraint_violation, prelude::CheapClone};
 use graph::{
     prelude::{tokio, StoreError},
     util::timed_cache::TimedCache,
@@ -202,7 +198,7 @@ impl BlockStore {
     pub fn new(
         logger: Logger,
         // (network, ident, shard)
-        chains: Vec<(String, Vec<ChainIdentifier>, Shard)>,
+        chains: Vec<(String, ChainIdentifier, Shard)>,
         // shard -> pool
         pools: HashMap<Shard, ConnectionPool>,
         sender: Arc<NotificationSender>,
@@ -226,30 +222,13 @@ impl BlockStore {
             chain_store_metrics,
         };
 
-        fn reduce_idents(
-            chain_name: &str,
-            idents: Vec<ChainIdentifier>,
-        ) -> Result<Option<ChainIdentifier>, StoreError> {
-            let mut idents: HashSet<ChainIdentifier> = HashSet::from_iter(idents.into_iter());
-            match idents.len() {
-                0 => Ok(None),
-                1 => Ok(idents.drain().next()),
-                _ => Err(anyhow!(
-                    "conflicting network identifiers for chain {}: {:?}",
-                    chain_name,
-                    idents
-                )
-                .into()),
-            }
-        }
-
         /// Check that the configuration for `chain` hasn't changed so that
         /// it is ok to ingest from it
         fn chain_ingestible(
             logger: &Logger,
             chain: &primary::Chain,
             shard: &Shard,
-            ident: &Option<ChainIdentifier>,
+            ident: &ChainIdentifier,
         ) -> bool {
             if &chain.shard != shard {
                 error!(
@@ -261,53 +240,42 @@ impl BlockStore {
                 );
                 return false;
             }
-            match ident {
-                Some(ident) => {
-                    if chain.net_version != ident.net_version {
-                        error!(logger,
+            if chain.net_version != ident.net_version {
+                error!(logger,
                         "the net version for chain {} has changed from {} to {} since the last time we ran",
                         chain.name,
                         chain.net_version,
                         ident.net_version
                     );
-                        return false;
-                    }
-                    if chain.genesis_block != ident.genesis_block_hash.hash_hex() {
-                        error!(logger,
+                return false;
+            }
+            if chain.genesis_block != ident.genesis_block_hash.hash_hex() {
+                error!(logger,
                         "the genesis block hash for chain {} has changed from {} to {} since the last time we ran",
                         chain.name,
                         chain.genesis_block,
                         ident.genesis_block_hash
                     );
-                        return false;
-                    }
-                    true
-                }
-                None => {
-                    warn!(logger, "Failed to get net version and genesis hash from provider. Assuming it has not changed");
-                    true
-                }
+                return false;
             }
+            true
         }
 
         // For each configured chain, add a chain store
-        for (chain_name, idents, shard) in chains {
-            let ident = reduce_idents(&chain_name, idents)?;
-            match (
-                existing_chains
-                    .iter()
-                    .find(|chain| chain.name == chain_name),
-                ident,
-            ) {
-                (Some(chain), ident) => {
+        for (chain_name, ident, shard) in chains {
+            match existing_chains
+                .iter()
+                .find(|chain| chain.name == chain_name)
+            {
+                Some(chain) => {
                     let status = if chain_ingestible(&block_store.logger, chain, &shard, &ident) {
                         ChainStatus::Ingestible
                     } else {
                         ChainStatus::ReadOnly
                     };
                     block_store.add_chain_store(chain, status, false)?;
                 }
-                (None, Some(ident)) => {
+                None => {
                     let chain = primary::add_chain(
                         block_store.mirror.primary(),
                         &chain_name,
@@ -316,13 +284,6 @@ impl BlockStore {
                     )?;
                     block_store.add_chain_store(&chain, ChainStatus::Ingestible, true)?;
                 }
-                (None, None) => {
-                    error!(
-                        &block_store.logger,
-                        " the chain {} is new but we could not get a network identifier for it",
-                        chain_name
-                    );
-                }
             };
         }
 
```

### store/test-store/src/store.rs
```diff
@@ -562,10 +562,14 @@ fn build_store() -> (Arc<Store>, ConnectionPool, Config, Arc<SubscriptionManager
             };
 
             (
-                builder.network_store(vec![
-                    (NETWORK_NAME.to_string(), vec![ident.clone()]),
-                    (FAKE_NETWORK_SHARED.to_string(), vec![ident]),
-                ]),
+                builder.network_store(
+                    vec![
+                        (NETWORK_NAME.to_string(), ident.clone()),
+                        (FAKE_NETWORK_SHARED.to_string(), ident),
+                    ]
+                    .into_iter()
+                    .collect(),
+                ),
                 primary_pool,
                 config,
                 subscription_manager,
```

### tests/src/fixture/mod.rs
```diff
@@ -299,11 +299,13 @@ pub async fn stores(store_config_path: &str) -> Stores {
     let chain_head_listener = store_builder.chain_head_update_listener();
     let network_identifiers = vec![(
         network_name.clone(),
-        (vec![ChainIdentifier {
+        ChainIdentifier {
             net_version: "".into(),
             genesis_block_hash: test_ptr(0).hash,
-        }]),
-    )];
+        },
+    )]
+    .into_iter()
+    .collect();
     let network_store = store_builder.network_store(network_identifiers);
     let chain_store = network_store
         .block_store()
```
