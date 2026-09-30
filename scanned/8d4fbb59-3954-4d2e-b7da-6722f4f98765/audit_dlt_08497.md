# [?] Fix Asset Hub collator crashing when starting from genesis (#1788)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2023-10-09
Source: https://github.com/paritytech/polkadot-sdk/commit/98286ade0b5e8edf1521078c454404c7afaab438
Type: security-commit

## Details
Fix Asset Hub collator crashing when starting from genesis (#1788)

## Patch
### cumulus/polkadot-parachain/src/command.rs
```diff
@@ -836,21 +836,21 @@ pub fn run() -> Result<()> {
 				info!("Is collating: {}", if config.role.is_authority() { "yes" } else { "no" });
 
 				match config.chain_spec.runtime() {
-					Runtime::AssetHubPolkadot => crate::service::start_generic_aura_node::<
+					Runtime::AssetHubPolkadot => crate::service::start_asset_hub_node::<
 						asset_hub_polkadot_runtime::RuntimeApi,
 						AssetHubPolkadotAuraId,
 					>(config, polkadot_config, collator_options, id, hwbench)
 					.await
 					.map(|r| r.0)
 					.map_err(Into::into),
-					Runtime::AssetHubKusama => crate::service::start_generic_aura_node::<
+					Runtime::AssetHubKusama => crate::service::start_asset_hub_node::<
 						asset_hub_kusama_runtime::RuntimeApi,
 						AuraId,
 					>(config, polkadot_config, collator_options, id, hwbench)
 					.await
 					.map(|r| r.0)
 					.map_err(Into::into),
-					Runtime::AssetHubWestend => crate::service::start_generic_aura_node::<
+					Runtime::AssetHubWestend => crate::service::start_asset_hub_node::<
 						asset_hub_westend_runtime::RuntimeApi,
 						AuraId,
 					>(config, polkadot_config, collator_options, id, hwbench)
```

### cumulus/polkadot-parachain/src/service.rs
```diff
@@ -14,7 +14,7 @@
 // You should have received a copy of the GNU General Public License
 // along with Cumulus.  If not, see <http://www.gnu.org/licenses/>.
 
-use codec::Codec;
+use codec::{Codec, Decode};
 use cumulus_client_cli::CollatorOptions;
 use cumulus_client_collator::service::CollatorService;
 use cumulus_client_consensus_aura::collators::{
@@ -44,7 +44,7 @@ use crate::rpc;
 pub use parachains_common::{AccountId, Balance, Block, BlockNumber, Hash, Header, Nonce};
 
 use cumulus_client_consensus_relay_chain::Verifier as RelayChainVerifier;
-use futures::lock::Mutex;
+use futures::{lock::Mutex, prelude::*};
 use sc_consensus::{
 	import_queue::{BasicQueue, Verifier as VerifierT},
 	BlockImportParams, ImportQueue,
@@ -54,10 +54,14 @@ use sc_network::{config::FullNetworkConfiguration, NetworkBlock};
 use sc_network_sync::SyncingService;
 use sc_service::{Configuration, PartialComponents, TFullBackend, TFullClient, TaskManager};
 use sc_telemetry::{Telemetry, TelemetryHandle, TelemetryWorker, TelemetryWorkerHandle};
-use sp_api::{ApiExt, ConstructRuntimeApi};
+use sp_api::{ApiExt, ConstructRuntimeApi, ProvideRuntimeApi};
 use sp_consensus_aura::AuraApi;
+use sp_core::traits::SpawnEssentialNamed;
 use sp_keystore::KeystorePtr;
-use sp_runtime::{app_crypto::AppCrypto, traits::Header as HeaderT};
+use sp_runtime::{
+	app_crypto::AppCrypto,
+	traits::{Block as BlockT, Header as HeaderT},
+};
 use std::{marker::PhantomData, sync::Arc, time::Duration};
 use substrate_prometheus_endpoint::Registry;
 
@@ -1389,6 +1393,149 @@ where
 	.await
 }
 
+/// Start a shell node which should later transition into an Aura powered parachain node. Asset Hub
+/// uses this because at genesis, Asset Hub was on the `shell` runtime which didn't have Aura and
+/// needs to sync and upgrade before it can run `AuraApi` functions.
+pub async fn start_asset_hub_node<RuntimeApi, AuraId: AppCrypto + Send + Codec + Sync>(
+	parachain_config: Configuration,
+	polkadot_config: Configuration,
+	collator_options: CollatorOptions,
+	para_id: ParaId,
+	hwbench: Option<sc_sysinfo::HwBench>,
+) -> sc_service::error::Result<(TaskManager, Arc<ParachainClient<RuntimeApi>>)>
+where
+	RuntimeApi: ConstructRuntimeApi<Block, ParachainClient<RuntimeApi>> + Send + Sync + 'static,
+	RuntimeApi::RuntimeApi: sp_transaction_pool::runtime_api::TaggedTransactionQueue<Block>
+		+ sp_api::Metadata<Block>
+		+ sp_session::SessionKeys<Block>
+		+ sp_api::ApiExt<Block>
+		+ sp_offchain::OffchainWorkerApi<Block>
+		+ sp_block_builder::BlockBuilder<Block>
+		+ cumulus_primitives_core::CollectCollationInfo<Block>
+		+ sp_consensus_aura::AuraApi<Block, <<AuraId as AppCrypto>::Pair as Pair>::Public>
+		+ pallet_transaction_payment_rpc::TransactionPaymentRuntimeApi<Block, Balance>
+		+ frame_rpc_system::AccountNonceApi<Block, AccountId, Nonce>,
+	<<AuraId as AppCrypto>::Pair as Pair>::Signature:
+		TryFrom<Vec<u8>> + std::hash::Hash + sp_runtime::traits::Member + Codec,
+{
+	start_node_impl::<RuntimeApi, _, _, _>(
+		parachain_config,
+		polkadot_config,
+		collator_options,
+		CollatorSybilResistance::Resistant, // Aura
+		para_id,
+		|_| Ok(RpcModule::new(())),
+		aura_build_import_queue::<_, AuraId>,
+		|client,
+		 block_import,
+		 prometheus_registry,
+		 telemetry,
+		 task_manager,
+		 relay_chain_interface,
+		 transaction_pool,
+		 sync_oracle,
+		 keystore,
+		 relay_chain_slot_duration,
+		 para_id,
+		 collator_key,
+		 overseer_handle,
+		 announce_block| {
+			let relay_chain_interface2 = relay_chain_interface.clone();
+
+			let collator_service = CollatorService::new(
+				client.clone(),
+				Arc::new(task_manager.spawn_handle()),
+				announce_block,
+				client.clone(),
+			);
+
+			let spawner = task_manager.spawn_handle();
+
+			let proposer_factory = sc_basic_authorship::ProposerFactory::with_proof_recording(
+				spawner,
+				client.clone(),
+				transaction_pool,
+				prometheus_registry,
+				telemetry.clone(),
+			);
+
+			let collation_future = Box::pin(async move {
+				// Start collating with the `shell` runtime while waiting for an upgrade to an Aura
+				// compatible runtime.
+				let mut request_stream = cumulus_client_collator::relay_chain_driven::init(
+					collator_key.clone(),
+					para_id,
+					overseer_handle.clone(),
+				)
+				.await;
+				while let Some(request) = request_stream.next().await {
+					let pvd = request.persisted_validation_data().clone();
+					let last_head_hash =
+						match <Block as BlockT>::Header::decode(&mut &pvd.parent_head.0[..]) {
+							Ok(header) => header.hash(),
+							Err(e) => {
+								log::error!("Could not decode the head data: {e}");
+								request.complete(None);
+								continue
+							},
+						};
+
+					// Check if we have upgraded to an Aura compatible runtime and transition if
+					// necessary.
+					if client
+						.runtime_api()
+						.has_api::<dyn AuraApi<Block, AuraId>>(last_head_hash)
+						.unwrap_or(false)
+					{
+						// Respond to this request before transitioning to Aura.
+						request.complete(None);
+						break
+					}
+				}
+
+				// Move to Aura consensus.
+				let slot_duration = match cumulus_client_consensus_aura::slot_duration(&*client) {
+					Ok(d) => d,
+					Err(e) => {
+						log::error!("Could not get Aura slot duration: {e}");
+						return
+					},
+				};
+
+				let proposer = Proposer::new(proposer_factory);
+
+				let params = BasicAuraParams {
+					create_inherent_data_providers: move |_, ()| async move { Ok(()) },
+					block_import,
+					para_client: client,
+					relay_client: relay_chain_interface2,
+					sync_oracle,
+					keystore,
+					collator_key,
+					para_id,
+					overseer_handle,
+					slot_duration,
+					relay_chain_slot_duration,
+					proposer,
+					collator_service,
+					// Very limited proposal time.
+					authoring_duration: Duration::from_millis(500),
+				};
+
+				basic_aura::run::<Block, <AuraId as AppCrypto>::Pair, _, _, _, _, _, _, _>(params)
+					.await
+			});
+
+			let spawner = task_manager.spawn_essential_handle();
+			spawner.spawn_essential("cumulus-asset-hub-collator", None, collation_future);
+
+			Ok(())
+		},
+		hwbench,
+	)
+	.await
+}
+
 /// Start an aura powered parachain node which uses the lookahead collator to support async backing.
 /// This node is basic in the sense that its runtime api doesn't include common contents such as
 /// transaction payment. Used for aura glutton.
```
