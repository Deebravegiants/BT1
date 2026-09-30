# [?] node: fix a potential crash when Firehose provider is faulty (#3129)

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2022-01-06
Source: https://github.com/graphprotocol/graph-node/commit/f8d75a285835fd11c2b2280bedefcc8d95ee43ba
Type: security-commit

## Details
node: fix a potential crash when Firehose provider is faulty (#3129)

When a provider is faulty, it's removed from the list of endpoints for this particular chain. This means later on, places where at least one valid provide must exists panicked, this is the case for the `FirehoseBlockIngestor`.

As well as removing the faulty provider in `connect_firehose_networks`, we also completely remove the chain itself if at the end the chain has 0 providers.

Alternative would be to keep the chain but make downstream users to deal with the fact that providers could be 0. I decided on removing at the source instead since a chain with 0 providers is like no chain at all since nothing could run.

### Renames

I took the opportunity to trimmed down the structs where firehose providers and chain id to providers are stored. I was always finding hard to reason about those struct where there is a lot of repition in the name and the single fields. Hopefully it's a bit better now. I will highlight the bug fix in the diff.

Co-authored-by: Matthieu Vachon <matt@streamingfast.io>

## Patch
### chain/ethereum/src/chain.rs
```diff
@@ -1,7 +1,7 @@
 use anyhow::{Context, Error};
 use graph::blockchain::BlockchainKind;
 use graph::data::subgraph::UnifiedMappingApiVersion;
-use graph::firehose::FirehoseNetworkEndpoints;
+use graph::firehose::FirehoseEndpoints;
 use graph::prelude::{
     EthereumBlock, EthereumCallCache, LightEthereumBlock, LightEthereumBlockExt, StopwatchMetrics,
 };
@@ -70,7 +70,7 @@ pub struct Chain {
     name: String,
     node_id: NodeId,
     registry: Arc<dyn MetricsRegistry>,
-    firehose_endpoints: Arc<FirehoseNetworkEndpoints>,
+    firehose_endpoints: Arc<FirehoseEndpoints>,
     eth_adapters: Arc<EthereumNetworkAdapters>,
     ancestor_count: BlockNumber,
     chain_store: Arc<dyn ChainStore>,
@@ -96,7 +96,7 @@ impl Chain {
         chain_store: Arc<dyn ChainStore>,
         call_cache: Arc<dyn EthereumCallCache>,
         subgraph_store: Arc<dyn SubgraphStore>,
-        firehose_endpoints: FirehoseNetworkEndpoints,
+        firehose_endpoints: FirehoseEndpoints,
         eth_adapters: EthereumNetworkAdapters,
         chain_head_update_listener: Arc<dyn ChainHeadUpdateListener>,
         ancestor_count: BlockNumber,
```

### chain/near/src/chain.rs
```diff
@@ -1,7 +1,7 @@
 use graph::blockchain::BlockchainKind;
 use graph::cheap_clone::CheapClone;
 use graph::data::subgraph::UnifiedMappingApiVersion;
-use graph::firehose::FirehoseNetworkEndpoints;
+use graph::firehose::FirehoseEndpoints;
 use graph::prelude::StopwatchMetrics;
 use graph::{
     anyhow,
@@ -34,7 +34,7 @@ use graph::blockchain::block_stream::BlockStream;
 pub struct Chain {
     logger_factory: LoggerFactory,
     name: String,
-    firehose_endpoints: Arc<FirehoseNetworkEndpoints>,
+    firehose_endpoints: Arc<FirehoseEndpoints>,
     chain_store: Arc<dyn ChainStore>,
 }
 
@@ -49,7 +49,7 @@ impl Chain {
         logger_factory: LoggerFactory,
         name: String,
         chain_store: Arc<dyn ChainStore>,
-        firehose_endpoints: FirehoseNetworkEndpoints,
+        firehose_endpoints: FirehoseEndpoints,
     ) -> Self {
         Chain {
             logger_factory,
```

### graph/src/firehose/endpoints.rs
```diff
@@ -141,45 +141,39 @@ impl FirehoseEndpoint {
         Ok(block_stream)
     }
 }
-
-#[derive(Clone, Debug)]
-pub struct FirehoseNetworkEndpoint {
-    endpoint: Arc<FirehoseEndpoint>,
-}
-
 #[derive(Clone, Debug)]
-pub struct FirehoseNetworkEndpoints {
-    pub endpoints: Vec<FirehoseNetworkEndpoint>,
-}
+pub struct FirehoseEndpoints(Vec<Arc<FirehoseEndpoint>>);
 
-impl FirehoseNetworkEndpoints {
+impl FirehoseEndpoints {
     pub fn new() -> Self {
-        Self { endpoints: vec![] }
+        Self(vec![])
     }
 
     pub fn len(&self) -> usize {
-        self.endpoints.len()
+        self.0.len()
     }
 
     pub fn random(&self) -> Option<&Arc<FirehoseEndpoint>> {
-        if self.endpoints.len() == 0 {
+        if self.0.len() == 0 {
             return None;
         }
 
         // Select from the matching adapters randomly
         let mut rng = rand::thread_rng();
-        Some(&self.endpoints.iter().choose(&mut rng).unwrap().endpoint)
+        Some(&self.0.iter().choose(&mut rng).unwrap())
     }
 
     pub fn remove(&mut self, provider: &str) {
-        self.endpoints
-            .retain(|network_endpoint| network_endpoint.endpoint.provider != provider);
+        self.0
+            .retain(|network_endpoint| network_endpoint.provider != provider);
     }
 }
 
 #[derive(Clone, Debug)]
 pub struct FirehoseNetworks {
-    pub networks: BTreeMap<String, FirehoseNetworkEndpoints>,
+    /// networks contains a map from chain id (`near-mainnet`, `near-testnet`, `solana-mainnet`, etc.)
+    /// to a list of FirehoseEndpoint (type wrapper around `Arc<Vec<FirehoseEndpoint>>`).
+    pub networks: BTreeMap<String, FirehoseEndpoints>,
 }
 
 impl FirehoseNetworks {
@@ -189,32 +183,33 @@ impl FirehoseNetworks {
         }
     }
 
-    pub fn insert(&mut self, name: String, endpoint: Arc<FirehoseEndpoint>) {
-        let network_endpoints = self
+    pub fn insert(&mut self, chain_id: String, endpoint: Arc<FirehoseEndpoint>) {
+        let endpoints = self
             .networks
-            .entry(name)
-            .or_insert(FirehoseNetworkEndpoints { endpoints: vec![] });
-        network_endpoints.endpoints.push(FirehoseNetworkEndpoint {
-            endpoint: endpoint.clone(),
-        });
+            .entry(chain_id)
+            .or_insert(FirehoseEndpoints::new());
+
+        endpoints.0.push(endpoint.clone());
     }
 
-    pub fn remove(&mut self, name: &str, provider: &str) {
-        if let Some(endpoints) = self.networks.get_mut(name) {
+    pub fn remove(&mut self, chain_id: &str, provider: &str) {
+        if let Some(endpoints) = self.networks.get_mut(chain_id) {
             endpoints.remove(provider);
         }
     }
 
+    /// Returns a `Vec` of tuples where the first element of the tuple is
+    /// the chain's id and the second one is an endpoint for this chain.
+    /// There can be mulitple tuple with the same chain id but with different
+    /// endpoint where multiple providers exist for a single chain id.
     pub fn flatten(&self) -> Vec<(String, Arc<FirehoseEndpoint>)> {
         self.networks
             .iter()
-            .flat_map(|(network_name, firehose_endpoints)| {
+            .flat_map(|(chain_id, firehose_endpoints)| {
                 firehose_endpoints
-                    .endpoints
+                    .0
                     .iter()
-                    .map(move |firehose_endpoint| {
-                        (network_name.clone(), firehose_endpoint.endpoint.clone())
-                    })
+                    .map(move |endpoint| (chain_id.clone(), endpoint.clone()))
             })
             .collect()
     }
```

### node/src/chain.rs
```diff
@@ -24,11 +24,11 @@ use std::time::Duration;
 #[derive(PartialEq)]
 enum ProviderNetworkStatus {
     Broken {
-        network: String,
+        chain_id: String,
         provider: String,
     },
     Version {
-        network: String,
+        chain_id: String,
         ident: ChainIdentifier,
     },
 }
@@ -258,7 +258,7 @@ pub async fn connect_ethereum_networks(
                         error!(logger, "Connection to provider failed. Not using this provider";
                                        "error" =>  e.to_string());
                         ProviderNetworkStatus::Broken {
-                            network,
+                            chain_id: network,
                             provider: eth_adapter.provider().to_string(),
                         }
                     }
@@ -269,7 +269,10 @@ pub async fn connect_ethereum_networks(
                             "network_version" => &ident.net_version,
                             "capabilities" => &capabilities
                         );
-                        ProviderNetworkStatus::Version { network, ident }
+                        ProviderNetworkStatus::Version {
+                            chain_id: network,
+                            ident,
+                        }
                     }
                 }
             }),
@@ -282,12 +285,14 @@ pub async fn connect_ethereum_networks(
             .into_iter()
             .fold(HashMap::new(), |mut networks, status| {
                 match status {
-                    ProviderNetworkStatus::Broken { network, provider } => {
-                        eth_networks.remove(&network, &provider)
-                    }
-                    ProviderNetworkStatus::Version { network, ident } => {
-                        networks.entry(network.to_string()).or_default().push(ident)
-                    }
+                    ProviderNetworkStatus::Broken {
+                        chain_id: network,
+                        provider,
+                    } => eth_networks.remove(&network, &provider),
+                    ProviderNetworkStatus::Version {
+                        chain_id: network,
+                        ident,
+                    } => networks.entry(network.to_string()).or_default().push(ident),
                 }
                 networks
             });
@@ -316,11 +321,11 @@ where
         firehose_networks
             .flatten()
             .into_iter()
-            .map(|(network_name, endpoint)| (network_name, endpoint, logger.clone()))
-            .map(|(network, endpoint, logger)| async move {
+            .map(|(chain_id, endpoint)| (chain_id, endpoint, logger.clone()))
+            .map(|(chain_id, endpoint, logger)| async move {
                 let logger = logger.new(o!("provider" => endpoint.provider.to_string()));
                 info!(
-                    logger, "Connecting to Firehose to get network identifier";
+                    logger, "Connecting to Firehose to get chain identifier";
                     "url" => &endpoint.uri,
                 );
                 match tokio::time::timeout(
@@ -336,7 +341,7 @@ where
                         error!(logger, "Connection to provider failed. Not using this provider";
                                        "error" =>  e.to_string());
                         ProviderNetworkStatus::Broken {
-                            network,
+                            chain_id,
                             provider: endpoint.provider.to_string(),
                         }
                     }
@@ -353,28 +358,42 @@ where
                             genesis_block_hash: ptr.hash,
                         };
 
-                        ProviderNetworkStatus::Version { network, ident }
+                        ProviderNetworkStatus::Version { chain_id, ident }
                     }
                 }
             }),
     )
     .await;
 
-    // Group identifiers by network name
+    // Group identifiers by chain id
     let idents: HashMap<String, Vec<ChainIdentifier>> =
         statuses
             .into_iter()
             .fold(HashMap::new(), |mut networks, status| {
                 match status {
-                    ProviderNetworkStatus::Broken { network, provider } => {
-                        firehose_networks.remove(&network, &provider)
-                    }
-                    ProviderNetworkStatus::Version { network, ident } => {
-                        networks.entry(network.to_string()).or_default().push(ident)
+                    ProviderNetworkStatus::Broken { chain_id, provider } => {
+                        firehose_networks.remove(&chain_id, &provider)
                     }
+                    ProviderNetworkStatus::Version { chain_id, ident } => networks
+                        .entry(chain_id.to_string())
+                        .or_default()
+                        .push(ident),
                 }
                 networks
             });
+
+    // Clean-up chains with 0 provider
+    firehose_networks.networks.retain(|chain_id, endpoints| {
+        if endpoints.len() == 0 {
+            error!(
+                logger,
+                "No non-broken providers available for chain {}; ignoring this chain", chain_id
+            );
+        }
+
+        endpoints.len() > 0
+    });
+
     let idents: Vec<_> = idents.into_iter().collect();
     (firehose_networks, idents)
 }
```

### node/src/main.rs
```diff
@@ -5,7 +5,7 @@ use graph::blockchain::firehose_block_ingestor::FirehoseBlockIngestor;
 use graph::blockchain::{Block as BlockchainBlock, Blockchain, BlockchainKind, BlockchainMap};
 use graph::components::store::BlockStore;
 use graph::data::graphql::effort::LoadManager;
-use graph::firehose::{FirehoseNetworkEndpoints, FirehoseNetworks};
+use graph::firehose::{FirehoseEndpoints, FirehoseNetworks};
 use graph::log::logger;
 use graph::prelude::{IndexNodeServer as _, JsonRpcServer as _, *};
 use graph::prometheus::Registry;
@@ -476,7 +476,7 @@ fn ethereum_networks_as_chains(
                 chain_store.cheap_clone(),
                 chain_store,
                 store.subgraph_store(),
-                firehose_endpoints.map_or_else(|| FirehoseNetworkEndpoints::new(), |v| v.clone()),
+                firehose_endpoints.map_or_else(|| FirehoseEndpoints::new(), |v| v.clone()),
                 eth_adapters.clone(),
                 chain_head_update_listener.clone(),
                 *ANCESTOR_COUNT,
@@ -505,38 +505,38 @@ fn near_networks_as_chains(
     let chains: Vec<_> = firehose_networks
         .networks
         .iter()
-        .filter_map(|(network_name, firehose_endpoints)| {
+        .filter_map(|(chain_id, endpoints)| {
             store
                 .block_store()
-                .chain_store(network_name)
-                .map(|chain_store| (network_name, chain_store, firehose_endpoints))
+                .chain_store(chain_id)
+                .map(|chain_store| (chain_id, chain_store, endpoints))
                 .or_else(|| {
                     error!(
                         logger,
-                        "No store configured for NEAR chain {}; ignoring this chain", network_name
+                        "No store configured for NEAR chain {}; ignoring this chain", chain_id
                     );
                     None
                 })
         })
-        .map(|(network_name, chain_store, firehose_endpoints)| {
+        .map(|(chain_id, chain_store, endpoints)| {
             (
-                network_name.clone(),
+                chain_id.clone(),
                 FirehoseChain {
                     chain: Arc::new(near::Chain::new(
                         logger_factory.clone(),
-                        network_name.clone(),
+                        chain_id.clone(),
                         chain_store,
-                        firehose_endpoints.clone(),
+                        endpoints.clone(),
                     )),
-                    firehose_endpoints: firehose_endpoints.clone(),
+                    firehose_endpoints: endpoints.clone(),
                 },
             )
         })
         .collect();
 
-    for (network_name, firehose_chain) in chains.iter() {
+    for (chain_id, firehose_chain) in chains.iter() {
         blockchain_map
-            .insert::<graph_chain_near::Chain>(network_name.clone(), firehose_chain.chain.clone())
+            .insert::<graph_chain_near::Chain>(chain_id.clone(), firehose_chain.chain.clone())
     }
 
     HashMap::from_iter(chains)
@@ -594,7 +594,7 @@ fn start_block_ingestor(
 #[derive(Clone)]
 struct FirehoseChain<C: Blockchain> {
     chain: Arc<C>,
-    firehose_endpoints: FirehoseNetworkEndpoints,
+    firehose_endpoints: FirehoseEndpoints,
 }
 
 fn start_firehose_block_ingestor<C, M>(
```
