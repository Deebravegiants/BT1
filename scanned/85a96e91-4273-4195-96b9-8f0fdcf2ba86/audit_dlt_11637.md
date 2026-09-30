# [?] Fix `eth_getTransactionReceipt` race condition (#1802)

## Summary
Severity: Unknown
Chain: Polkadot
Component: polkadot-evm/frontier
Published: 2026-02-03
Source: https://github.com/polkadot-evm/frontier/commit/f90139d16af16ba9cf8646cae88be7824610c185
Type: security-commit

## Details
Fix `eth_getTransactionReceipt` race condition (#1802)

* test: :test_tube: add TDD failing test

* refactor: :recycle: use mapping-sync as single source of truth for eth_ RPCs

* fix: :bug: fix missing args

* test: :white_check_mark: redefine waitForBlock as a polling function

* style: :art: fmt

* fix: :bug: wait for the right block number

* revert: :fire: remove temporary delay

* chore: :package: update package lock

* test: :white_check_mark: update test timeouts

* test: :white_check_mark: remove explicit nonce to fix EIP-7702 test race condition

* fix: bypass ethers.js nonce caching in EIP-7702 tests

ethers.js v6 caches eth_getTransactionCount responses at the provider
level. When multiple tests run sequentially using the same signer,
subsequent tests may receive stale cached nonces instead of making
fresh RPC calls.

This fixes the "nonce has already been used" test failures by:
- Using direct RPC calls (context.ethersjs.send) to bypass caching
- Explicitly setting nonces in transactions to ensure correctness

The backend changes to latest_block_hash() use mapping-sync as the
source of truth for consistency with other RPCs. When the best block
isn't indexed yet, it falls back to the latest indexed block.

* fix: :bug: verify mapped blocks against canonical chain during reorgs

* revert: :fire: remove LATEST_INDEXED_BLOCK

* fix: :bug: correctly error instead of defaulting to block number 0

* fix: :bug: verify all non-genesis blocks

* test: :white_check_mark: add error handling to waitForBlock

* fix: :bug: use consistent behavior for eth_getBlockByNumber("latest") on SQL backend

* feat: :sparkles: add KV store migration

* fix: :bug: do not default to 0

* feat: :loud_sound: log processed entries in parity db migration

## Patch
### client/api/src/backend.rs
```diff
@@ -39,6 +39,9 @@ pub trait Backend<Block: BlockT>: Send + Sync {
 		ethereum_block_hash: &H256,
 	) -> Result<Option<Vec<Block::Hash>>, String>;
 
+	/// Get the ethereum block hash for a given block number.
+	async fn block_hash_by_number(&self, block_number: u64) -> Result<Option<H256>, String>;
+
 	/// Get the transaction metadata with the given ethereum block hash.
 	async fn transaction_metadata(
 		&self,
```

### client/cli/src/frontier_db_cmd/mapping_db.rs
```diff
@@ -23,7 +23,7 @@ use serde::Deserialize;
 // Substrate
 use sp_api::ProvideRuntimeApi;
 use sp_blockchain::HeaderBackend;
-use sp_runtime::traits::Block as BlockT;
+use sp_runtime::traits::{Block as BlockT, Header as HeaderT, UniqueSaturatedInto};
 // Frontier
 use fp_rpc::EthereumRuntimeRPCApi;
 
@@ -103,7 +103,20 @@ where
 							ethereum_transaction_hashes: existing_transaction_hashes,
 						};
 
-						self.backend.mapping().write_hashes(commitment)?;
+						// Get block number from header
+						let block_number: u64 = (*self
+							.client
+							.header(*substrate_block_hash)
+							.map_err(|e| format!("{e:?}"))?
+							.ok_or_else(|| {
+								format!("Header not found for block {substrate_block_hash:?}")
+							})?
+							.number())
+						.unique_saturated_into();
+
+						self.backend
+							.mapping()
+							.write_hashes(commitment, block_number)?;
 					} else {
 						return Err(self.key_not_empty_error(key));
 					}
@@ -161,7 +174,20 @@ where
 							ethereum_transaction_hashes: existing_transaction_hashes,
 						};
 
-						self.backend.mapping().write_hashes(commitment)?;
+						// Get block number from header
+						let block_number: u64 = (*self
+							.client
+							.header(*substrate_block_hash)
+							.map_err(|e| format!("{e:?}"))?
+							.ok_or_else(|| {
+								format!("Header not found for block {substrate_block_hash:?}")
+							})?
+							.number())
+						.unique_saturated_into();
+
+						self.backend
+							.mapping()
+							.write_hashes(commitment, block_number)?;
 					}
 				}
 				_ => return Err(self.key_value_error(key, value)),
```

### client/db/src/kv/mod.rs
```diff
@@ -33,7 +33,7 @@ pub use sc_client_db::DatabaseSource;
 use sp_blockchain::HeaderBackend;
 use sp_core::{H160, H256};
 pub use sp_database::Database;
-use sp_runtime::traits::Block as BlockT;
+use sp_runtime::traits::{Block as BlockT, UniqueSaturatedInto};
 // Frontier
 use fc_api::{FilteredLog, TransactionMetadata};
 use fp_storage::{EthereumStorageSchema, PALLET_ETHEREUM_SCHEMA_CACHE};
@@ -49,12 +49,13 @@ pub struct DatabaseSettings {
 }
 
 pub(crate) mod columns {
-	pub const NUM_COLUMNS: u32 = 4;
+	pub const NUM_COLUMNS: u32 = 5;
 
 	pub const META: u32 = 0;
 	pub const BLOCK_MAPPING: u32 = 1;
 	pub const TRANSACTION_MAPPING: u32 = 2;
 	pub const SYNCED_MAPPING: u32 = 3;
+	pub const BLOCK_NUMBER_MAPPING: u32 = 4;
 }
 
 pub mod static_keys {
@@ -78,6 +79,10 @@ impl<Block: BlockT, C: HeaderBackend<Block>> fc_api::Backend<Block> for Backend<
 		self.mapping().block_hash(ethereum_block_hash)
 	}
 
+	async fn block_hash_by_number(&self, block_number: u64) -> Result<Option<H256>, String> {
+		self.mapping().block_hash_by_number(block_number)
+	}
+
 	async fn transaction_metadata(
 		&self,
 		ethereum_transaction_hash: &H256,
@@ -95,7 +100,39 @@ impl<Block: BlockT, C: HeaderBackend<Block>> fc_api::Backend<Block> for Backend<
 	}
 
 	async fn latest_block_hash(&self) -> Result<Block::Hash, String> {
-		Ok(self.client.info().best_hash)
+		// Return the latest block hash that is both indexed AND on the canonical chain.
+		// This prevents returning stale data during reorgs.
+		//
+		// Note: During initial sync or after restart while mapping-sync catches up,
+		// this returns the genesis block hash. This is consistent with Geth's behavior
+		// where eth_getBlockByNumber("latest") returns block 0 during initial sync.
+		// Users can check sync status via eth_syncing to determine if the node is
+		// still catching up.
+		let best_number: u64 = self.client.info().best_number.unique_saturated_into();
+
+		// Get the canonical hash for verification.
+		let canonical_hash = self
+			.client
+			.hash(best_number.unique_saturated_into())
+			.map_err(|e| format!("{e:?}"))?;
+
+		// Query mapping-sync for the ethereum block hash at best_number
+		if let Some(eth_hash) = self.mapping.block_hash_by_number(best_number)? {
+			// Get the substrate block hash(es) for this ethereum block hash
+			if let Some(substrate_hashes) = self.mapping.block_hash(&eth_hash)? {
+				// Verify the mapped hash is on the canonical chain.
+				// During a reorg, the mapping may point to a reorged-out block.
+				if let Some(canonical) = canonical_hash {
+					if substrate_hashes.contains(&canonical) {
+						return Ok(canonical);
+					}
+				}
+				// Mapping exists but is stale (reorg happened) - treat as not indexed
+			}
+		}
+
+		// Block not indexed yet or stale - return genesis
+		Ok(self.client.info().genesis_hash)
 	}
 }
 
@@ -310,7 +347,11 @@ impl<Block: BlockT> MappingDb<Block> {
 		Ok(())
 	}
 
-	pub fn write_hashes(&self, commitment: MappingCommitment<Block>) -> Result<(), String> {
+	pub fn write_hashes(
+		&self,
+		commitment: MappingCommitment<Block>,
+		block_number: u64,
+	) -> Result<(), String> {
 		let _lock = self.write_lock.lock();
 
 		let mut transaction = sp_database::Transaction::new();
@@ -337,6 +378,13 @@ impl<Block: BlockT> MappingDb<Block> {
 			&substrate_hashes.encode(),
 		);
 
+		// Write block number -> ethereum block hash mapping
+		transaction.set(
+			columns::BLOCK_NUMBER_MAPPING,
+			&block_number.encode(),
+			&commitment.ethereum_block_hash.encode(),
+		);
+
 		for (i, ethereum_transaction_hash) in commitment
 			.ethereum_transaction_hashes
 			.into_iter()
@@ -365,4 +413,16 @@ impl<Block: BlockT> MappingDb<Block> {
 
 		Ok(())
 	}
+
+	pub fn block_hash_by_number(&self, block_number: u64) -> Result<Option<H256>, String> {
+		match self
+			.db
+			.get(columns::BLOCK_NUMBER_MAPPING, &block_number.encode())
+		{
+			Some(raw) => Ok(Some(
+				H256::decode(&mut &raw[..]).map_err(|e| format!("{e:?}"))?,
+			)),
+			None => Ok(None),
+		}
+	}
 }
```

### client/db/src/kv/upgrade.rs
```diff
@@ -34,11 +34,12 @@ use sp_runtime::traits::Block as BlockT;
 const VERSION_FILE_NAME: &str = "db_version";
 
 /// Current db version.
-const CURRENT_VERSION: u32 = 2;
+const CURRENT_VERSION: u32 = 3;
 
 /// Number of columns in each version.
 const _V1_NUM_COLUMNS: u32 = 4;
-const V2_NUM_COLUMNS: u32 = 4;
+const _V2_NUM_COLUMNS: u32 = 4;
+const V3_NUM_COLUMNS: u32 = 5;
 
 /// Database upgrade errors.
 #[derive(Debug)]
@@ -60,6 +61,11 @@ pub(crate) struct UpgradeVersion1To2Summary {
 	pub error: Vec<H256>,
 }
 
+pub(crate) struct UpgradeVersion2To3Summary {
+	pub success: u32,
+	pub skipped: u32,
+}
+
 impl From<io::Error> for UpgradeError {
 	fn from(err: io::Error) -> Self {
 		UpgradeError::Io(err)
@@ -95,30 +101,57 @@ pub(crate) fn upgrade_db<Block: BlockT, C: HeaderBackend<Block>>(
 	db_path: &Path,
 	source: &DatabaseSource,
 ) -> UpgradeResult<()> {
-	let db_version = current_version(db_path)?;
-	match db_version {
-		0 => return Err(UpgradeError::UnsupportedVersion(db_version)),
-		1 => {
-			let summary: UpgradeVersion1To2Summary = match source {
-				DatabaseSource::ParityDb { .. } => {
-					migrate_1_to_2_parity_db::<Block, C>(client, db_path)?
-				}
-				#[cfg(feature = "rocksdb")]
-				DatabaseSource::RocksDb { .. } => migrate_1_to_2_rocks_db::<Block, C>(client, db_path)?,
-				_ => panic!("DatabaseSource required for upgrade ParityDb | RocksDb"),
-			};
-			if !summary.error.is_empty() {
-				panic!(
-					"Inconsistent migration from version 1 to 2. Failed on {:?}",
-					summary.error
-				);
-			} else {
-				log::info!("✔️ Successful Frontier DB migration from version 1 to version 2 ({:?} entries).", summary.success);
+	let mut db_version = current_version(db_path)?;
+	if db_version == 0 {
+		return Err(UpgradeError::UnsupportedVersion(db_version));
+	}
+
+	// Version 1 -> 2: Migrate block mapping from One-to-one to One-to-many
+	if db_version == 1 {
+		let summary: UpgradeVersion1To2Summary = match source {
+			DatabaseSource::ParityDb { .. } => {
+				migrate_1_to_2_parity_db::<Block, C>(client.clone(), db_path)?
 			}
+			#[cfg(feature = "rocksdb")]
+			DatabaseSource::RocksDb { .. } => migrate_1_to_2_rocks_db::<Block, C>(client.clone(), db_path)?,
+			_ => panic!("DatabaseSource required for upgrade ParityDb | RocksDb"),
+		};
+		if !summary.error.is_empty() {
+			panic!(
+				"Inconsistent migration from version 1 to 2. Failed on {:?}",
+				summary.error
+			);
+		} else {
+			log::info!(
+				"✔️ Successful Frontier DB migration from version 1 to version 2 ({:?} entries).",
+				summary.success
+			);
 		}
-		CURRENT_VERSION => (),
-		_ => return Err(UpgradeError::FutureDatabaseVersion(db_version)),
+		db_version = 2;
+	}
+
+	// Version 2 -> 3: Backfill block_number -> ethereum_block_hash mapping
+	if db_version == 2 {
+		let summary: UpgradeVersion2To3Summary = match source {
+			DatabaseSource::ParityDb { .. } => {
+				migrate_2_to_3_parity_db::<Block, C>(client.clone(), db_path)?
+			}
+			#[cfg(feature = "rocksdb")]
+			DatabaseSource::RocksDb { .. } => migrate_2_to_3_rocks_db::<Block, C>(client.clone(), db_path)?,
+			_ => panic!("DatabaseSource required for upgrade ParityDb | RocksDb"),
+		};
+		log::info!(
+			"✔️ Successful Frontier DB migration from version 2 to version 3 ({} entries migrated, {} skipped).",
+			summary.success,
+			summary.skipped
+		);
+		db_version = 3;
 	}
+
+	if db_version != CURRENT_VERSION {
+		return Err(UpgradeError::FutureDatabaseVersion(db_version));
+	}
+
 	update_version(db_path)?;
 	Ok(())
 }
@@ -220,7 +253,9 @@ pub(crate) fn migrate_1_to_2_rocks_db<Block: BlockT, C: HeaderBackend<Block>>(
 		Ok(())
 	};
 
-	let db_cfg = kvdb_rocksdb::DatabaseConfig::with_columns(V2_NUM_COLUMNS);
+	// Open with V3_NUM_COLUMNS to handle both v1 DBs (will create missing columns)
+	// and test DBs that were created with 5 columns.
+	let db_cfg = kvdb_rocksdb::DatabaseConfig::with_columns(V3_NUM_COLUMNS);
 	let db = kvdb_rocksdb::Database::open(&db_cfg, db_path)?;
 
 	// Get all the block hashes we need to update
@@ -292,7 +327,9 @@ pub(crate) fn migrate_1_to_2_parity_db<Block: BlockT, C: HeaderBackend<Block>>(
 		Ok(())
 	};
 
-	let mut db_cfg = parity_db::Options::with_columns(db_path, V2_NUM_COLUMNS as u8);
+	// Open with V3_NUM_COLUMNS to handle both v1 DBs (will create missing columns)
+	// and test DBs that were created with 5 columns.
+	let mut db_cfg = parity_db::Options::with_columns(db_path, V3_NUM_COLUMNS as u8);
 	db_cfg.columns[super::columns::BLOCK_MAPPING as usize].btree_index = true;
 
 	let db = parity_db::Db::open_or_create(&db_cfg)
@@ -312,6 +349,179 @@ pub(crate) fn migrate_1_to_2_parity_db<Block: BlockT, C: HeaderBackend<Block>>(
 	// Read and update each entry in db transaction batches
 	const CHUNK_SIZE: usize = 10_000;
 	let chunks = ethereum_hashes.chunks(CHUNK_SIZE);
+	let all_len = ethereum_hashes.len();
+	for (i, chunk) in chunks.enumerate() {
+		process_chunk(&db, chunk)?;
+		log::debug!(
+			target: "fc-db-upgrade",
+			"🔨 Processed {} of {} entries.",
+			(CHUNK_SIZE * (i + 1)),
+			all_len
+		);
+	}
+	Ok(res)
+}
+
+/// Migration from version 2 to version 3:
+/// - Backfill the block_number -> ethereum_block_hash mapping for existing blocks.
+/// - This enables efficient lookups by block number without iterating through all mappings.
+#[cfg(feature = "rocksdb")]
+pub(crate) fn migrate_2_to_3_rocks_db<Block: BlockT, C: HeaderBackend<Block>>(
+	client: Arc<C>,
+	db_path: &Path,
+) -> UpgradeResult<UpgradeVersion2To3Summary> {
+	log::info!("🔨 Running Frontier DB migration from version 2 to version 3. Please wait.");
+	let mut res = UpgradeVersion2To3Summary {
+		success: 0,
+		skipped: 0,
+	};
+
+	// Process a batch of entries in a single db transaction
+	#[rustfmt::skip]
+	let mut process_chunk = |
+		db: &kvdb_rocksdb::Database,
+		entries: &[(smallvec::SmallVec<[u8; 32]>, Vec<u8>)]
+	| -> UpgradeResult<()> {
+		let mut transaction = db.transaction();
+		for (ethereum_hash, substrate_hashes_raw) in entries {
+			// Decode the Vec<Block::Hash> from the BLOCK_MAPPING value
+			if let Ok(substrate_hashes) = Vec::<Block::Hash>::decode(&mut &substrate_hashes_raw[..]) {
+				// Try to find a block number for any of the substrate hashes
+				let mut found = false;
+				for substrate_hash in substrate_hashes {
+					if let Ok(Some(number)) = client.number(substrate_hash) {
+						// Write block_number -> ethereum_block_hash mapping
+						let Ok(block_number): Result<u64, _> = number.try_into() else {
+							res.skipped += 1;
+							continue;
+						};
+						let eth_hash = H256::from_slice(ethereum_hash);
+						transaction.put_vec(
+							super::columns::BLOCK_NUMBER_MAPPING,
+							&block_number.encode(),
+							eth_hash.encode(),
+						);
+						res.success += 1;
+						found = true;
+						break;
+					}
+				}
+				if !found {
+					res.skipped += 1;
+				}
+			} else {
+				res.skipped += 1;
+			}
+		}
+		db.write(transaction)
+			.map_err(|_| io::Error::other("Failed to commit on migrate_2_to_3"))?;
+		log::debug!(
+			target: "fc-db-upgrade",
+			"🔨 Migration 2->3: Success {}, skipped {}.",
+			res.success,
+			res.skipped
+		);
+		Ok(())
+	};
+
+	let db_cfg = kvdb_rocksdb::DatabaseConfig::with_columns(V3_NUM_COLUMNS);
+	let db = kvdb_rocksdb::Database::open(&db_cfg, db_path)?;
+
+	// Get all the block mapping entries
+	let entries: Vec<_> = db
+		.iter(super::columns::BLOCK_MAPPING)
+		.filter_map(|entry| entry.ok())
+		.collect();
+
+	// Read and update each entry in db transaction batches
+	const CHUNK_SIZE: usize = 10_000;
+	let chunks = entries.chunks(CHUNK_SIZE);
+	let all_len = entries.len();
+	for (i, chunk) in chunks.enumerate() {
+		process_chunk(&db, chunk)?;
+		log::debug!(
+			target: "fc-db-upgrade",
+			"🔨 Processed {} of {} entries.",
+			(CHUNK_SIZE * (i + 1)).min(all_len),
+			all_len
+		);
+	}
+	Ok(res)
+}
+
+pub(crate) fn migrate_2_to_3_parity_db<Block: BlockT, C: HeaderBackend<Block>>(
+	client: Arc<C>,
+	db_path: &Path,
+) -> UpgradeResult<UpgradeVersion2To3Summary> {
+	log::info!("🔨 Running Frontier DB migration from version 2 to version 3. Please wait.");
+	let mut res = UpgradeVersion2To3Summary {
+		success: 0,
+		skipped: 0,
+	};
+
+	// Process a batch of entries in a single db transaction
+	#[rustfmt::skip]
+	let mut process_chunk = |
+		db: &parity_db::Db,
+		entries: &[(Vec<u8>, Vec<u8>)]
+	| -> UpgradeResult<()> {
+		let mut transaction = vec![];
+		for (ethereum_hash, substrate_hashes_raw) in entries {
+			// Decode the Vec<Block::Hash> from the BLOCK_MAPPING value
+			if let Ok(substrate_hashes) = Vec::<Block::Hash>::decode(&mut &substrate_hashes_raw[..]) {
+				// Try to find a block number for any of the substrate hashes
+				let mut found = false;
+				for substrate_hash in substrate_hashes {
+					if let Ok(Some(number)) = client.number(substrate_hash) {
+						// Write block_number -> ethereum_block_hash mapping
+						let Ok(block_number): Result<u64, _> = number.try_into() else {
+							res.skipped += 1;
+							continue;
+						};
+						let eth_hash = H256::from_slice(ethereum_hash);
+						transaction.push((
+							super::columns::BLOCK_NUMBER_MAPPING as u8,
+							block_number.encode(),
+							Some(eth_hash.encode()),
+						));
+						res.success += 1;
+						found = true;
+						break;
+					}
+				}
+				if !found {
+					res.skipped += 1;
+				}
+			} else {
+				res.skipped += 1;
+			}
+		}
+		db.commit(transaction)
+			.map_err(|_| io::Error::other("Failed to commit on migrate_2_to_3"))?;
+		Ok(())
+	};
+
+	let mut db_cfg = parity_db::Options::with_columns(db_path, V3_NUM_COLUMNS as u8);
+	db_cfg.columns[super::columns::BLOCK_MAPPING as usize].btree_index = true;
+
+	let db = parity_db::Db::open_or_create(&db_cfg)
+		.map_err(|_| io::Error::other("Failed to open db"))?;
+
+	// Get all the block mapping entries
+	let entries: Vec<_> = match db.iter(super::columns::BLOCK_MAPPING as u8) {
+		Ok(mut iter) => {
+			let mut items = vec![];
+			while let Ok(Some((k, v))) = iter.next() {
+				items.push((k, v));
+			}
+			items
+		}
+		Err(_) => vec![],
+	};
+
+	// Read and update each entry in db transaction batches
+	const CHUNK_SIZE: usize = 10_000;
+	let chunks = entries.chunks(CHUNK_SIZE);
 	for chunk in chunks {
 		process_chunk(&db, chunk)?;
 	}
@@ -354,7 +564,7 @@ mod tests {
 
 	#[cfg_attr(not(feature = "rocksdb"), ignore)]
 	#[test]
-	fn upgrade_1_to_2_works() {
+	fn upgrade_1_to_current_works() {
 		let settings: Vec<crate::kv::DatabaseSettings> = vec![
 			// Rocks db
 			#[cfg(feature = "rocksdb")]
@@ -403,6 +613,7 @@ mod tests {
 			let mut ethereum_hashes = vec![];
 			let mut substrate_hashes = vec![];
 			let mut transaction_hashes = vec![];
+			let mut block_numbers = vec![];
 			{
 				// Create a temporary frontier secondary DB.
 				let backend = open_frontier_backend::<OpaqueBlock, _>(client.clone(), &setting)
@@ -440,6 +651,7 @@ mod tests {
 					// Track canon hash
 					ethereum_hashes.push(ethhash);
 					substrate_hashes.push(next_canon_block_hash);
+					block_numbers.push(next_canon_block_number);
 					// Set orphan hash block mapping
 					transaction.set(
 						crate::kv::columns::BLOCK_MAPPING,
@@ -480,14 +692,15 @@ mod tests {
 				.write_all(format!("{}", 1).as_bytes())
 				.expect("write version 1");
 
-			// Upgrade database from version 1 to 2
+			// Upgrade database from version 1 to current
 			let _ = super::upgrade_db::<OpaqueBlock, _>(client.clone(), path, &setting.source);
 
 			// Check data after migration
 			let backend = open_frontier_backend::<OpaqueBlock, _>(client, &setting)
 				.expect("a temporary db was created");
 			for (i, original_ethereum_hash) in ethereum_hashes.iter().enumerate() {
 				let canon_substrate_block_hash = substrate_hashes.get(i).expect("Block hash");
+				let block_number = *block_numbers.get(i).expect("Block number");
 				let mapped_block = backend
 					.mapping()
 					.block_hash(original_ethereum_hash)
@@ -505,10 +718,16 @@ mod tests {
 				assert!(mapped_transaction
 					.into_iter()
 					.any(|tx| tx.substrate_block_hash == *canon_substrate_block_hash));
+				// Verify block_number -> ethereum_hash mapping (v2->v3 migration)
+				let mapped_eth_hash = backend
+					.mapping()
+					.block_hash_by_number(block_number)
+					.unwrap();
+				assert_eq!(mapped_eth_hash, Some(*original_ethereum_hash));
 			}
 
 			// Upgrade db version file
-			assert_eq!(super::current_version(path).expect("version"), 2u32);
+			assert_eq!(super::current_version(path).expect("version"), 3u32);
 		}
 	}
 
@@ -537,6 +756,6 @@ mod tests {
 
 		let mut s = String::new();
 		file.read_to_string(&mut s).expect("read file contents");
-		assert_eq!(s.parse::<u32>().expect("parse file contents"), 2u32);
+		assert_eq!(s.parse::<u32>().expect("parse file contents"), 3u32);
 	}
 }
```

### client/db/src/sql/mod.rs
```diff
@@ -782,6 +782,18 @@ impl<Block: BlockT<Hash = H256>> fc_api::Backend<Block> for Backend<Block> {
 		Ok(res)
 	}
 
+	async fn block_hash_by_number(&self, block_number: u64) -> Result<Option<H256>, String> {
+		let block_number = block_number as i64;
+		sqlx::query(
+			"SELECT ethereum_block_hash FROM blocks WHERE block_number = ? AND is_canon = 1",
+		)
+		.bind(block_number)
+		.fetch_optional(&self.pool)
+		.await
+		.map(|maybe_row| maybe_row.map(|row| H256::from_slice(&row.get::<Vec<u8>, _>(0)[..])))
+		.map_err(|e| format!("Failed to fetch block hash by number: {e}"))
+	}
+
 	async fn transaction_metadata(
 		&self,
 		ethereum_transaction_hash: &H256,
@@ -828,12 +840,22 @@ impl<Block: BlockT<Hash = H256>> fc_api::Backend<Block> for Backend<Block> {
 	}
 
 	async fn latest_block_hash(&self) -> Result<Block::Hash, String> {
-		// Retrieves the block hash for the latest indexed block, maybe it's not canon.
-		sqlx::query("SELECT substrate_block_hash FROM blocks ORDER BY block_number DESC LIMIT 1")
-			.fetch_one(self.pool())
-			.await
-			.map(|row| H256::from_slice(&row.get::<Vec<u8>, _>(0)[..]))
-			.map_err(|e| format!("Failed to fetch best hash: {e}"))
+		// Return the latest indexed canonical block hash.
+		// This prevents returning stale data during reorgs.
+		//
+		// Note: During initial sync or after restart while mapping-sync catches up,
+		// this returns the genesis block hash (first indexed block). This is consistent
+		// with Geth's behavior where eth_getBlockByNumber("latest") returns block 0
+		// during initial sync. Users can check sync status via eth_syncing to determine
+		// if the node is still catching up.
+		sqlx::query(
+			"SELECT substrate_block_hash FROM blocks WHERE is_canon = 1 ORDER BY block_number DESC LIMIT 1",
+		)
+		.fetch_optional(self.pool())
+		.await
+		.map_err(|e| format!("Failed to fetch best hash: {e}"))?
+		.map(|row| H256::from_slice(&row.get::<Vec<u8>, _>(0)[..]))
+		.ok_or_else(|| "No canonical blocks indexed yet".to_string())
 	}
 }
 
```

### client/mapping-sync/src/kv/mod.rs
```diff
@@ -29,7 +29,7 @@ use sc_client_api::backend::{Backend, StorageProvider};
 use sp_api::{ApiExt, ProvideRuntimeApi};
 use sp_blockchain::{Backend as _, HeaderBackend};
 use sp_consensus::SyncOracle;
-use sp_runtime::traits::{Block as BlockT, Header as HeaderT, Zero};
+use sp_runtime::traits::{Block as BlockT, Header as HeaderT, UniqueSaturatedInto, Zero};
 // Frontier
 use fc_storage::StorageOverride;
 use fp_consensus::{FindLogError, Hashes, Log, PostLog, PreLog};
@@ -47,6 +47,8 @@ pub fn sync_block<Block: BlockT, C: HeaderBackend<Block>>(
 	header: &Block::Header,
 ) -> Result<(), String> {
 	let substrate_block_hash = header.hash();
+	let block_number: u64 = (*header.number()).unique_saturated_into();
+
 	match fp_consensus::find_log(header.digest()) {
 		Ok(log) => {
 			let gen_from_hashes = |hashes: Hashes| -> fc_db::kv::MappingCommitment<Block> {
@@ -64,16 +66,22 @@ pub fn sync_block<Block: BlockT, C: HeaderBackend<Block>>(
 			match log {
 				Log::Pre(PreLog::Block(block)) => {
 					let mapping_commitment = gen_from_block(block);
-					backend.mapping().write_hashes(mapping_commitment)
+					backend
+						.mapping()
+						.write_hashes(mapping_commitment, block_number)
 				}
 				Log::Post(post_log) => match post_log {
 					PostLog::Hashes(hashes) => {
 						let mapping_commitment = gen_from_hashes(hashes);
-						backend.mapping().write_hashes(mapping_commitment)
+						backend
+							.mapping()
+							.write_hashes(mapping_commitment, block_number)
 					}
 					PostLog::Block(block) => {
 						let mapping_commitment = gen_from_block(block);
-						backend.mapping().write_hashes(mapping_commitment)
+						backend
+							.mapping()
+							.write_hashes(mapping_commitment, block_number)
 					}
 					PostLog::BlockHash(expect_eth_block_hash) => {
 						let ethereum_block = storage_override.current_block(substrate_block_hash);
@@ -88,7 +96,9 @@ pub fn sync_block<Block: BlockT, C: HeaderBackend<Block>>(
 									))
 								} else {
 									let mapping_commitment = gen_from_block(block);
-									backend.mapping().write_hashes(mapping_commitment)
+									backend
+										.mapping()
+										.write_hashes(mapping_commitment, block_number)
 								}
 							}
 							None => backend.mapping().write_none(substrate_block_hash),
@@ -112,6 +122,7 @@ where
 	C::Api: EthereumRuntimeRPCApi<Block>,
 {
 	let substrate_block_hash = header.hash();
+	let block_number: u64 = (*header.number()).unique_saturated_into();
 
 	if let Some(api_version) = client
 		.runtime_api()
@@ -140,7 +151,9 @@ where
 			ethereum_block_hash: block_hash,
 			ethereum_transaction_hashes: Vec::new(),
 		};
-		backend.mapping().write_hashes(mapping_commitment)?;
+		backend
+			.mapping()
+			.write_hashes(mapping_commitment, block_number)?;
 	} else {
 		backend.mapping().write_none(substrate_block_hash)?;
 	};
```

### client/rpc/src/eth/block.rs
```diff
@@ -16,8 +16,6 @@
 // You should have received a copy of the GNU General Public License
 // along with this program. If not, see <https://www.gnu.org/licenses/>.
 
-use std::sync::Arc;
-
 use ethereum_types::{H256, U256};
 use jsonrpsee::core::RpcResult;
 // Substrate
@@ -33,7 +31,7 @@ use fp_rpc::EthereumRuntimeRPCApi;
 
 use crate::{
 	eth::{rich_block_build, BlockInfo, Eth},
-	frontier_backend_client, internal_err,
+	internal_err,
 };
 
 impl<B, C, P, CT, BE, CIDP, EC> Eth<B, C, P, CT, BE, CIDP, EC>
@@ -85,96 +83,86 @@ where
 		number_or_hash: BlockNumberOrHash,
 		full: bool,
 	) -> RpcResult<Option<RichBlock>> {
-		let client = Arc::clone(&self.client);
-		let block_data_cache = Arc::clone(&self.block_data_cache);
-		let backend = Arc::clone(&self.backend);
-		let pool = Arc::clone(&self.pool);
-
-		match frontier_backend_client::native_block_id::<B, C>(
-			client.as_ref(),
-			backend.as_ref(),
-			Some(number_or_hash),
-		)
-		.await?
-		{
-			Some(id) => {
-				let substrate_hash = client
-					.expect_block_hash_from_id(&id)
-					.map_err(|_| internal_err(format!("Expect block number from id: {id}")))?;
-
-				let block = block_data_cache.current_block(substrate_hash).await;
-				let statuses = block_data_cache
-					.current_transaction_statuses(substrate_hash)
-					.await;
-
-				let base_fee = client.runtime_api().gas_price(substrate_hash).ok();
-
-				match (block, statuses) {
-					(Some(block), Some(statuses)) => {
-						let hash = H256::from(keccak_256(&rlp::encode(&block.header)));
-						let mut rich_block = rich_block_build(
-							block,
-							statuses.into_iter().map(Option::Some).collect(),
-							Some(hash),
-							full,
-							base_fee,
-							false,
-						);
-
-						let substrate_hash = H256::from_slice(substrate_hash.as_ref());
-						if let Some(parent_hash) = self
-							.forced_parent_hashes
-							.as_ref()
-							.and_then(|parent_hashes| parent_hashes.get(&substrate_hash).cloned())
-						{
-							rich_block.inner.header.parent_hash = parent_hash
-						}
-
-						Ok(Some(rich_block))
-					}
-					_ => Ok(None),
-				}
-			}
-			None if number_or_hash == BlockNumberOrHash::Pending => {
-				let api = client.runtime_api();
-				let best_hash = client.info().best_hash;
-
-				// Get current in-pool transactions
-				let mut xts: Vec<<B as BlockT>::Extrinsic> = Vec::new();
-				// ready validated pool
-				xts.extend(
-					pool.ready()
-						.map(|in_pool_tx| in_pool_tx.data().as_ref().clone())
-						.collect::<Vec<<B as BlockT>::Extrinsic>>(),
-				);
+		// Handle pending blocks specially - they're not in mapping-sync
+		if number_or_hash == BlockNumberOrHash::Pending {
+			return self.pending_block(full).await;
+		}
 
-				// future validated pool
-				xts.extend(
-					pool.futures()
-						.iter()
-						.map(|in_pool_tx| in_pool_tx.data().as_ref().clone())
-						.collect::<Vec<<B as BlockT>::Extrinsic>>(),
+		// For all other block queries, use mapping-sync via block_info_by_number
+		let BlockInfo {
+			block,
+			statuses,
+			substrate_hash,
+			base_fee,
+			..
+		} = self.block_info_by_number(number_or_hash).await?;
+
+		match (block, statuses) {
+			(Some(block), Some(statuses)) => {
+				let hash = H256::from(keccak_256(&rlp::encode(&block.header)));
+				let mut rich_block = rich_block_build(
+					block,
+					statuses.into_iter().map(Option::Some).collect(),
+					Some(hash),
+					full,
+					Some(base_fee),
+					false,
 				);
 
-				let (block, statuses) = api
-					.pending_block(best_hash, xts)
-					.map_err(|_| internal_err(format!("Runtime access error at {best_hash}")))?;
-
-				let base_fee = api.gas_price(best_hash).ok();
-
-				match (block, statuses) {
-					(Some(block), Some(statuses)) => Ok(Some(rich_block_build(
-						block,
-						statuses.into_iter().map(Option::Some).collect(),
-						None,
-						full,
-						base_fee,
-						true,
-					))),
-					_ => Ok(None),
+				let substrate_hash = H256::from_slice(substrate_hash.as_ref());
+				if let Some(parent_hash) = self
+					.forced_parent_hashes
+					.as_ref()
+					.and_then(|parent_hashes| parent_hashes.get(&substrate_hash).cloned())
+				{
+					rich_block.inner.header.parent_hash = parent_hash
 				}
+
+				Ok(Some(rich_block))
 			}
-			None => Ok(None),
+			_ => Ok(None),
+		}
+	}
+
+	async fn pending_block(&self, full: bool) -> RpcResult<Option<RichBlock>> {
+		let api = self.client.runtime_api();
+		let best_hash = self.client.info().best_hash;
+
+		// Get current in-pool transactions
+		let mut xts: Vec<<B as BlockT>::Extrinsic> = Vec::new();
+		// ready validated pool
+		xts.extend(
+			self.pool
+				.ready()
+				.map(|in_pool_tx| in_pool_tx.data().as_ref().clone())
+				.collect::<Vec<<B as BlockT>::Extrinsic>>(),
+		);
+
+		// future validated pool
+		xts.extend(
+			self.pool
+				.futures()
+				.iter()
+				.map(|in_pool_tx| in_pool_tx.data().as_ref().clone())
+				.collect::<Vec<<B as BlockT>::Extrinsic>>(),
+		);
+
+		let (block, statuses) = api
+			.pending_block(best_hash, xts)
+			.map_err(|_| internal_err(format!("Runtime access error at {best_hash}")))?;
+
+		let base_fee = api.gas_price(best_hash).ok();
+
+		match (block, statuses) {
+			(Some(block), Some(statuses)) => Ok(Some(rich_block_build(
+				block,
+				statuses.into_iter().map(Option::Some).collect(),
+				None,
+				full,
+				base_fee,
+				true,
+			))),
+			_ => Ok(None),
 		}
 	}
 
```

### client/rpc/src/eth/mod.rs
```diff
@@ -141,21 +141,75 @@ where
 		&self,
 		number_or_hash: BlockNumberOrHash,
 	) -> RpcResult<BlockInfo<B::Hash>> {
-		let id = match frontier_backend_client::native_block_id::<B, C>(
+		// Derive the block number from the request.
+		let block_number: Option<u64> = match number_or_hash {
+			BlockNumberOrHash::Num(n) => Some(n),
+			BlockNumberOrHash::Latest => {
+				Some(self.client.info().best_number.unique_saturated_into())
+			}
+			BlockNumberOrHash::Earliest => Some(0),
+			BlockNumberOrHash::Safe | BlockNumberOrHash::Finalized => {
+				Some(self.client.info().finalized_number.unique_saturated_into())
+			}
+			BlockNumberOrHash::Pending => {
+				// Pending blocks are not indexed in mapping-sync.
+				// Return empty BlockInfo - pending blocks are handled specially
+				// by methods that need them (e.g., pending_block()).
+				return Ok(BlockInfo::default());
+			}
+			BlockNumberOrHash::Hash { hash, .. } => {
+				// For hash queries, use the existing eth block hash lookup
+				return self.block_info_by_eth_block_hash(hash).await;
+			}
+		};
+
+		// Query mapping-sync for the ethereum block hash by block number.
+		// This ensures consistency: if a block is visible, its transaction
+		// receipts are also available.
+		let eth_block_hash = match block_number {
+			Some(n) => self
+				.backend
+				.block_hash_by_number(n)
+				.await
+				.map_err(|err| internal_err(format!("{err:?}")))?,
+			None => None,
+		};
+
+		let Some(eth_hash) = eth_block_hash else {
+			return Ok(BlockInfo::default());
+		};
+
+		// Get substrate hash(es) for this ethereum block hash
+		let substrate_hashes = frontier_backend_client::load_hash::<B, C>(
 			self.client.as_ref(),
 			self.backend.as_ref(),
-			Some(number_or_hash),
+			eth_hash,
 		)
-		.await?
-		{
-			Some(id) => id,
-			None => return Ok(BlockInfo::default()),
+		.await
+		.map_err(|err| internal_err(format!("{err:?}")))?;
+
+		let Some(substrate_hash) = substrate_hashes else {
+			return Ok(BlockInfo::default());
 		};
 
-		let substrate_hash = self
-			.client
-			.expect_block_hash_from_id(&id)
-			.map_err(|_| internal_err(format!("Expect block number from id: {id}")))?;
+		// Verify the substrate hash is on the canonical chain for all non-genesis blocks.
+		// The mapping is written at block import time, not finalization. If mapping-sync
+		// is lagging or processed an orphan block, the mapping could be stale even for
+		// finalized block numbers. We always verify against the canonical chain to ensure
+		// consistency, with genesis (block 0) as the only exception since it's immutable.
+		if let Some(block_num) = block_number {
+			if block_num > 0 {
+				let canonical_hash = self
+					.client
+					.hash(block_num.unique_saturated_into())
+					.map_err(|e| internal_err(format!("{e:?}")))?;
+
+				if canonical_hash != Some(substrate_hash) {
+					// Mapping is stale - treat as not indexed yet
+					return Ok(BlockInfo::default());
+				}
+			}
+		}
 
 		self.block_info_by_substrate_hash(substrate_hash).await
 	}
```

### client/rpc/src/lib.rs
```diff
@@ -437,7 +437,7 @@ mod tests {
 			ethereum_block_hash,
 			ethereum_transaction_hashes: vec![],
 		};
-		let _ = backend.mapping().write_hashes(commitment);
+		let _ = backend.mapping().write_hashes(commitment, 2);
 
 		// Expect B1 to be canon
 		assert_eq!(
@@ -469,7 +469,7 @@ mod tests {
 			ethereum_block_hash,
 			ethereum_transaction_hashes: vec![],
 		};
-		let _ = backend.mapping().write_hashes(commitment);
+		let _ = backend.mapping().write_hashes(commitment, 2);
 
 		// Still expect B1 to be canon
 		assert_eq!(
```

### ts-tests/.mocharc.json
```diff
@@ -0,0 +1,3 @@
+{
+  "timeout": 15000
+}
```

### ts-tests/tests/test-balance.ts
```diff
@@ -17,7 +17,6 @@ describeWithFrontier("Frontier RPC (Balance)", (context) => {
 
 	step("balance to be updated after transfer", async function () {
 		await createAndFinalizeBlock(context.web3);
-		this.timeout(15000);
 
 		const tx = await context.web3.eth.accounts.signTransaction(
 			{
```

### ts-tests/tests/test-block.ts
```diff
@@ -57,7 +57,6 @@ describeWithFrontier("Frontier RPC (Block)", (context) => {
 
 	let firstBlockCreated = false;
 	step("should be at block 1 after block production", async function () {
-		this.timeout(15000);
 		await createAndFinalizeBlock(context.web3);
 		expect(await context.web3.eth.getBlockNumber()).to.equal(1);
 		firstBlockCreated = true;
@@ -138,7 +137,6 @@ describeWithFrontier("Frontier RPC (Block)", (context) => {
 	});
 
 	it.skip("should include previous block hash as parent", async function () {
-		this.timeout(15000);
 		await createAndFinalizeBlock(context.web3);
 		const block = await context.web3.eth.getBlock("latest");
 		expect(block.hash).to.not.equal(previousBlock.hash);
```
