# [?] Relayer syncing can't double spend (#971)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2023-02-08
Source: https://github.com/FuelLabs/fuel-core/commit/51541e173f7a8213303562f381b9f230cd27e40c
Type: security-commit

## Details
Relayer syncing can't double spend (#971)

closes #781 #681 #977

---------

Co-authored-by: green <xgreenx9999@gmail.com>
Co-authored-by: Brandon Kite <brandonkite92@gmail.com>

## Patch
### Cargo.lock
```diff
@@ -2411,6 +2411,7 @@ dependencies = [
  "serde_json",
  "tai64",
  "thiserror",
+ "tracing",
 ]
 
 [[package]]
@@ -2433,6 +2434,7 @@ dependencies = [
  "fuel-core-poa",
  "fuel-core-types",
  "test-case",
+ "tokio",
 ]
 
 [[package]]
@@ -2615,6 +2617,7 @@ dependencies = [
  "anyhow",
  "fuel-core-types",
  "fuel-vm",
+ "mockall",
  "thiserror",
 ]
 
```

### README.md
```diff
@@ -165,6 +165,6 @@ RET(RegId::ONE),
 ```
 
 ```console
-$ cargo run --bin fuel-gql-cli -- transaction submit \
+$ cargo run --bin fuel-core-client -- transaction submit \
 "{\"Script\":{\"gas_price\":0,\"gas_limit\":1000000,\"maturity\":0,\"script\":[80,64,0,202,80,68,0,186,51,65,16,0,36,4,0,0],\"script_data\":[],\"inputs\":[],\"outputs\":[],\"witnesses\":[],\"receipts_root\":\"0x6114142d12e0f58cfb8c72c270cd0535944fb1ba763dce83c17e882c482224a2\"}}"
 ```
```

### bin/fuel-core/src/cli/run.rs
```diff
@@ -21,6 +21,7 @@ use fuel_core::{
         config::Trigger,
         Config,
         DbType,
+        RelayerVerifierConfig,
         ServiceTrait,
         VMConfig,
     },
@@ -144,6 +145,11 @@ pub struct Command {
 
     #[arg(long = "metrics", env)]
     pub metrics: bool,
+
+    #[clap(long = "verify_max_da_lag", default_value = "10", env)]
+    pub max_da_lag: u64,
+    #[clap(long = "verify_max_relayer_wait", default_value = "30s", env)]
+    pub max_wait_time: humantime::Duration,
 }
 
 impl Command {
@@ -169,6 +175,8 @@ impl Command {
             #[cfg(feature = "p2p")]
             sync_args,
             metrics,
+            max_da_lag,
+            max_wait_time,
         } = self;
 
         let addr = net::SocketAddr::new(ip, port);
@@ -218,6 +226,11 @@ impl Command {
                 .unwrap_or_default()
         };
 
+        let verifier = RelayerVerifierConfig {
+            max_da_lag: max_da_lag.into(),
+            max_wait_time: max_wait_time.into(),
+        };
+
         Ok(Config {
             addr,
             database_path,
@@ -245,6 +258,7 @@ impl Command {
             sync: sync_args.into(),
             consensus_key,
             name: String::default(),
+            verifier,
         })
     }
 }
