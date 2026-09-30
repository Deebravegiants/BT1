# [?] fix: egress id race condition (#4235)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2023-11-16
Source: https://github.com/chainflip-io/chainflip-backend/commit/4e9d18aa453599d46e2703ce4941efaefa046392
Type: security-commit

## Details
fix: egress id race condition (#4235)

## Patch
### engine/src/witness/btc.rs
```diff
@@ -5,7 +5,7 @@ pub mod btc_source;
 use std::sync::Arc;
 
 use bitcoin::{BlockHash, Transaction};
-use cf_chains::btc::{deposit_address::DepositAddress, CHANGE_ADDRESS_SALT};
+use cf_chains::btc::{self, deposit_address::DepositAddress, BlockNumber, CHANGE_ADDRESS_SALT};
 use cf_primitives::EpochIndex;
 use futures_core::Future;
 use secp256k1::hashes::Hash;
@@ -32,7 +32,7 @@ const SAFETY_MARGIN: usize = 5;
 
 pub async fn process_egress<ProcessCall, ProcessingFut, ExtraInfo, ExtraHistoricInfo>(
 	epoch: Vault<cf_chains::Bitcoin, ExtraInfo, ExtraHistoricInfo>,
-	header: Header<u64, BlockHash, (Vec<Transaction>, Vec<[u8; 32]>)>,
+	header: Header<u64, BlockHash, (Vec<Transaction>, Vec<(btc::Hash, BlockNumber)>)>,
 	process_call: ProcessCall,
 ) where
 	ProcessCall: Fn(state_chain_runtime::RuntimeCall, EpochIndex) -> ProcessingFut
@@ -44,7 +44,9 @@ pub async fn process_egress<ProcessCall, ProcessingFut, ExtraInfo, ExtraHistoric
 {
 	let (txs, monitored_tx_hashes) = header.data;
 
-	for tx_hash in success_witnesses(&monitored_tx_hashes, &txs) {
+	let monitored_tx_hashes = monitored_tx_hashes.iter().map(|(tx_hash, _)| tx_hash);
+
+	for tx_hash in success_witnesses(monitored_tx_hashes, &txs) {
 		process_call(
 			state_chain_runtime::RuntimeCall::BitcoinBroadcaster(
 				pallet_cf_broadcast::Call::transaction_succeeded {
@@ -156,11 +158,16 @@ where
 	Ok(())
 }
 
-fn success_witnesses(monitored_tx_hashes: &[[u8; 32]], txs: &Vec<Transaction>) -> Vec<[u8; 32]> {
+fn success_witnesses<'a>(
+	monitored_tx_hashes: impl Iterator<Item = &'a btc::Hash> + Clone,
+	txs: &Vec<Transaction>,
+) -> Vec<btc::Hash> {
 	let mut successful_witnesses = Vec::new();
+
 	for tx in txs {
+		let mut monitored = monitored_tx_hashes.clone();
 		let tx_hash = tx.txid().as_raw_hash().to_byte_array();
-		if monitored_tx_hashes.contains(&tx_hash) {
+		if monitored.any(|&monitored_hash| monitored_hash == tx_hash) {
 			successful_witnesses.push(tx_hash);
 		}
 	}
@@ -197,19 +204,22 @@ mod tests {
 				value: 232232,
 				script_pubkey: ScriptBuf::from(vec![32, 32, 121, 9]),
 			}]),
+			fake_transaction(vec![TxOut {
+				value: 232232,
+				script_pubkey: ScriptBuf::from(vec![33, 2, 1, 9]),
+			}]),
 		];
 
-		let tx_hashes = txs
-			.iter()
-			.map(|tx| tx.txid().to_raw_hash().to_byte_array())
-			// Only watch for the first 2.
-			.take(2)
-			.collect::<Vec<_>>();
+		let tx_hashes =
+			txs.iter().map(|tx| tx.txid().to_raw_hash().to_byte_array()).collect::<Vec<_>>();
+
+		// we're not monitoring for index 2, and they're out of order.
+		let mut monitored_hashes = vec![tx_hashes[3], tx_hashes[0], tx_hashes[1]];
 
-		let success_witnesses = success_witnesses(&tx_hashes, &txs);
+		let mut success_witnesses = success_witnesses(monitored_hashes.iter(), &txs);
+		success_witnesses.sort();
+		monitored_hashes.sort();
 
-		assert_eq!(success_witnesses.len(), 2);
-		assert_eq!(success_witnesses[0], tx_hashes[0]);
-		assert_eq!(success_witnesses[1], tx_hashes[1]);
+		assert_eq!(success_witnesses, monitored_hashes);
 	}
 }
```

### engine/src/witness/common/chunked_chain_source/chunked_by_vault.rs
```diff
@@ -2,6 +2,7 @@ pub mod builder;
 pub mod continuous;
 pub mod deposit_addresses;
 pub mod egress_items;
+pub mod monitored_items;
 
 use cf_chains::Chain;
 use futures_util::StreamExt;
```

### engine/src/witness/common/chunked_chain_source/chunked_by_vault/deposit_addresses.rs
```diff
@@ -1,26 +1,14 @@
-use std::sync::Arc;
-
-use cf_chains::ChainState;
-use frame_support::CloneNoBound;
-use futures::FutureExt;
-use futures_util::{stream, StreamExt};
 use pallet_cf_ingress_egress::DepositChannelDetails;
 use state_chain_runtime::PalletInstanceAlias;
-use tokio::sync::watch;
-use utilities::{
-	loop_select,
-	task_scope::{Scope, OR_CANCEL},
-};
+use std::sync::Arc;
+use utilities::task_scope::Scope;
 
 use crate::{
 	state_chain_observer::client::{storage_api::StorageApi, StateChainStreamApi},
-	witness::common::{
-		chain_source::{ChainClient, ChainStream, Header},
-		RuntimeHasChain, STATE_CHAIN_BEHAVIOUR, STATE_CHAIN_CONNECTION,
-	},
+	witness::common::{RuntimeHasChain, STATE_CHAIN_CONNECTION},
 };
 
-use super::{builder::ChunkedByVaultBuilder, ChunkedByVault};
+use super::{builder::ChunkedByVaultBuilder, monitored_items::MonitoredSCItems, ChunkedByVault};
 
 pub type Addresses<Inner> = Vec<
 	DepositChannelDetails<
@@ -29,254 +17,6 @@ pub type Addresses<Inner> = Vec<
 	>,
 >;
 
-/// This helps ensure the set of deposit addresses witnessed at each block are consistent across
-/// every validator
-
-#[derive(Clone)]
-#[allow(clippy::type_complexity)]
-pub struct DepositAddresses<Inner: ChunkedByVault>
-where
-	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
-{
-	inner: Inner,
-	receiver: tokio::sync::watch::Receiver<(ChainState<Inner::Chain>, Addresses<Inner>)>,
-}
-impl<Inner: ChunkedByVault> DepositAddresses<Inner>
-where
-	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
-{
-	// We wait for the chain_tracking to pass a blocks height before assessing the addresses that
-	// should be witnessed at that block to ensure, the set of addresses each engine attempts to
-	// witness at a given block is consistent.
-	// We ensure the index is strictly less than the block height. This is because we need to ensure
-	// that for a particular chain state block height, no more deposit channels can be created with
-	// that opened_at block height.
-	fn is_header_ready(index: Inner::Index, chain_state: &ChainState<Inner::Chain>) -> bool {
-		index < chain_state.block_height
-	}
-
-	// FOr a given header we only witness addresses opened at or before the header, the set of
-	// addresses each engine attempts to witness at a given block is consistent
-	fn addresses_for_header(index: Inner::Index, addresses: &Addresses<Inner>) -> Addresses<Inner> {
-		addresses
-			.iter()
-			.filter(|details| details.opened_at <= index && index <= details.expires_at)
-			.cloned()
-			.collect()
-	}
-
-	async fn get_chain_state_and_addresses<StateChainClient: StorageApi + Send + Sync + 'static>(
-		state_chain_client: &StateChainClient,
-		block_hash: state_chain_runtime::Hash,
-	) -> (ChainState<Inner::Chain>, Addresses<Inner>)
-	where
-		state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
-	{
-		(
-			state_chain_client
-				.storage_value::<pallet_cf_chain_tracking::CurrentChainState<
-					state_chain_runtime::Runtime,
-					<Inner::Chain as PalletInstanceAlias>::Instance,
-				>>(block_hash)
-				.await
-				.expect(STATE_CHAIN_CONNECTION)
-				.expect(STATE_CHAIN_BEHAVIOUR),
-			state_chain_client
-				.storage_map_values::<pallet_cf_ingress_egress::DepositChannelLookup<
-					state_chain_runtime::Runtime,
-					<Inner::Chain as PalletInstanceAlias>::Instance,
-				>>(block_hash)
-				.await
-				.expect(STATE_CHAIN_CONNECTION),
-		)
-	}
-
-	pub async fn new<
-		'env,
-		StateChainStream: StateChainStreamApi<FINALIZED>,
-		StateChainClient: StorageApi + Send + Sync + 'static,
-		const FINALIZED: bool,
-	>(
-		inner: Inner,
-		scope: &Scope<'env, anyhow::Error>,
-		mut state_chain_stream: StateChainStream,
-		state_chain_client: Arc<StateChainClient>,
-	) -> Self
-	where
-		state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
-	{
-		let (sender, receiver) = watch::channel(
-			Self::get_chain_state_and_addresses(
-				&*state_chain_client,
-				state_chain_stream.cache().hash,
-			)
-			.await,
-		);
-
-		scope.spawn(async move {
-            utilities::loop_select! {
-                let _ = sender.closed() => { break Ok(()) },
-                if let Some(_block_header) = state_chain_stream.next() => {
-					// Note it is still possible for engines to inconsistently select addresses to witness for a block due to how the SC expiries deposit addresses
-                    let _result = sender.send(Self::get_chain_state_and_addresses(&*state_chain_client, state_chain_stream.cache().hash).await);
-                } else break Ok(()),
-            }
-        });
-
-		Self { inner, receiver }
-	}
-}
-#[async_trait::async_trait]
-impl<Inner: ChunkedByVault> ChunkedByVault for DepositAddresses<Inner>
-where
-	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
-{
-	type ExtraInfo = Inner::ExtraInfo;
-	type ExtraHistoricInfo = Inner::ExtraHistoricInfo;
-
-	type Index = Inner::Index;
-	type Hash = Inner::Hash;
-	type Data = (Inner::Data, Addresses<Inner>);
-
-	type Client = DepositAddressesClient<Inner>;
-
-	type Chain = Inner::Chain;
-
-	type Parameters = Inner::Parameters;
-
-	async fn stream(
-		&self,
-		parameters: Self::Parameters,
-	) -> crate::witness::common::BoxActiveAndFuture<'_, super::Item<'_, Self>> {
-		self.inner
-			.stream(parameters)
-			.await
-			.then(move |(epoch, chain_stream, chain_client)| async move {
-				struct State<Inner: ChunkedByVault> where
-				state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain> {
-					receiver:
-						tokio::sync::watch::Receiver<(ChainState<Inner::Chain>, Addresses<Inner>)>,
-					pending_headers: Vec<Header<Inner::Index, Inner::Hash, Inner::Data>>,
-					ready_headers:
-						Vec<Header<Inner::Index, Inner::Hash, (Inner::Data, Addresses<Inner>)>>,
-				}
-				impl<Inner: ChunkedByVault> State<Inner> where
-				state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain> {
-					fn add_headers<
-						It: IntoIterator<Item = Header<Inner::Index, Inner::Hash, Inner::Data>>,
-					>(
-						&mut self,
-						headers: It,
-					) {
-						let chain_state_and_addresses = self.receiver.borrow();
-						let (chain_state, addresses) = &*chain_state_and_addresses;
-						for header in headers {
-							if DepositAddresses::<Inner>::is_header_ready(
-								header.index,
-								chain_state,
-							) {
-								self.ready_headers.push(header.map_data(|header| {
-									(
-										header.data,
-										DepositAddresses::<Inner>::addresses_for_header(
-											header.index,
-											addresses,
-										),
-									)
-								}));
-							} else {
-								self.pending_headers.push(header);
-							}
-						}
-					}
-				}
-
-				(
-					epoch,
-					stream::unfold(
-						(
-							chain_stream.fuse(),
-							State::<Inner> {
-								receiver: self.receiver.clone(),
-								pending_headers: vec![],
-								ready_headers: vec![],
-							}
-						),
-						|(mut chain_stream, mut state)| async move {
-							loop_select!(
-								if !state.ready_headers.is_empty() => break Some((state.ready_headers.pop().unwrap(), (chain_stream, state))),
-								if let Some(header) = chain_stream.next() => {
-									state.add_headers(std::iter::once(header));
-								} else disable then if state.pending_headers.is_empty() => break None,
-								let _ = state.receiver.changed().map(|result| result.expect(OR_CANCEL)) => {
-									let pending_headers = std::mem::take(&mut state.pending_headers);
-									state.add_headers(pending_headers);
-								},
-							)
-						},
-					)
-					.into_box(),
-					DepositAddressesClient::new(chain_client, self.receiver.clone()),
-				)
-			})
-			.await
-			.into_box()
-	}
-}
-
-#[derive(CloneNoBound)]
-pub struct DepositAddressesClient<Inner: ChunkedByVault>
-where
-	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
-{
-	inner_client: Inner::Client,
-	receiver: tokio::sync::watch::Receiver<(ChainState<Inner::Chain>, Addresses<Inner>)>,
-}
-
-impl<Inner: ChunkedByVault> DepositAddressesClient<Inner>
-where
-	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
-{
-	pub fn new(
-		inner_client: Inner::Client,
-		receiver: tokio::sync::watch::Receiver<(ChainState<Inner::Chain>, Addresses<Inner>)>,
-	) -> Self {
-		Self { inner_client, receiver }
-	}
-}
-#[async_trait::async_trait]
-impl<Inner: ChunkedByVault> ChainClient for DepositAddressesClient<Inner>
-where
-	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
-{
-	type Index = Inner::Index;
-	type Hash = Inner::Hash;
-	type Data = (Inner::Data, Addresses<Inner>);
-
-	async fn header_at_index(
-		&self,
-		index: Self::Index,
-	) -> Header<Self::Index, Self::Hash, Self::Data> {
-		let mut receiver = self.receiver.clone();
-
-		let addresses = {
-			let chain_state_and_addresses = receiver
-				.wait_for(|(chain_state, _addresses)| {
-					DepositAddresses::<Inner>::is_header_ready(index, chain_state)
-				})
-				.await
-				.expect(OR_CANCEL);
-			let (_option_chain_state, addresses) = &*chain_state_and_addresses;
-			DepositAddresses::<Inner>::addresses_for_header(index, addresses)
-		};
-
-		self.inner_client
-			.header_at_index(index)
-			.await
-			.map_data(|header| (header.data, addresses))
-	}
-}
-
 impl<Inner: ChunkedByVault> ChunkedByVaultBuilder<Inner> {
 	pub async fn deposit_addresses<
 		'env,
@@ -288,14 +28,46 @@ impl<Inner: ChunkedByVault> ChunkedByVaultBuilder<Inner> {
 		scope: &Scope<'env, anyhow::Error>,
 		state_chain_stream: StateChainStream,
 		state_chain_client: Arc<StateChainClient>,
-	) -> ChunkedByVaultBuilder<DepositAddresses<Inner>>
+	) -> ChunkedByVaultBuilder<
+		MonitoredSCItems<
+			Inner,
+			Addresses<Inner>,
+			impl Fn(Inner::Index, &Addresses<Inner>) -> Addresses<Inner> + Send + Sync + Clone + 'static,
+		>,
+	>
 	where
 		state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
 		StateChainStream: StateChainStreamApi<FINALIZED>,
 		StateChainClient: StorageApi + Send + Sync + 'static,
 	{
+		let state_chain_client_c = state_chain_client.clone();
 		ChunkedByVaultBuilder::new(
-			DepositAddresses::new(self.source, scope, state_chain_stream, state_chain_client).await,
+			MonitoredSCItems::new(
+				self.source,
+				scope,
+				state_chain_stream,
+				state_chain_client,
+				move |block_hash| {
+					let state_chain_client = state_chain_client_c.clone();
+					async move {
+						state_chain_client
+							.storage_map_values::<pallet_cf_ingress_egress::DepositChannelLookup<
+								state_chain_runtime::Runtime,
+								<Inner::Chain as PalletInstanceAlias>::Instance,
+							>>(block_hash)
+							.await
+							.expect(STATE_CHAIN_CONNECTION)
+					}
+				},
+				|index, addresses: &Addresses<Inner>| {
+					addresses
+						.iter()
+						.filter(|details| details.opened_at <= index && index <= details.expires_at)
+						.cloned()
+						.collect()
+				},
+			)
+			.await,
 			self.parameters,
 		)
 	}
```

### engine/src/witness/common/chunked_chain_source/chunked_by_vault/egress_items.rs
```diff
@@ -1,15 +1,15 @@
 use std::sync::Arc;
 
-use crate::witness::common::chain_source::{ChainClient, ChainStream};
 use cf_chains::{Chain, ChainCrypto};
-use frame_support::CloneNoBound;
-use futures_util::{stream, StreamExt};
 use state_chain_runtime::PalletInstanceAlias;
-use utilities::{loop_select, task_scope::Scope};
+use utilities::task_scope::Scope;
 
 use crate::{
 	state_chain_observer::client::{storage_api::StorageApi, StateChainStreamApi},
-	witness::common::{chain_source::Header, RuntimeHasChain, STATE_CHAIN_CONNECTION},
+	witness::common::{
+		chunked_chain_source::chunked_by_vault::monitored_items::MonitoredSCItems, RuntimeHasChain,
+		STATE_CHAIN_CONNECTION,
+	},
 };
 
 use super::{builder::ChunkedByVaultBuilder, ChunkedByVault};
@@ -18,178 +18,65 @@ pub type TxOutId<Inner> =
 	<<<Inner as ChunkedByVault>::Chain as Chain>::ChainCrypto as ChainCrypto>::TransactionOutId;
 pub type TxOutIds<Inner> = Vec<TxOutId<Inner>>;
 
-/// This helps ensure the set of egress items witnessed at each block are consistent across
-/// every validator.
-/// The specific item monitored by each chain for determining what's an egress is different for each
-/// chain. It's based on the TransactionOutId for each chain.
-#[allow(clippy::type_complexity)]
-pub struct EgressItems<Inner: ChunkedByVault>
-where
-	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
-{
-	inner: Inner,
-	receiver: tokio::sync::watch::Receiver<TxOutIds<Inner>>,
-}
-
-impl<Inner: ChunkedByVault> EgressItems<Inner>
-where
-	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
-{
-	pub async fn get_transaction_out_ids<StateChainClient: StorageApi + Send + Sync + 'static>(
-		state_chain_client: &StateChainClient,
-		block_hash: state_chain_runtime::Hash,
-	) -> TxOutIds<Inner>
-	where
-		state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
-	{
-		state_chain_client
-			.storage_map::<pallet_cf_broadcast::TransactionOutIdToBroadcastId<
-				state_chain_runtime::Runtime,
-				<Inner::Chain as PalletInstanceAlias>::Instance,
-			>, Vec<_>>(block_hash)
-			.await
-			.expect(STATE_CHAIN_CONNECTION)
-			.into_iter()
-			.map(|(tx_out_id, _)| tx_out_id)
-			.collect()
-	}
-
-	pub async fn new<
-		'env,
-		StateChainStream: StateChainStreamApi<FINALIZED>,
-		StateChainClient: StorageApi + Send + Sync + 'static,
-		const FINALIZED: bool,
-	>(
-		inner: Inner,
-		scope: &Scope<'env, anyhow::Error>,
-		mut state_chain_stream: StateChainStream,
-		state_chain_client: Arc<StateChainClient>,
-	) -> Self {
-		let (sender, receiver) = tokio::sync::watch::channel(
-			Self::get_transaction_out_ids(&*state_chain_client, state_chain_stream.cache().hash)
-				.await,
-		);
-
-		scope.spawn(async move {
-			utilities::loop_select! {
-				let _ = sender.closed() => { break Ok(()) },
-				if let Some(block) = state_chain_stream.next() => {
-					let _result = sender.send(Self::get_transaction_out_ids(&*state_chain_client, block.hash).await);
-				} else break Ok(()),
-			}
-		});
-
-		Self { inner, receiver }
-	}
-}
+pub type ChainBlockNumber<Inner> = <<Inner as ChunkedByVault>::Chain as Chain>::ChainBlockNumber;
 
-#[derive(CloneNoBound)]
-pub struct EgressClient<Inner: ChunkedByVault>
-where
-	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
-{
-	inner_client: Inner::Client,
-	receiver: tokio::sync::watch::Receiver<TxOutIds<Inner>>,
-}
-impl<Inner: ChunkedByVault> EgressClient<Inner>
-where
-	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
-{
-	pub fn new(
-		inner_client: Inner::Client,
-		receiver: tokio::sync::watch::Receiver<TxOutIds<Inner>>,
-	) -> Self {
-		Self { inner_client, receiver }
-	}
-}
-
-#[async_trait::async_trait]
-impl<Inner: ChunkedByVault> ChunkedByVault for EgressItems<Inner>
-where
-	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
-{
-	type ExtraInfo = Inner::ExtraInfo;
-	type ExtraHistoricInfo = Inner::ExtraHistoricInfo;
-
-	type Index = Inner::Index;
-	type Hash = Inner::Hash;
-	type Data = (Inner::Data, TxOutIds<Inner>);
-
-	type Client = EgressClient<Inner>;
-
-	type Chain = Inner::Chain;
-
-	type Parameters = Inner::Parameters;
-
-	async fn stream(
-		&self,
-		parameters: Self::Parameters,
-	) -> crate::witness::common::BoxActiveAndFuture<'_, super::Item<'_, Self>> {
-		self.inner
-			.stream(parameters)
-			.await
-			.then(move |(epoch, chain_stream, chain_client)| async move {
-				(
-					epoch,
-					stream::unfold(
-						(chain_stream.fuse(), self.receiver.clone()),
-						|(mut chain_stream, receiver)| async move {
-							loop_select!(
-								if let Some(header) = chain_stream.next() => {
-									// Always get the latest tx out ids.
-									// NB: There is a race condition here. If we're not watching for a particular egress id (because our state chain is slow for some reason) at the time
-									// it arrives on external chain, we won't witness it. This is pretty unlikely since the time between the egress id being set on the SC and the tx
-									// being confirmed on the external chain is quite large. We should fix this eventually though. PRO-689
-									let tx_out_ids = receiver.borrow().clone();
-									break Some((header.map_data(|header| (header.data, tx_out_ids)), (chain_stream, receiver)))
-								} else break None,
-							)
-						},
-					)
-					.into_box(),
-					EgressClient::new(chain_client, self.receiver.clone()),
-				)
-			})
-			.await
-			.into_box()
-	}
-}
-
-#[async_trait::async_trait]
-impl<Inner: ChunkedByVault> ChainClient for EgressClient<Inner>
-where
-	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
-{
-	type Index = Inner::Index;
-	type Hash = Inner::Hash;
-	type Data = (Inner::Data, TxOutIds<Inner>);
-
-	async fn header_at_index(
-		&self,
-		index: Self::Index,
-	) -> Header<Self::Index, Self::Hash, Self::Data> {
-		let egress_items = self.receiver.borrow().clone();
-		self.inner_client
-			.header_at_index(index)
-			.await
-			.map_data(|header| (header.data, egress_items))
-	}
-}
+pub type TxOutIdsInitiatedAt<Inner> = Vec<(TxOutId<Inner>, ChainBlockNumber<Inner>)>;
 
 impl<Inner: ChunkedByVault> ChunkedByVaultBuilder<Inner> {
 	pub async fn egress_items<'env, StateChainStream, StateChainClient, const FINALIZED: bool>(
 		self,
 		scope: &Scope<'env, anyhow::Error>,
 		state_chain_stream: StateChainStream,
 		state_chain_client: Arc<StateChainClient>,
-	) -> ChunkedByVaultBuilder<EgressItems<Inner>>
+	) -> ChunkedByVaultBuilder<
+		MonitoredSCItems<
+			Inner,
+			TxOutIdsInitiatedAt<Inner>,
+			impl Fn(Inner::Index, &TxOutIdsInitiatedAt<Inner>) -> TxOutIdsInitiatedAt<Inner>
+				+ Send
+				+ Sync
+				+ Clone
+				+ 'static,
+		>,
+	>
 	where
 		state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
 		StateChainStream: StateChainStreamApi<FINALIZED>,
 		StateChainClient: StorageApi + Send + Sync + 'static,
 	{
+		let state_chain_client_c = state_chain_client.clone();
 		ChunkedByVaultBuilder::new(
-			EgressItems::new(self.source, scope, state_chain_stream, state_chain_client).await,
+			MonitoredSCItems::new(
+				self.source,
+				scope,
+				state_chain_stream,
+				state_chain_client.clone(),
+				move |block_hash| {
+					let state_chain_client = state_chain_client_c.clone();
+					async move {
+						state_chain_client
+							.storage_map::<pallet_cf_broadcast::TransactionOutIdToBroadcastId<
+								state_chain_runtime::Runtime,
+								<Inner::Chain as PalletInstanceAlias>::Instance,
+							>, Vec<_>>(block_hash)
+							.await
+							.expect(STATE_CHAIN_CONNECTION)
+							.into_iter()
+							.map(|(tx_out_id, (_broadcast_id, initiated_at))| {
+								(tx_out_id, initiated_at)
+							})
+							.collect()
+					}
+				},
+				|index, tx_out_ids: &TxOutIdsInitiatedAt<Inner>| {
+					tx_out_ids
+						.iter()
+						.filter(|(_, initiated_at)| initiated_at <= &index)
+						.cloned()
+						.collect()
+				},
+			)
+			.await,
 			self.parameters,
 		)
 	}
```

### engine/src/witness/common/chunked_chain_source/chunked_by_vault/monitored_items.rs
```diff
@@ -0,0 +1,313 @@
+use std::sync::Arc;
+
+use cf_chains::ChainState;
+use frame_support::CloneNoBound;
+use futures::{Future, FutureExt};
+use futures_util::{stream, StreamExt};
+use state_chain_runtime::PalletInstanceAlias;
+use tokio::sync::watch;
+use utilities::{
+	loop_select,
+	task_scope::{Scope, OR_CANCEL},
+};
+
+use crate::{
+	state_chain_observer::client::{storage_api::StorageApi, StateChainStreamApi},
+	witness::common::{
+		chain_source::{ChainClient, ChainStream, Header},
+		RuntimeHasChain, STATE_CHAIN_BEHAVIOUR, STATE_CHAIN_CONNECTION,
+	},
+};
+
+use super::ChunkedByVault;
+
+/// This helps ensure the set of ingress addresses witnessed at each block are consistent across
+/// every validator. We only consider a header ready when the chain tracking has passed the block.
+/// This gives the CFEs a single point to synchronise against.
+fn is_header_ready<Inner: ChunkedByVault>(
+	index: Inner::Index,
+	chain_state: &ChainState<Inner::Chain>,
+) -> bool {
+	index < chain_state.block_height
+}
+
+/// This helps ensure a set of items we want to witness are consistent for each block across all
+/// validators. Without this functionality of holding up blocks and filtering out items, the
+/// CFEs can go out of sync. Consider the case of 2 CFEs.
+/// - CFE A is ahead of CFE B with respect to external chain X by 1 block.
+/// - CFE B witnesses block 10 of X, and is watching for addresses that it fetches from the SC, at
+///   SC block 50.
+/// - CFE A witnesses block 11 of X, and is watching for addresses that it fetches from the SC, at
+///   the same SC block 50.
+/// - The SC progresses to block 51, revealing that an address is to be witnessed.
+/// - There is a deposit at block 10 of X, which CFE B witnesses, but CFE A does not.
+/// If CFE A does not wait until the block is ready to process it can miss witnesses and be out
+/// of sync with the other CFEs.
+#[derive(Clone)]
+#[allow(clippy::type_complexity)]
+pub struct MonitoredSCItems<Inner: ChunkedByVault, MonitoredItems, ItemFilter>
+where
+	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
+	MonitoredItems: Send + Sync + 'static,
+	ItemFilter: Fn(Inner::Index, &MonitoredItems) -> MonitoredItems + Send + Sync + Clone + 'static,
+{
+	inner: Inner,
+	receiver: tokio::sync::watch::Receiver<(ChainState<Inner::Chain>, MonitoredItems)>,
+	filter_fn: ItemFilter,
+}
+
+impl<Inner: ChunkedByVault, MonitoredItems, ItemFilter>
+	MonitoredSCItems<Inner, MonitoredItems, ItemFilter>
+where
+	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
+	MonitoredItems: Send + Sync + 'static,
+	ItemFilter: Fn(Inner::Index, &MonitoredItems) -> MonitoredItems + Send + Sync + Clone + 'static,
+{
+	async fn get_chain_state_and_items<
+		StateChainClient: StorageApi + Send + Sync + 'static,
+		GetItemsFut,
+		GetItemsGenerator,
+	>(
+		state_chain_client: &StateChainClient,
+		block_hash: state_chain_runtime::Hash,
+		get_items: &GetItemsGenerator,
+	) -> (ChainState<Inner::Chain>, MonitoredItems)
+	where
+		state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
+		GetItemsFut: Future<Output = MonitoredItems> + Send + 'static,
+		GetItemsGenerator:
+			Fn(state_chain_runtime::Hash) -> GetItemsFut + Send + Sync + Clone + 'static,
+	{
+		(
+			state_chain_client
+				.storage_value::<pallet_cf_chain_tracking::CurrentChainState<
+					state_chain_runtime::Runtime,
+					<Inner::Chain as PalletInstanceAlias>::Instance,
+				>>(block_hash)
+				.await
+				.expect(STATE_CHAIN_CONNECTION)
+				.expect(STATE_CHAIN_BEHAVIOUR),
+			get_items(block_hash).await,
+		)
+	}
+
+	pub async fn new<
+		'env,
+		StateChainStream: StateChainStreamApi<FINALIZED>,
+		StateChainClient: StorageApi + Send + Sync + 'static,
+		GetItemsFut: Future<Output = MonitoredItems> + Send + 'static,
+		GetItemsGenerator: Fn(state_chain_runtime::Hash) -> GetItemsFut + Send + Sync + Clone + 'static,
+		const FINALIZED: bool,
+	>(
+		inner: Inner,
+		scope: &Scope<'env, anyhow::Error>,
+		mut state_chain_stream: StateChainStream,
+		state_chain_client: Arc<StateChainClient>,
+		get_items: GetItemsGenerator,
+		filter_fn: ItemFilter,
+	) -> Self
+	where
+		state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
+	{
+		let (sender, receiver) = watch::channel(
+			Self::get_chain_state_and_items(
+				&*state_chain_client,
+				state_chain_stream.cache().hash,
+				&get_items,
+			)
+			.await,
+		);
+
+		scope.spawn(async move {
+			utilities::loop_select! {
+				let _ = sender.closed() => { break Ok(()) },
+				if let Some(_block_header) = state_chain_stream.next() => {
+					// Note it is still possible for engines to inconsistently select addresses to witness for a
+					// block due to how the SC expiries deposit addresses
+				let _result = sender.send(Self::get_chain_state_and_items(&*state_chain_client, state_chain_stream.cache().hash, &get_items).await);
+				} else break Ok(()),
+			}
+		});
+
+		Self { inner, receiver, filter_fn }
+	}
+}
+#[async_trait::async_trait]
+impl<Inner: ChunkedByVault, MonitoredItems, ItemFilter> ChunkedByVault
+	for MonitoredSCItems<Inner, MonitoredItems, ItemFilter>
+where
+	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
+	MonitoredItems: Send + Sync + Unpin + 'static,
+	ItemFilter: Fn(Inner::Index, &MonitoredItems) -> MonitoredItems + Send + Sync + Clone + 'static,
+{
+	type ExtraInfo = Inner::ExtraInfo;
+	type ExtraHistoricInfo = Inner::ExtraHistoricInfo;
+
+	type Index = Inner::Index;
+	type Hash = Inner::Hash;
+
+	type Data = (Inner::Data, MonitoredItems);
+
+	type Client = MonitoredSCItemsClient<Inner, MonitoredItems, ItemFilter>;
+
+	type Chain = Inner::Chain;
+
+	type Parameters = Inner::Parameters;
+
+	async fn stream(
+		&self,
+		parameters: Self::Parameters,
+	) -> crate::witness::common::BoxActiveAndFuture<'_, super::Item<'_, Self>> {
+		self.inner
+			.stream(parameters)
+			.await
+			.then(move |(epoch, chain_stream, chain_client)| async move {
+				struct State<Inner: ChunkedByVault, MonitoredItems, ItemFilter>
+				where
+					state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
+					MonitoredItems: Send + Sync + 'static,
+					ItemFilter: Fn(Inner::Index, &MonitoredItems) -> MonitoredItems
+						+ Send
+						+ Sync
+						+ Clone
+						+ 'static,
+				{
+					receiver:
+						tokio::sync::watch::Receiver<(ChainState<Inner::Chain>, MonitoredItems)>,
+					pending_headers: Vec<Header<Inner::Index, Inner::Hash, Inner::Data>>,
+					ready_headers:
+						Vec<Header<Inner::Index, Inner::Hash, (Inner::Data, MonitoredItems)>>,
+					filter_fn: ItemFilter,
+				}
+				impl<Inner: ChunkedByVault, MonitoredItems, ItemFilter> State<Inner, MonitoredItems, ItemFilter>
+				where
+					state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
+					MonitoredItems: Send + Sync + 'static,
+					ItemFilter: Fn(Inner::Index, &MonitoredItems) -> MonitoredItems
+						+ Send
+						+ Sync
+						+ Clone
+						+ 'static,
+				{
+					fn add_headers<
+						It: IntoIterator<Item = Header<Inner::Index, Inner::Hash, Inner::Data>>,
+					>(
+						&mut self,
+						headers: It,
+					) {
+						let chain_state_and_addresses = self.receiver.borrow();
+						let (chain_state, addresses) = &*chain_state_and_addresses;
+						for header in headers {
+							if is_header_ready::<Inner>(header.index, chain_state) {
+								// We're saying the block itself is ready. But the items within that header may not be required.
+								// Consider the cases:
+								// 1. An item in the header has expired. Its expiry block is after the current block.
+								// 2. An item in the header has an initiation/starting block after the current block.
+								self.ready_headers.push(header.map_data(|header| {
+									(header.data, (self.filter_fn)(header.index, addresses))
+								}));
+							} else {
+								self.pending_headers.push(header);
+							}
+						}
+					}
+				}
+
+				(
+					epoch,
+					stream::unfold(
+						(
+							chain_stream.fuse(),
+							State::<Inner, MonitoredItems, ItemFilter> {
+								receiver: self.receiver.clone(),
+								pending_headers: vec![],
+								ready_headers: vec![],
+								filter_fn: self.filter_fn.clone(),
+							},
+						),
+						|(mut chain_stream, mut state)| async move {
+							loop_select!(
+								if !state.ready_headers.is_empty() => break Some((state.ready_headers.pop().unwrap(), (chain_stream, state))),
+								if let Some(header) = chain_stream.next() => {
+									state.add_headers(std::iter::once(header));
+								} else disable then if state.pending_headers.is_empty() => break None,
+								let _ = state.receiver.changed().map(|result| result.expect(OR_CANCEL)) => {
+									// Headers we weren't yet ready to process might be ready now if the chain tracking has progressed.
+									let pending_headers = std::mem::take(&mut state.pending_headers);
+									state.add_headers(pending_headers);
+								},
+							)
+						},
+					)
+					.into_box(),
+					MonitoredSCItemsClient::new(
+						chain_client,
+						self.receiver.clone(),
+						(self.filter_fn).clone(),
+					),
+				)
+			})
+			.await
+			.into_box()
+	}
+}
+
+#[derive(CloneNoBound)]
+pub struct MonitoredSCItemsClient<Inner: ChunkedByVault, MonitoredItems, ItemFilter>
+where
+	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
+	ItemFilter: Fn(Inner::Index, &MonitoredItems) -> MonitoredItems + Send + Sync + Clone + 'static,
+{
+	inner_client: Inner::Client,
+	receiver: tokio::sync::watch::Receiver<(ChainState<Inner::Chain>, MonitoredItems)>,
+	filter_fn: ItemFilter,
+}
+
+impl<Inner: ChunkedByVault, MonitoredItems, ItemFilter>
+	MonitoredSCItemsClient<Inner, MonitoredItems, ItemFilter>
+where
+	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
+	ItemFilter: Fn(Inner::Index, &MonitoredItems) -> MonitoredItems + Send + Sync + Clone + 'static,
+{
+	pub fn new(
+		inner_client: Inner::Client,
+		receiver: tokio::sync::watch::Receiver<(ChainState<Inner::Chain>, MonitoredItems)>,
+		filter_fn: ItemFilter,
+	) -> Self {
+		Self { inner_client, receiver, filter_fn }
+	}
+}
+#[async_trait::async_trait]
+impl<Inner: ChunkedByVault, MonitoredItems, ItemFilter> ChainClient
+	for MonitoredSCItemsClient<Inner, MonitoredItems, ItemFilter>
+where
+	state_chain_runtime::Runtime: RuntimeHasChain<Inner::Chain>,
+	MonitoredItems: Send + Sync + Unpin + 'static,
+	ItemFilter: Fn(Inner::Index, &MonitoredItems) -> MonitoredItems + Send + Sync + Clone + 'static,
+{
+	type Index = Inner::Index;
+	type Hash = Inner::Hash;
+	type Data = (Inner::Data, MonitoredItems);
+
+	async fn header_at_index(
+		&self,
+		index: Self::Index,
+	) -> Header<Self::Index, Self::Hash, Self::Data> {
+		let mut receiver = self.receiver.clone();
+
+		let addresses = {
+			let chain_state_and_addresses = receiver
+				.wait_for(|(chain_state, _addresses)| is_header_ready::<Inner>(index, chain_state))
+				.await
+				.expect(OR_CANCEL);
+			let (_option_chain_state, addresses) = &*chain_state_and_addresses;
+
+			(self.filter_fn)(index, addresses)
+		};
+
+		self.inner_client
+			.header_at_index(index)
+			.await
+			.map_data(|header| (header.data, addresses))
+	}
+}
```

### engine/src/witness/dot.rs
```diff
@@ -108,7 +108,10 @@ pub async fn process_egress<ProcessCall, ProcessingFut>(
 	header: Header<
 		PolkadotBlockNumber,
 		PolkadotHash,
-		((Vec<(Phase, EventWrapper)>, BTreeSet<u32>), Vec<PolkadotSignature>),
+		(
+			(Vec<(Phase, EventWrapper)>, BTreeSet<u32>),
+			Vec<(PolkadotSignature, PolkadotBlockNumber)>,
+		),
 	>,
 	process_call: ProcessCall,
 	dot_client: DotRetryRpcClient,
@@ -120,7 +123,12 @@ pub async fn process_egress<ProcessCall, ProcessingFut>(
 		+ 'static,
 	ProcessingFut: Future<Output = ()> + Send + 'static,
 {
-	let ((events, mut extrinsic_indices), monitored_egress_ids) = header.data;
+	let ((events, mut extrinsic_indices), monitored_egress_data) = header.data;
+
+	let monitored_egress_ids = monitored_egress_data
+		.into_iter()
+		.map(|(signature, _)| signature)
+		.collect::<BTreeSet<_>>();
 
 	// To guarantee witnessing egress, we are interested in all extrinsics that were successful
 	extrinsic_indices.extend(extrinsic_success_indices(&events));
```
