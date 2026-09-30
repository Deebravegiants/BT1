# [?] [grpc] fix deadlock (#11381)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2023-12-21
Source: https://github.com/aptos-labs/aptos-core/commit/a65c44e35fedd9664246ae0aa5dd37092938ce03
Type: security-commit

## Details
[grpc] fix deadlock (#11381)

* fix deadlock

* fix lint

* remove verify bucket from cache worker

* Cache worker logging (#11373)

* Cache worker logging

* fix the counter.

* fix the counter.

* fix the counter.

* fix worker.

* chain id update in file worker.

* chain id update in file worker.

* Add log

* Cache worker refactor

* Change duration logging to be mutually exclusive

* something exist unexpectly.

* explicit error when stream is ended.

* explicit error when stream is ended.

* explicit error when stream is ended.

* Fix verification check

* fix the error message for grpc.

* Make duration logging mutually exclusive

---------

Co-authored-by: Larry Liu <larry@aptoslabs.com>

* Delete unnecessary upload metadata loop

---------

Co-authored-by: Renee Tso <8248583+rtso@users.noreply.github.com>
Co-authored-by: Larry Liu <larry@aptoslabs.com>

## Patch
### docker/compose/indexer-grpc/docker-compose.yaml
```diff
@@ -75,7 +75,7 @@ services:
       - '--config-path'
       - '/opt/aptos/file-store-config.yaml'
     depends_on:
-      - indexer-grpc-cache-worker
+      - redis
 
   indexer-grpc-data-service:
     image: "${INDEXER_GRPC_IMAGE_REPO:-aptoslabs/indexer-grpc}:${IMAGE_TAG:-main}"
@@ -106,6 +106,7 @@ services:
       - "18084:8084" # health
     depends_on:
       - indexer-grpc-cache-worker
+      - indexer-grpc-file-store
       - redis-replica
 
 # This joins the indexer-grpc compose with the validator-testnet compose using a shared docker network
```

### docker/compose/indexer-grpc/file-store-config.yaml
```diff
@@ -5,3 +5,4 @@ server_config:
   file_store_config:
     file_store_type: LocalFileStore
     local_file_store_path: /opt/aptos/file-store
+  chain_id: 4
\ No newline at end of file
```

### ecosystem/indexer-grpc/indexer-grpc-cache-worker/src/lib.rs
```diff
@@ -43,7 +43,11 @@ impl RunnableConfig for IndexerGrpcCacheWorkerConfig {
         )
         .await
         .context("Failed to create cache worker")?;
-        worker.run().await?;
+        worker
+            .run()
+            .await
+            .context("Failed to run cache worker")
+            .expect("Cache worker failed");
         Ok(())
     }
 
```

### ecosystem/indexer-grpc/indexer-grpc-cache-worker/src/main.rs
```diff
@@ -9,5 +9,8 @@ use clap::Parser;
 #[tokio::main]
 async fn main() -> Result<()> {
     let args = ServerArgs::parse();
-    args.run::<IndexerGrpcCacheWorkerConfig>().await
+    args.run::<IndexerGrpcCacheWorkerConfig>()
+        .await
+        .expect("Cache worker failed to run");
+    Ok(())
 }
```

### ecosystem/indexer-grpc/indexer-grpc-cache-worker/src/worker.rs
```diff
@@ -55,10 +55,7 @@ pub(crate) enum GrpcDataStatus {
     /// Ok status with processed count.
     /// Each batch may contain multiple data chunks(like 1000 transactions).
     /// These data chunks may be out of order.
-    ChunkDataOk {
-        start_version: u64,
-        num_of_transactions: u64,
-    },
+    ChunkDataOk { num_of_transactions: u64 },
     /// Init signal received with start version of current stream.
     /// No two `Init` signals will be sent in the same stream.
     StreamInit(u64),
@@ -124,9 +121,7 @@ impl Worker {
                     LocalFileStoreOperator::new(local_file_store.local_file_store_path.clone()),
                 ),
             };
-            // TODO: this is unnecessary
             // TODO: move chain id check somewhere around here
-            file_store_operator.verify_storage_bucket_existence().await;
             // This ensures that metadata is created before we start the cache worker
             let mut starting_version = file_store_operator.get_latest_version().await;
             while starting_version.is_none() {
@@ -144,7 +139,13 @@ impl Worker {
             // There's a guarantee at this point that starting_version is not null
             let starting_version = starting_version.unwrap();
 
-            let file_store_metadata = file_store_operator.get_file_store_metadata().await;
+            let file_store_metadata = file_store_operator.get_file_store_metadata().await.unwrap();
+
+            tracing::info!(
+                service_type = SERVICE_TYPE,
+                "[Indexer Cache] Starting cache worker with version {}",
+                starting_version
+            );
 
             // 2. Start streaming RPC.
             let request = tonic::Request::new(GetTransactionsFromNodeRequest {
@@ -161,16 +162,25 @@ impl Worker {
                         starting_version
                     )
                 })?;
-
+            info!(
+                service_type = SERVICE_TYPE,
+                "[Indexer Cache] Streaming RPC started."
+            );
             // 3&4. Infinite streaming until error happens. Either stream ends or worker crashes.
             process_streaming_response(conn, file_store_metadata, response.into_inner()).await?;
+
+            info!(
+                service_type = SERVICE_TYPE,
+                "[Indexer Cache] Streaming RPC ended."
+            );
         }
     }
 }
 
 async fn process_transactions_from_node_response(
     response: TransactionsFromNodeResponse,
     cache_operator: &mut CacheOperator<redis::aio::ConnectionManager>,
+    batch_start_time: std::time::Instant,
 ) -> Result<GrpcDataStatus> {
     let size_in_bytes = response.encoded_len();
     match response.response.unwrap() {
@@ -194,7 +204,6 @@ async fn process_transactions_from_node_response(
             }
         },
         Response::Data(data) => {
-            let starting_time = std::time::Instant::now();
             let transaction_len = data.transactions.len();
             let first_transaction = data
                 .transactions
@@ -207,6 +216,22 @@ async fn process_transactions_from_node_response(
             let start_version = first_transaction.version;
             let first_transaction_pb_timestamp = first_transaction.timestamp.clone();
             let last_transaction_pb_timestamp = last_transaction.timestamp.clone();
+
+            log_grpc_step(
+                SERVICE_TYPE,
+                IndexerGrpcStep::CacheWorkerReceivedTxns,
+                Some(start_version as i64),
+                Some(last_transaction.version as i64),
+                first_transaction_pb_timestamp.as_ref(),
+                last_transaction_pb_timestamp.as_ref(),
+                Some(batch_start_time.elapsed().as_secs_f64()),
+                Some(size_in_bytes),
+                Some((last_transaction.version - first_transaction.version + 1) as i64),
+                None,
+            );
+
+            let decode_txns_start_time = std::time::Instant::now();
+
             let transactions = data
                 .transactions
                 .clone()
@@ -224,6 +249,21 @@ async fn process_transactions_from_node_response(
                 })
                 .collect::<Result<Vec<(u64, String, u64)>>>()?;
 
+            log_grpc_step(
+                SERVICE_TYPE,
+                IndexerGrpcStep::CacheWorkerTxnDecoded,
+                Some(start_version as i64),
+                Some(last_transaction.version as i64),
+                first_transaction_pb_timestamp.as_ref(),
+                last_transaction_pb_timestamp.as_ref(),
+                Some(decode_txns_start_time.elapsed().as_secs_f64()),
+                Some(size_in_bytes),
+                Some((last_transaction.version - first_transaction.version + 1) as i64),
+                None,
+            );
+
+            let cache_update_start_time = std::time::Instant::now();
+
             // Push to cache.
             match cache_operator.update_cache_transactions(transactions).await {
                 Ok(_) => {
@@ -234,7 +274,7 @@ async fn process_transactions_from_node_response(
                         Some(last_transaction.version as i64),
                         first_transaction_pb_timestamp.as_ref(),
                         last_transaction_pb_timestamp.as_ref(),
-                        Some(starting_time.elapsed().as_secs_f64()),
+                        Some(cache_update_start_time.elapsed().as_secs_f64()),
                         Some(size_in_bytes),
                         Some((last_transaction.version - first_transaction.version + 1) as i64),
                         None,
@@ -248,22 +288,18 @@ async fn process_transactions_from_node_response(
                 },
             }
             Ok(GrpcDataStatus::ChunkDataOk {
-                start_version,
                 num_of_transactions: transaction_len as u64,
             })
         },
     }
 }
 
 //// Setup the cache operator with init signal, includeing chain id and starting version from fullnode.
-async fn setup_cache_with_init_signal(
-    conn: redis::aio::ConnectionManager,
+async fn verify_fullnode_init_signal(
+    cache_operator: &mut CacheOperator<redis::aio::ConnectionManager>,
     init_signal: TransactionsFromNodeResponse,
-) -> Result<(
-    CacheOperator<redis::aio::ConnectionManager>,
-    ChainID,
-    StartingVersion,
-)> {
+    file_store_metadata: FileStoreMetadata,
+) -> Result<(ChainID, StartingVersion)> {
     let (fullnode_chain_id, starting_version) = match init_signal
         .response
         .expect("[Indexer Cache] Response type does not exist.")
@@ -283,20 +319,27 @@ async fn setup_cache_with_init_signal(
         },
     };
 
-    let mut cache_operator = CacheOperator::new(conn);
-    cache_operator.cache_setup_if_needed().await?;
-    cache_operator
-        .update_or_verify_chain_id(fullnode_chain_id as u64)
-        .await
-        .context("[Indexer Cache] Chain id mismatch between cache and fullnode.")?;
+    // Guaranteed that chain id is here at this point because we already ensure that fileworker did the set up
+    let chain_id = cache_operator.get_chain_id().await?.unwrap();
+    if chain_id != fullnode_chain_id as u64 {
+        bail!("[Indexer Cache] Chain ID mismatch between fullnode init signal and cache.");
+    }
 
-    Ok((cache_operator, fullnode_chain_id, starting_version))
+    // It's required to start the worker with the same version as file store.
+    if file_store_metadata.version != starting_version {
+        bail!("[Indexer Cache] Starting version mismatch between filestore metadata and fullnode init signal.");
+    }
+    if file_store_metadata.chain_id != fullnode_chain_id as u64 {
+        bail!("[Indexer Cache] Chain id mismatch between filestore metadata and fullnode.");
+    }
+
+    Ok((fullnode_chain_id, starting_version))
 }
 
 /// Infinite streaming processing. Retry if error happens; crash if fatal.
 async fn process_streaming_response(
     conn: redis::aio::ConnectionManager,
-    file_store_metadata: Option<FileStoreMetadata>,
+    file_store_metadata: FileStoreMetadata,
     mut resp_stream: impl futures_core::Stream<Item = Result<TransactionsFromNodeResponse, tonic::Status>>
         + std::marker::Unpin,
 ) -> Result<()> {
@@ -309,24 +352,30 @@ async fn process_streaming_response(
             bail!("[Indexer Cache] Streaming error: no response.");
         },
     };
-    let (mut cache_operator, fullnode_chain_id, starting_version) =
-        setup_cache_with_init_signal(conn, init_signal)
+    let mut cache_operator = CacheOperator::new(conn);
+
+    let (fullnode_chain_id, starting_version) =
+        verify_fullnode_init_signal(&mut cache_operator, init_signal, file_store_metadata)
             .await
-            .context("[Indexer Cache] Failed to setup cache")?;
-    // It's required to start the worker with the same version as file store.
-    if let Some(file_store_metadata) = file_store_metadata {
-        if file_store_metadata.version != starting_version {
-            bail!("[Indexer Cache] File store version mismatch with fullnode.");
-        }
-        if file_store_metadata.chain_id != fullnode_chain_id as u64 {
-            bail!("[Indexer Cache] Chain id mismatch between file store and fullnode.");
-        }
-    }
+            .context("[Indexer Cache] Failed to verify init signal")?;
+
     let mut current_version = starting_version;
-    let mut starting_time = std::time::Instant::now();
+    let mut batch_start_time = std::time::Instant::now();
 
     // 4. Process the streaming response.
-    while let Some(received) = resp_stream.next().await {
+    loop {
+        let start_time = std::time::Instant::now();
+        let received = match resp_stream.next().await {
+            Some(r) => r,
+            _ => {
+                error!(
+                    service_type = SERVICE_TYPE,
+                    "[Indexer Cache] Streaming error: no response."
+                );
+                ERROR_COUNT.with_label_values(&["streaming_error"]).inc();
+                break;
+            },
+        };
         let received: TransactionsFromNodeResponse = match received {
             Ok(r) => r,
             Err(err) => {
@@ -345,10 +394,11 @@ async fn process_streaming_response(
 
         let size_in_bytes = received.encoded_len();
 
-        match process_transactions_from_node_response(received, &mut cache_operator).await {
+        match process_transactions_from_node_response(received, &mut cache_operator, start_time)
+            .await
+        {
             Ok(status) => match status {
                 GrpcDataStatus::ChunkDataOk {
-                    start_version,
                     num_of_transactions,
                 } => {
                     current_version += num_of_transactions;
@@ -359,11 +409,6 @@ async fn process_streaming_response(
                     // TODO: Reasses whether this metric useful
                     LATEST_PROCESSED_VERSION_OLD.set(current_version as i64);
                     PROCESSED_BATCH_SIZE.set(num_of_transactions as i64);
-                    info!(
-                        start_version = start_version,
-                        num_of_transactions = num_of_transactions,
-                        "[Indexer Cache] Data chunk received.",
-                    );
                 },
                 GrpcDataStatus::StreamInit(new_version) => {
                     error!(
@@ -406,12 +451,12 @@ async fn process_streaming_response(
                         Some((start_version + num_of_transactions - 1) as i64),
                         None,
                         None,
-                        Some(starting_time.elapsed().as_secs_f64()),
+                        Some(batch_start_time.elapsed().as_secs_f64()),
                         Some(size_in_bytes),
                         Some(num_of_transactions as i64),
                         None,
                     );
-                    starting_time = std::time::Instant::now();
+                    batch_start_time = std::time::Instant::now();
                 },
             },
             Err(e) => {
@@ -431,7 +476,7 @@ async fn process_streaming_response(
         loop {
             let file_store_version = cache_operator
                 .get_file_store_latest_version()
-                .await
+                .await?
                 .unwrap();
             if file_store_version + FILE_STORE_VERSIONS_RESERVED < current_version {
                 tokio::time::sleep(std::time::Duration::from_millis(
```

### ecosystem/indexer-grpc/indexer-grpc-data-service/src/service.rs
```diff
@@ -7,7 +7,7 @@ use crate::metrics::{
     PROCESSED_LATENCY_IN_SECS, PROCESSED_LATENCY_IN_SECS_ALL, PROCESSED_VERSIONS_COUNT,
     SHORT_CONNECTION_COUNT,
 };
-use anyhow::Context;
+use anyhow::{Context, Result};
 use aptos_indexer_grpc_utils::{
     build_protobuf_encoded_transaction_wrappers,
     cache_operator::{CacheBatchGetStatus, CacheOperator},
@@ -50,6 +50,9 @@ const AHEAD_OF_CACHE_RETRY_SLEEP_DURATION_MS: u64 = 50;
 // When error happens when fetching data from cache and file store, the server will retry after this duration.
 // TODO(larry): fix all errors treated as transient errors.
 const TRANSIENT_DATA_ERROR_RETRY_SLEEP_DURATION_MS: u64 = 1000;
+// This is the time we wait for the file store to be ready. It should only be
+// kicked off when there's no metadata in the file store.
+const FILE_STORE_METADATA_WAIT_MS: u64 = 2000;
 
 // The server will retry to send the response to the client and give up after RESPONSE_CHANNEL_SEND_TIMEOUT.
 // This is to prevent the server from being occupied by a slow client.
@@ -199,11 +202,26 @@ impl RawData for RawDataServerWrapper {
                     },
                 };
                 let mut cache_operator = CacheOperator::new(conn);
-                file_store_operator.verify_storage_bucket_existence().await;
 
-                // Validate redis chain id
+                // Validate chain id
+                let mut metadata = file_store_operator.get_file_store_metadata().await;
+                while metadata.is_none() {
+                    metadata = file_store_operator.get_file_store_metadata().await;
+                    tracing::warn!(
+                        "[File worker] File store metadata not found. Waiting for {} ms.",
+                        FILE_STORE_METADATA_WAIT_MS
+                    );
+                    tokio::time::sleep(std::time::Duration::from_millis(
+                        FILE_STORE_METADATA_WAIT_MS,
+                    ))
+                    .await;
+                }
+
+                let metadata_chain_id = metadata.unwrap().chain_id;
+
+                // Validate redis chain id. Must be present by the time it gets here
                 let chain_id = match cache_operator.get_chain_id().await {
-                    Ok(chain_id) => chain_id,
+                    Ok(chain_id) => chain_id.unwrap(),
                     Err(e) => {
                         ERROR_COUNT
                             .with_label_values(&["redis_get_chain_id_failed"])
@@ -217,20 +235,32 @@ impl RawData for RawDataServerWrapper {
                             .inc();
                         // Connection will be dropped anyway, so we ignore the error here.
                         let _result = tx
-                            .send_timeout(
-                                Err(Status::unavailable(
-                                    "[Data Service] Cannot get the chain id from redis; please retry.",
-                                )),
-                                RESPONSE_CHANNEL_SEND_TIMEOUT,
-                            )
-                            .await;
+                                            .send_timeout(
+                                                Err(Status::unavailable(
+                                                    "[Data Service] Cannot get the chain id from redis; please retry.",
+                                                )),
+                                                RESPONSE_CHANNEL_SEND_TIMEOUT,
+                                            )
+                                            .await;
                         error!(
                             error = e.to_string(),
                             "[Data Service] Failed to get chain id from redis."
                         );
                         return;
                     },
                 };
+
+                if metadata_chain_id != chain_id {
+                    let _result = tx
+                        .send_timeout(
+                            Err(Status::unavailable("[Data Service] Chain ID mismatch.")),
+                            RESPONSE_CHANNEL_SEND_TIMEOUT,
+                        )
+                        .await;
+                    error!("[Data Service] Chain ID mismatch.",);
+                    return;
+                }
+
                 // Data service metrics.
                 let mut tps_calculator = MovingAverage::new(MOVING_AVERAGE_WINDOW_SIZE);
 
@@ -241,7 +271,6 @@ impl RawData for RawDataServerWrapper {
                         current_version,
                         &mut cache_operator,
                         file_store_operator.as_ref(),
-                        current_batch_start_time,
                         request_metadata.clone(),
                     )
                     .await
@@ -314,7 +343,6 @@ impl RawData for RawDataServerWrapper {
                     let resp_items = get_transactions_responses_builder(
                         transaction_data,
                         chain_id as u32,
-                        current_batch_start_time,
                         request_metadata.clone(),
                     );
                     let data_latency_in_secs = resp_items
@@ -330,7 +358,6 @@ impl RawData for RawDataServerWrapper {
                     match channel_send_multiple_with_timeout(
                         resp_items,
                         tx.clone(),
-                        current_batch_start_time,
                         request_metadata.clone(),
                     )
                     .await
@@ -431,9 +458,9 @@ impl RawData for RawDataServerWrapper {
 fn get_transactions_responses_builder(
     data: Vec<EncodedTransactionWithVersion>,
     chain_id: u32,
-    current_batch_start_time: Instant,
     request_metadata: IndexerGrpcRequestMetadata,
 ) -> Vec<TransactionsResponse> {
+    let decode_start_time = Instant::now();
     let transactions: Vec<Transaction> = data
         .into_iter()
         .map(|(encoded, _)| {
@@ -468,7 +495,7 @@ fn get_transactions_responses_builder(
         Some(overall_end_version as i64),
         overall_start_txn_timestamp.as_ref(),
         overall_end_txn_timestamp.as_ref(),
-        Some(current_batch_start_time.elapsed().as_secs_f64()),
+        Some(decode_start_time.elapsed().as_secs_f64()),
         Some(overall_size_in_bytes),
         Some((overall_end_version - overall_start_version + 1) as i64),
         Some(request_metadata.clone()),
@@ -482,9 +509,9 @@ async fn data_fetch(
     starting_version: u64,
     cache_operator: &mut CacheOperator<redis::aio::ConnectionManager>,
     file_store_operator: &dyn FileStoreOperator,
-    current_batch_start_time: Instant,
     request_metadata: IndexerGrpcRequestMetadata,
 ) -> anyhow::Result<TransactionsDataStatus> {
+    let cache_fetch_start_time = Instant::now();
     let batch_get_result = cache_operator
         .batch_get_encoded_proto_data(starting_version)
         .await;
@@ -498,7 +525,6 @@ async fn data_fetch(
                 .map(|transaction| transaction.len())
                 .sum::<usize>();
             let num_of_transactions = transactions.len();
-            let duration_in_secs = current_batch_start_time.elapsed().as_secs_f64();
             let start_version_timestamp = {
                 let decoded_transaction = base64::decode(transactions.first().unwrap())
                     .expect("Failed to decode base64.");
@@ -521,7 +547,7 @@ async fn data_fetch(
                 Some(starting_version as i64 + num_of_transactions as i64 - 1),
                 start_version_timestamp.as_ref(),
                 end_version_timestamp.as_ref(),
-                Some(duration_in_secs),
+                Some(cache_fetch_start_time.elapsed().as_secs_f64()),
                 Some(size_in_bytes),
                 Some(num_of_transactions as i64),
                 Some(request_metadata.clone()),
@@ -533,6 +559,7 @@ async fn data_fetch(
         },
         Ok(CacheBatchGetStatus::EvictedFromCache) => {
             // Data is evicted from the cache. Fetch from file store.
+            let file_store_fetch_start_time = Instant::now();
             let file_store_batch_get_result =
                 file_store_operator.get_transactions(starting_version).await;
             match file_store_batch_get_result {
@@ -542,7 +569,6 @@ async fn data_fetch(
                         .map(|transaction| transaction.len())
                         .sum::<usize>();
                     let num_of_transactions = transactions.len();
-                    let duration_in_secs = current_batch_start_time.elapsed().as_secs_f64();
                     let start_version_timestamp = {
                         let decoded_transaction = base64::decode(transactions.first().unwrap())
                             .expect("Failed to decode base64.");
@@ -565,7 +591,7 @@ async fn data_fetch(
                         Some(starting_version as i64 + num_of_transactions as i64 - 1),
                         start_version_timestamp.as_ref(),
                         end_version_timestamp.as_ref(),
-                        Some(duration_in_secs),
+                        Some(file_store_fetch_start_time.elapsed().as_secs_f64()),
                         Some(size_in_bytes),
                         Some(num_of_transactions as i64),
                         Some(request_metadata.clone()),
@@ -660,9 +686,9 @@ fn get_request_metadata(
 async fn channel_send_multiple_with_timeout(
     resp_items: Vec<TransactionsResponse>,
     tx: tokio::sync::mpsc::Sender<Result<TransactionsResponse, Status>>,
-    current_batch_start_time: Instant,
     request_metadata: IndexerGrpcRequestMetadata,
 ) -> Result<(), SendTimeoutError<Result<TransactionsResponse, Status>>> {
+    let overall_send_start_time = Instant::now();
     let overall_size_in_bytes = resp_items
         .iter()
         .map(|resp_item| resp_item.encoded_len())
@@ -675,6 +701,7 @@ async fn channel_send_multiple_with_timeout(
     let overall_end_txn_timestamp = overall_end_txn.clone().timestamp;
 
     for resp_item in resp_items {
+        let send_start_time = Instant::now();
         let response_size = resp_item.encoded_len();
         let num_of_transactions = resp_item.transactions.len();
         let start_version = resp_item.transactions.first().unwrap().version;
@@ -707,7 +734,7 @@ async fn channel_send_multiple_with_timeout(
             Some(end_version as i64),
             Some(start_version_txn_timestamp),
             Some(end_version_txn_timestamp),
-            Some(current_batch_start_time.elapsed().as_secs_f64()),
+            Some(send_start_time.elapsed().as_secs_f64()),
             Some(response_size),
             Some(num_of_transactions as i64),
             Some(request_metadata.clone()),
@@ -721,7 +748,7 @@ async fn channel_send_multiple_with_timeout(
         Some(overall_end_version as i64),
         overall_start_txn_timestamp.as_ref(),
         overall_end_txn_timestamp.as_ref(),
-        Some(current_batch_start_time.elapsed().as_secs_f64()),
+        Some(overall_send_start_time.elapsed().as_secs_f64()),
         Some(overall_size_in_bytes),
         Some((overall_end_version - overall_start_version + 1) as i64),
         Some(request_metadata.clone()),
```

### ecosystem/indexer-grpc/indexer-grpc-file-store/src/lib.rs
```diff
@@ -4,7 +4,7 @@
 pub mod metrics;
 pub mod processor;
 
-use anyhow::{Context, Result};
+use anyhow::Result;
 use aptos_indexer_grpc_server_framework::RunnableConfig;
 use aptos_indexer_grpc_utils::{config::IndexerGrpcFileStoreConfig, types::RedisUrl};
 use processor::Processor;
@@ -16,18 +16,21 @@ pub struct IndexerGrpcFileStoreWorkerConfig {
     pub file_store_config: IndexerGrpcFileStoreConfig,
     pub redis_main_instance_address: RedisUrl,
     pub enable_expensive_logging: Option<bool>,
+    pub chain_id: u64,
 }
 
 impl IndexerGrpcFileStoreWorkerConfig {
     pub fn new(
         file_store_config: IndexerGrpcFileStoreConfig,
         redis_main_instance_address: RedisUrl,
         enable_expensive_logging: Option<bool>,
+        chain_id: u64,
     ) -> Self {
         Self {
             file_store_config,
             redis_main_instance_address,
             enable_expensive_logging,
+            chain_id,
         }
     }
 }
@@ -39,14 +42,15 @@ impl RunnableConfig for IndexerGrpcFileStoreWorkerConfig {
             self.redis_main_instance_address.clone(),
             self.file_store_config.clone(),
             self.enable_expensive_logging.unwrap_or(false),
+            self.chain_id,
         )
         .await
-        .context("Failed to create processor for file store worker")?;
+        .expect("Failed to create file store processor");
         processor
             .run()
             .await
             .expect("File store processor exited unexpectedly");
-        Err(anyhow::anyhow!("File store processor exited unexpectedly"))
+        Ok(())
     }
 
     fn get_server_name(&self) -> String {
```

### ecosystem/indexer-grpc/indexer-grpc-file-store/src/main.rs
```diff
@@ -9,5 +9,8 @@ use clap::Parser;
 #[tokio::main]
 async fn main() -> Result<()> {
     let args = ServerArgs::parse();
-    args.run::<IndexerGrpcFileStoreWorkerConfig>().await
+    args.run::<IndexerGrpcFileStoreWorkerConfig>()
+        .await
+        .expect("Failed to run server");
+    Ok(())
 }
```

### ecosystem/indexer-grpc/indexer-grpc-file-store/src/processor.rs
```diff
@@ -2,7 +2,7 @@
 // SPDX-License-Identifier: Apache-2.0
 
 use crate::metrics::{METADATA_UPLOAD_FAILURE_COUNT, PROCESSED_VERSIONS_COUNT};
-use anyhow::{bail, Context, Result};
+use anyhow::{bail, ensure, Context, Result};
 use aptos_indexer_grpc_utils::{
     build_protobuf_encoded_transaction_wrappers,
     cache_operator::{CacheBatchGetStatus, CacheOperator},
@@ -27,7 +27,7 @@ const SERVICE_TYPE: &str = "file_worker";
 pub struct Processor {
     cache_operator: CacheOperator<redis::aio::ConnectionManager>,
     file_store_operator: Box<dyn FileStoreOperator>,
-    cache_chain_id: u64,
+    chain_id: u64,
     enable_expensive_logging: bool,
 }
 
@@ -36,6 +36,7 @@ impl Processor {
         redis_main_instance_address: RedisUrl,
         file_store_config: IndexerGrpcFileStoreConfig,
         enable_expensive_logging: bool,
+        chain_id: u64,
     ) -> Result<Self> {
         // Connection to redis is a hard dependency for file store processor.
         let conn = redis::Client::open(redis_main_instance_address.0.clone())
@@ -53,14 +54,9 @@ impl Processor {
                     redis_main_instance_address.0
                 )
             })?;
-
         let mut cache_operator = CacheOperator::new(conn);
-        let cache_chain_id = cache_operator
-            .get_chain_id()
-            .await
-            .context("Get chain id failed.")?;
 
-        let file_store_operator: Box<dyn FileStoreOperator> = match &file_store_config {
+        let mut file_store_operator: Box<dyn FileStoreOperator> = match &file_store_config {
             IndexerGrpcFileStoreConfig::GcsFileStore(gcs_file_store) => {
                 Box::new(GcsFileStoreOperator::new(
                     gcs_file_store.gcs_file_store_bucket_name.clone(),
@@ -74,11 +70,47 @@ impl Processor {
             ),
         };
         file_store_operator.verify_storage_bucket_existence().await;
+        let file_store_metadata: Option<
+            aptos_indexer_grpc_utils::file_store_operator::FileStoreMetadata,
+        > = file_store_operator.get_file_store_metadata().await;
+        if file_store_metadata.is_none() {
+            // If metadata doesn't exist, create and upload it and init file store latest version in cache.
+            while file_store_operator
+                .update_file_store_metadata_with_timeout(chain_id, 0)
+                .await
+                .is_err()
+            {
+                tracing::error!(
+                    batch_start_version = 0,
+                    service_type = SERVICE_TYPE,
+                    "[File worker] Failed to update file store metadata. Retrying."
+                );
+                std::thread::sleep(std::time::Duration::from_millis(500));
+                METADATA_UPLOAD_FAILURE_COUNT.inc();
+            }
+        }
+        // Metadata is guaranteed to exist now
+        let metadata = file_store_operator.get_file_store_metadata().await.unwrap();
 
+        ensure!(metadata.chain_id == chain_id, "Chain ID mismatch.");
+        let batch_start_version = metadata.version;
+        // Cache config in the cache
+        cache_operator.cache_setup_if_needed().await?;
+        match cache_operator.get_chain_id().await? {
+            Some(id) => {
+                ensure!(id == chain_id, "Chain ID mismatch.");
+            },
+            None => {
+                cache_operator.set_chain_id(chain_id).await?;
+            },
+        }
+        cache_operator
+            .update_file_store_latest_version(batch_start_version)
+            .await?;
         Ok(Self {
             cache_operator,
             file_store_operator,
-            cache_chain_id,
+            chain_id,
             enable_expensive_logging,
         })
     }
@@ -91,20 +123,21 @@ impl Processor {
     ///   3.2 If we're ready to process, create max of 10 threads and fetch / upload data
     ///   3.3 Update file store metadata at the end of a batch
     pub async fn run(&mut self) -> Result<()> {
-        let cache_chain_id = self.cache_chain_id;
+        let chain_id = self.chain_id;
 
-        let mut batch_start_version =
-            if let Some(metadata) = self.file_store_operator.get_file_store_metadata().await {
-                anyhow::ensure!(metadata.chain_id == cache_chain_id, "Chain ID mismatch.");
-                metadata.version
-            } else {
-                0
-            };
+        let metadata = self
+            .file_store_operator
+            .get_file_store_metadata()
+            .await
+            .unwrap();
+        ensure!(metadata.chain_id == chain_id, "Chain ID mismatch.");
+
+        let mut batch_start_version = metadata.version;
 
         let mut tps_calculator = MovingAverage::new(10_000);
         loop {
             let latest_loop_time = std::time::Instant::now();
-            let cache_worker_latest = self.cache_operator.get_latest_version().await?;
+            let cache_worker_latest = self.cache_operator.get_latest_version().await?.unwrap();
 
             // batches tracks the start version of the batches to fetch. 1000 at the time
             let mut batches = vec![];
@@ -134,15 +167,43 @@ impl Processor {
                 let mut cache_operator_clone = self.cache_operator.clone();
                 let mut file_store_operator_clone = self.file_store_operator.clone_box();
                 let task = tokio::spawn(async move {
+                    let fetch_start_time = std::time::Instant::now();
                     let transactions = cache_operator_clone
                         .batch_get_encoded_proto_data_x(start_version, BLOB_STORAGE_SIZE as u64)
                         .await
                         .unwrap();
                     let last_transaction = transactions.last().unwrap().0.clone();
+                    log_grpc_step(
+                        SERVICE_TYPE,
+                        IndexerGrpcStep::FilestoreFetchTxns,
+                        Some(start_version as i64),
+                        Some((start_version + BLOB_STORAGE_SIZE as u64 - 1) as i64),
+                        None,
+                        None,
+                        Some(fetch_start_time.elapsed().as_secs_f64()),
+                        None,
+                        Some(BLOB_STORAGE_SIZE as i64),
+                        None,
+                    );
+
+                    let upload_start_time = std::time::Instant::now();
                     let (start, end) = file_store_operator_clone
-                        .upload_transaction_batch(cache_chain_id, transactions)
+                        .upload_transaction_batch(chain_id, transactions)
                         .await
                         .unwrap();
+                    log_grpc_step(
+                        SERVICE_TYPE,
+                        IndexerGrpcStep::FilestoreUploadTxns,
+                        Some(start_version as i64),
+                        Some((start_version + BLOB_STORAGE_SIZE as u64 - 1) as i64),
+                        None,
+                        None,
+                        Some(upload_start_time.elapsed().as_secs_f64()),
+                        None,
+                        Some(BLOB_STORAGE_SIZE as i64),
+                        None,
+                    );
+
                     (start, end, last_transaction)
                 });
                 tasks.push(task);
@@ -206,7 +267,7 @@ impl Processor {
                 .await?;
             while self
                 .file_store_operator
-                .update_file_store_metadata_with_timeout(cache_chain_id, batch_start_version)
+                .update_file_store_metadata_with_timeout(chain_id, batch_start_version)
                 .await
                 .is_err()
             {
@@ -252,7 +313,7 @@ impl Processor {
             let full_loop_duration = latest_loop_time.elapsed().as_secs_f64();
             log_grpc_step(
                 SERVICE_TYPE,
-                IndexerGrpcStep::FilestoreUploadTxns,
+                IndexerGrpcStep::FilestoreProcessedBatch,
                 Some(first_version as i64),
                 Some(last_version as i64),
                 start_version_timestamp.as_ref(),
```

### ecosystem/indexer-grpc/indexer-grpc-fullnode/src/stream_coordinator.rs
```diff
@@ -95,7 +95,7 @@ impl IndexerStreamCoordinator {
             let transaction_sender = self.transactions_sender.clone();
 
             let task = tokio::spawn(async move {
-                let batch_start_time = std::time::Instant::now();
+                let fetch_start_time = std::time::Instant::now();
                 // Fetch and convert transactions from API
                 let raw_txns =
                     Self::fetch_raw_txns_with_retries(context.clone(), ledger_version, batch).await;
@@ -118,9 +118,11 @@ impl IndexerStreamCoordinator {
                     last_transaction_timestamp.as_ref(),
                     Some(ledger_version as i64),
                     None,
-                    Some(batch_start_time.elapsed().as_secs_f64()),
+                    Some(fetch_start_time.elapsed().as_secs_f64()),
                     Some(raw_txns.len() as i64),
                 );
+
+                let convert_start_time = std::time::Instant::now();
                 let api_txns = Self::convert_to_api_txns(context, raw_txns).await;
                 api_txns.last().map(record_fetched_transaction_latency);
                 let pb_txns = Self::convert_to_pb_txns(api_txns);
@@ -135,10 +137,12 @@ impl IndexerStreamCoordinator {
                     end_txn_timestamp.as_ref(),
                     Some(ledger_version as i64),
                     None,
-                    Some(batch_start_time.elapsed().as_secs_f64()),
+                    Some(convert_start_time.elapsed().as_secs_f64()),
                     Some(pb_txns.len() as i64),
                 );
 
+                let send_start_time = std::time::Instant::now();
+
                 // Wrap in stream response object and send to channel
                 for chunk in pb_txns.chunks(output_batch_size as usize) {
                     for chunk in chunk_transactions(chunk.to_vec(), MESSAGE_SIZE_LIMIT) {
@@ -169,7 +173,7 @@ impl IndexerStreamCoordinator {
                     end_txn_timestamp.as_ref(),
                     Some(ledger_version as i64),
                     None,
-                    Some(batch_start_time.elapsed().as_secs_f64()),
+                    Some(send_start_time.elapsed().as_secs_f64()),
                     Some(pb_txns.len() as i64),
                 );
                 Ok(end_transaction.version)
```

### ecosystem/indexer-grpc/indexer-grpc-server-framework/src/lib.rs
```diff
@@ -44,21 +44,24 @@ where
         register_probes_and_metrics_handler(health_port).await;
         Ok(())
     });
-    let main_task_handler = tokio::spawn(async move { config.run().await });
+    let main_task_handler =
+        tokio::spawn(async move { config.run().await.expect("task should exit with Ok.") });
     tokio::select! {
         res = task_handler => {
             if let Err(e) = res {
                 error!("Probes and metrics handler panicked or was shutdown: {:?}", e);
                 process::exit(1);
+            } else {
+                panic!("Probes and metrics handler exited unexpectedly");
             }
-            Ok(())
         },
         res = main_task_handler => {
             if let Err(e) = res {
                 error!("Main task panicked or was shutdown: {:?}", e);
                 process::exit(1);
+            } else {
+                panic!("Main task exited unexpectedly");
             }
-            Ok(())
         },
     }
 }
```

### ecosystem/indexer-grpc/indexer-grpc-utils/src/cache_operator.rs
```diff
@@ -26,22 +26,6 @@ const BASE_EXPIRATION_EPOCH_TIME_IN_SECONDS: u64 = 253_402_300_799;
 const CACHE_DEFAULT_LATEST_VERSION_NUMBER: &str = "0";
 const FILE_STORE_LATEST_VERSION: &str = "file_store_latest_version";
 
-// Returns 1 if the chain id is updated or verified. Otherwise(chain id not match), returns 0.
-// TODO(larry): add a test for this script.
-const CACHE_SCRIPT_UPDATE_OR_VERIFY_CHAIN_ID: &str = r#"
-    local chain_id = redis.call("GET", KEYS[1])
-    if chain_id then
-        if chain_id == ARGV[1] then
-            return 1
-        else
-            return 0
-        end
-    else
-        redis.call("SET", KEYS[1], ARGV[1])
-        return 1
-    end
-"#;
-
 /// This Lua script is used to update the latest version in cache.
 ///   Returns 0 if the cache is updated to 0 or sequentially update.
 ///   Returns 1 if the cache is updated but overlap detected.
@@ -135,47 +119,37 @@ impl<T: redis::aio::ConnectionLike + Send + Clone> CacheOperator<T> {
         Ok(version_inserted)
     }
 
-    // Update the chain id in cache if missing; otherwise, verify the chain id.
-    // It's a fatal error if the chain id is not correct.
-    pub async fn update_or_verify_chain_id(&mut self, chain_id: u64) -> anyhow::Result<()> {
-        let script = redis::Script::new(CACHE_SCRIPT_UPDATE_OR_VERIFY_CHAIN_ID);
-        let result: u8 = script
-            .key(CACHE_KEY_CHAIN_ID)
-            .arg(chain_id)
-            .invoke_async(&mut self.conn)
+    pub async fn set_chain_id(&mut self, chain_id: u64) -> anyhow::Result<()> {
+        self.conn
+            .set(CACHE_KEY_CHAIN_ID, chain_id)
             .await
-            .context("Redis chain id update/verification failed.")?;
-        if result != 1 {
-            anyhow::bail!("Chain id is not correct.");
-        }
+            .context("Redis chain id update failed.")?;
         Ok(())
     }
 
-    // Downstream system can infer the chain id from cache.
-    pub async fn get_chain_id(&mut self) -> anyhow::Result<u64> {
-        let chain_id: u64 = match self.conn.get::<&str, String>(CACHE_KEY_CHAIN_ID).await {
-            Ok(v) => v
-                .parse::<u64>()
-                .with_context(|| format!("Redis key {} is not a number.", CACHE_KEY_CHAIN_ID))?,
-            Err(err) => return Err(err.into()),
-        };
-        Ok(chain_id)
+    pub async fn get_chain_id(&mut self) -> anyhow::Result<Option<u64>> {
+        self.get_config_by_key(CACHE_KEY_CHAIN_ID).await
     }
 
-    pub async fn get_latest_version(&mut self) -> anyhow::Result<u64> {
-        self.conn
-            .get::<&str, String>(CACHE_KEY_LATEST_VERSION)
-            .await?
-            .parse::<u64>()
-            .context("Redis latest_version is not a number.")
+    pub async fn get_latest_version(&mut self) -> anyhow::Result<Option<u64>> {
+        self.get_config_by_key(CACHE_KEY_LATEST_VERSION).await
     }
 
-    pub async fn get_file_store_latest_version(&mut self) -> anyhow::Result<u64> {
-        self.conn
-            .get::<&str, String>(FILE_STORE_LATEST_VERSION)
-            .await?
-            .parse::<u64>()
-            .context("Redis file_store_latest_version is not a number.")
+    pub async fn get_file_store_latest_version(&mut self) -> anyhow::Result<Option<u64>> {
+        self.get_config_by_key(FILE_STORE_LATEST_VERSION).await
+    }
+
+    /// This gets latest version, chain id, and file store latest version
+    async fn get_config_by_key(&mut self, key: &str) -> anyhow::Result<Option<u64>> {
+        let result = self.conn.get::<&str, Vec<u8>>(key).await?;
+        if result.is_empty() {
+            Ok(None)
+        } else {
+            let result_string = String::from_utf8(result).unwrap();
+            Ok(Some(result_string.parse::<u64>().with_context(|| {
+                format!("Redis key {} is not a number.", key)
+            })?))
+        }
     }
 
     pub async fn update_file_store_latest_version(
@@ -539,7 +513,7 @@ mod tests {
         let mut cache_operator: CacheOperator<MockRedisConnection> =
             CacheOperator::new(mock_connection);
 
-        assert_eq!(cache_operator.get_chain_id().await.unwrap(), 123);
+        assert_eq!(cache_operator.get_chain_id().await.unwrap(), Some(123));
     }
 
     // Cache latest version tests.
@@ -554,7 +528,10 @@ mod tests {
         let mut cache_operator: CacheOperator<MockRedisConnection> =
             CacheOperator::new(mock_connection);
 
-        assert_eq!(cache_operator.get_latest_version().await.unwrap(), version);
+        assert_eq!(
+            cache_operator.get_latest_version().await.unwrap(),
+            Some(version)
+        );
     }
 
     // Cache update cache transactions tests.
```