```

### crates/chain-config/src/config/message.rs
```diff
@@ -8,7 +8,7 @@ use crate::{
 use fuel_core_storage::MerkleRoot;
 use fuel_core_types::{
     blockchain::primitives::DaBlockHeight,
-    entities::message::Message,
+    entities::message::CompressedMessage,
     fuel_asm::Word,
     fuel_types::Address,
 };
@@ -40,21 +40,20 @@ pub struct MessageConfig {
     pub da_height: DaBlockHeight,
 }
 
-impl From<MessageConfig> for Message {
+impl From<MessageConfig> for CompressedMessage {
     fn from(msg: MessageConfig) -> Self {
-        Message {
+        CompressedMessage {
             sender: msg.sender,
             recipient: msg.recipient,
             nonce: msg.nonce,
             amount: msg.amount,
             data: msg.data,
             da_height: msg.da_height,
-            fuel_block_spend: None,
         }
     }
 }
 
-impl GenesisCommitment for Message {
+impl GenesisCommitment for CompressedMessage {
     fn root(&self) -> anyhow::Result<MerkleRoot> {
         Ok(self.id().into())
     }
```

### crates/client/Cargo.toml
```diff
@@ -26,6 +26,7 @@ serde = { workspace = true, features = ["derive"] }
 serde_json = { version = "1.0", features = ["raw_value"] }
 tai64 = { version = "4.0", features = ["serde"] }
 thiserror = "1.0"
+tracing = "0.1"
 
 [dev-dependencies]
 insta = { workspace = true }
```

### crates/client/assets/schema.sdl
```diff
@@ -372,7 +372,7 @@ type Message {
 	nonce: U64!
 	data: HexString!
 	daHeight: U64!
-	fuelBlockSpend: U64
+	status: MessageStatus!
 }
 
 type MessageConnection {
@@ -423,6 +423,11 @@ type MessageProof {
 	header: Header!
 }
 
+enum MessageStatus {
+	UNSPENT
+	SPENT
+}
+
 type Mutation {
 	startSession: ID!
 	endSession(id: ID!): Boolean!
```

### crates/client/src/client.rs
```diff
@@ -79,6 +79,7 @@ use std::{
         FromStr,
     },
 };
+use tracing as _;
 use types::{
     TransactionResponse,
     TransactionStatus,
@@ -180,6 +181,7 @@ impl FuelClient {
         }
     }
 
+    #[tracing::instrument(skip_all)]
     #[cfg(feature = "subscriptions")]
     async fn subscribe<ResponseData, Vars>(
         &self,
@@ -219,6 +221,7 @@ impl FuelClient {
                 futures::future::ready(!matches!(result, Err(es::Error::Eof)))
             })
             .filter_map(move |result| {
+                tracing::debug!("Got result: {result:?}");
                 let r = match result {
                     Ok(es::SSE::Event(es::Event { data, .. })) => {
                         match serde_json::from_str::<GraphQlResponse<ResponseData>>(&data)
@@ -464,6 +467,7 @@ impl FuelClient {
         Ok(status)
     }
 
+    #[tracing::instrument(skip(self), level = "debug")]
     #[cfg(feature = "subscriptions")]
     /// Subscribe to the status of a transaction
     pub async fn subscribe_transaction_status(
@@ -473,7 +477,9 @@ impl FuelClient {
         use cynic::SubscriptionBuilder;
         let s = schema::tx::StatusChangeSubscription::build(TxIdArgs { id: id.parse()? });
 
+        tracing::debug!("subscribing");
         let stream = self.subscribe(s).await?.map(|tx| {
+            tracing::debug!("received {tx:?}");
             let tx = tx?;
             let status = tx.status_change.try_into()?;
             Ok(status)
```

### crates/client/src/client/schema/message.rs
```diff
@@ -26,7 +26,14 @@ pub struct Message {
     pub nonce: U64,
     pub data: HexString,
     pub da_height: U64,
-    pub fuel_block_spend: Option<U64>,
+    pub status: MessageStatus,
+}
+
+#[derive(cynic::Enum, Clone, Copy, Debug, Eq, PartialEq)]
+#[cynic(schema_path = "./assets/schema.sdl")]
+pub enum MessageStatus {
+    Unspent,
+    Spent,
 }
 
 #[derive(cynic::QueryFragment, Debug)]
```

### crates/client/src/client/schema/snapshots/fuel_core_client__client__schema__message__tests__owned_message_query_gql_output.snap
```diff
@@ -14,7 +14,7 @@ query($owner: Address, $after: String, $before: String, $first: Int, $last: Int)
         nonce
         data
         daHeight
-        fuelBlockSpend
+        status
       }
     }
     pageInfo {
```

### crates/fuel-core/src/database.rs
```diff
@@ -112,6 +112,13 @@ pub enum Column {
     FuelBlockMerkleData = 17,
     /// See [`FuelBlockMerkleMetadata`](storage::FuelBlockMerkleMetadata)
     FuelBlockMerkleMetadata = 18,
+    /// Messages that have been spent.
+    /// Existence of a key in this column means that the message has been spent.
+    /// See [`SpentMessages`](fuel_core_storage::tables::SpentMessages)
+    SpentMessages = 19,
+    /// Metadata for the relayer
+    /// See [`RelayerMetadata`](fuel_core_relayer::ports::RelayerMetadata)
+    RelayerMetadata = 20,
 }
 
 #[derive(Clone, Debug)]
@@ -298,7 +305,9 @@ impl Database {
     }
 }
 
-impl Transactional<Database> for Database {
+impl Transactional for Database {
+    type Storage = Database;
+
     fn transaction(&self) -> StorageTransaction<Database> {
         StorageTransaction::new(self.transaction())
     }
```

### crates/fuel-core/src/database/message.rs
```diff
@@ -8,13 +8,20 @@ use crate::{
 };
 use fuel_core_chain_config::MessageConfig;
 use fuel_core_storage::{
-    tables::Messages,
+    tables::{
+        Messages,
+        SpentMessages,
+    },
     Error as StorageError,
+    Result as StorageResult,
     StorageInspect,
     StorageMutate,
 };
 use fuel_core_types::{
-    entities::message::Message,
+    entities::message::{
+        CompressedMessage,
+        MessageStatus,
+    },
     fuel_types::{
         Address,
         Bytes32,
@@ -26,10 +33,15 @@ use std::{
     ops::Deref,
 };
 
+use super::storage::DatabaseColumn;
+
 impl StorageInspect<Messages> for Database {
     type Error = StorageError;
 
-    fn get(&self, key: &MessageId) -> Result<Option<Cow<Message>>, Self::Error> {
+    fn get(
+        &self,
+        key: &MessageId,
+    ) -> Result<Option<Cow<CompressedMessage>>, Self::Error> {
         Database::get(self, key.as_ref(), Column::Messages).map_err(Into::into)
     }
 
@@ -42,8 +54,8 @@ impl StorageMutate<Messages> for Database {
     fn insert(
         &mut self,
         key: &MessageId,
-        value: &Message,
-    ) -> Result<Option<Message>, Self::Error> {
+        value: &CompressedMessage,
+    ) -> Result<Option<CompressedMessage>, Self::Error> {
         // insert primary record
         let result = Database::insert(self, key.as_ref(), Column::Messages, value)?;
 
@@ -58,8 +70,11 @@ impl StorageMutate<Messages> for Database {
         Ok(result)
     }
 
-    fn remove(&mut self, key: &MessageId) -> Result<Option<Message>, Self::Error> {
-        let result: Option<Message> =
+    fn remove(
+        &mut self,
+        key: &MessageId,
+    ) -> Result<Option<CompressedMessage>, Self::Error> {
+        let result: Option<CompressedMessage> =
             Database::remove(self, key.as_ref(), Column::Messages)?;
 
         if let Some(message) = &result {
@@ -74,6 +89,12 @@ impl StorageMutate<Messages> for Database {
     }
 }
 
+impl DatabaseColumn for SpentMessages {
+    fn column() -> Column {
+        Column::SpentMessages
+    }
+}
+
 impl Database {
     pub fn owned_message_ids(
         &self,
@@ -99,28 +120,32 @@ impl Database {
         &self,
         start: Option<MessageId>,
         direction: Option<IterDirection>,
-    ) -> impl Iterator<Item = DatabaseResult<Message>> + '_ {
+    ) -> impl Iterator<Item = DatabaseResult<CompressedMessage>> + '_ {
         let start = start.map(|v| v.deref().to_vec());
-        self.iter_all_by_start::<Vec<u8>, Message, _>(Column::Messages, start, direction)
-            .map(|res| res.map(|(_, message)| message))
+        self.iter_all_by_start::<Vec<u8>, CompressedMessage, _>(
+            Column::Messages,
+            start,
+            direction,
+        )
+        .map(|res| res.map(|(_, message)| message))
     }
 
-    pub fn get_message_config(&self) -> DatabaseResult<Option<Vec<MessageConfig>>> {
+    pub fn get_message_config(&self) -> StorageResult<Option<Vec<MessageConfig>>> {
         let configs = self
             .all_messages(None, None)
             .filter_map(|msg| {
                 // Return only unspent messages
                 if let Ok(msg) = msg {
-                    if msg.fuel_block_spend.is_none() {
-                        Some(Ok(msg))
-                    } else {
-                        None
+                    match self.is_message_spent(&msg.id()) {
+                        Ok(false) => Some(Ok(msg)),
+                        Ok(true) => None,
+                        Err(e) => Some(Err(e)),
                     }
                 } else {
-                    Some(msg)
+                    Some(msg.map_err(StorageError::from))
                 }
             })
-            .map(|msg| -> DatabaseResult<MessageConfig> {
+            .map(|msg| -> StorageResult<MessageConfig> {
                 let msg = msg?;
 
                 Ok(MessageConfig {
@@ -132,10 +157,23 @@ impl Database {
                     da_height: msg.da_height,
                 })
             })
-            .collect::<DatabaseResult<Vec<MessageConfig>>>()?;
+            .collect::<StorageResult<Vec<MessageConfig>>>()?;
 
         Ok(Some(configs))
     }
+
+    pub fn is_message_spent(&self, message_id: &MessageId) -> StorageResult<bool> {
+        fuel_core_storage::StorageAsRef::storage::<SpentMessages>(&self)
+            .contains_key(message_id)
+    }
+
+    pub fn message_status(&self, message_id: &MessageId) -> StorageResult<MessageStatus> {
+        if self.is_message_spent(message_id)? {
+            Ok(MessageStatus::Spent)
+        } else {
+            Ok(MessageStatus::Unspent)
+        }
+    }
 }
 
 // TODO: Reuse `fuel_vm::storage::double_key` macro.
@@ -158,7 +196,7 @@ mod tests {
     #[test]
     fn owned_message_ids() {
         let mut db = Database::default();
-        let message = Message::default();
+        let message = CompressedMessage::default();
 
         // insert a message with the first id
         let first_id = MessageId::new([1; 32]);
```

### crates/fuel-core/src/database/metadata.rs
```diff
@@ -8,8 +8,6 @@ use fuel_core_chain_config::ChainConfig;
 
 pub(crate) const DB_VERSION_KEY: &[u8] = b"version";
 pub(crate) const CHAIN_NAME_KEY: &[u8] = b"chain_name";
-#[cfg(feature = "relayer")]
-pub(crate) const FINALIZED_DA_HEIGHT_KEY: &[u8] = b"finalized_da_height";
 
 /// Can be used to perform migrations in the future.
 pub(crate) const DB_VERSION: u32 = 0;
```
