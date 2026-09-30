# [?] Merge branch 'pox-wf-integration' into fix/pox5-contract-reentrancy

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2026-06-05
Source: https://github.com/stacks-network/stacks-core/commit/745e04e2d0a68c9c70bf9674ace1bf6b5b6fe47c
Type: security-commit

## Details
Merge branch 'pox-wf-integration' into fix/pox5-contract-reentrancy

## Patch
### changelog.d/protect-grant-signer-key.fixed
```diff
@@ -0,0 +1 @@
+Allow only the signer to call `grant-signer-key`. Without this check someone could grief the signer, by watching for their call to `register-self` in the mempool, grabbing the `signer-key`, and then frontrunning a call to `grant-signer-key`, causing the signer's call to fail with `ERR_SIGNER_KEY_GRANT_USED`.
```

### changelog.d/revert-p2wsh-outputs.removed
```diff
@@ -0,0 +1 @@
+Remove the p2wsh output storage which is no longer needed in the latest Pstaking design.
```

### changelog.d/wasm-time.fixed
```diff
@@ -0,0 +1 @@
+Replaced `time` dependency in logging code with `chrono` to allow it to work properly in Wasm builds.
```

### contrib/core-contract-tests/contracts/signer-manager.clar
```diff
@@ -280,12 +280,10 @@
     )
     (begin
         (try! (authorize-admin))
-        (as-contract? ()
-            (try! (contract-call? .pox-5 grant-signer-key signer-key current-contract
-                auth-id signer-sig
-            ))
-            (try! (contract-call? .pox-5 register-signer signer-manager signer-key))
-        )
+        (try! (contract-call? .pox-5 grant-signer-key signer-key current-contract
+            auth-id signer-sig
+        ))
+        (contract-call? .pox-5 register-signer signer-manager signer-key)
     )
 )
 
```

### contrib/stacks-inspect/src/main.rs
```diff
@@ -1572,7 +1572,6 @@ fn analyze_sortition_mev(
                 true,
                 &burn_block.header,
                 burn_block.ops.clone(),
-                vec![],
                 &burnchain,
                 &tip_sort_id,
                 rc_info_opt,
```

### stacks-common/Cargo.toml
```diff
@@ -101,7 +101,7 @@ bech32_std = []
 bech32_strict = []
 
 # Wasm-specific features for easier configuration
-wasm-web = ["rand", "getrandom/js", "libsecp256k1/static-context"]
+wasm-web = ["rand", "getrandom/js", "libsecp256k1/static-context", "chrono/wasmbind"]
 wasm-deterministic = ["getrandom/custom"]
 
 [package.metadata.pinny]
```

### stacks-common/src/deps_common/bitcoin/util/hash.rs
```diff
@@ -68,12 +68,6 @@ impl Hash160 {
     }
 }
 
-impl From<[u8; 20]> for Hash160 {
-    fn from(value: [u8; 20]) -> Self {
-        Self(value)
-    }
-}
-
 impl Default for Sha256dEncoder {
     fn default() -> Self {
         Self::new()
```

### stacks-common/src/util/log.rs
```diff
@@ -15,7 +15,6 @@
 // along with this program.  If not, see <http://www.gnu.org/licenses/>.
 
 use std::io::Write;
-use std::time::{Duration, SystemTime};
 use std::{env, io, thread};
 
 use chrono::prelude::*;
@@ -41,21 +40,18 @@ fn print_msg_header(mut rd: &mut dyn RecordDecorator, record: &Record) -> io::Re
     write!(rd, " ")?;
 
     rd.start_timestamp()?;
-    let system_time = SystemTime::now();
     match &*STACKS_LOG_FORMAT_TIME {
         None => {
-            let elapsed = system_time
-                .duration_since(SystemTime::UNIX_EPOCH)
-                .unwrap_or(Duration::from_secs(0));
+            let now = Utc::now();
             write!(
                 rd,
                 "[{:5}.{:06}]",
-                elapsed.as_secs(),
-                elapsed.subsec_micros()
+                now.timestamp(),
+                now.timestamp_subsec_micros()
             )?;
         }
         Some(ref format) => {
-            let datetime: DateTime<Local> = system_time.into();
+            let datetime: DateTime<Local> = Local::now();
             write!(rd, "[{}]", datetime.format(format))?;
         }
     }
```

### stackslib/src/burnchains/bitcoin/blocks.rs
```diff
@@ -24,12 +24,12 @@ use stacks_common::deps_common::bitcoin::util::hash::bitcoin_merkle_root;
 use stacks_common::types::chainstate::BurnchainHeaderHash;
 use stacks_common::util::hash::to_hex;
 
-use crate::burnchains::bitcoin::address::{BitcoinAddress, SegwitBitcoinAddress};
+use crate::burnchains::bitcoin::address::BitcoinAddress;
 use crate::burnchains::bitcoin::indexer::BitcoinIndexer;
 use crate::burnchains::bitcoin::messages::BitcoinMessageHandler;
 use crate::burnchains::bitcoin::{
     bits, BitcoinBlock, BitcoinNetworkType, BitcoinTransaction, BitcoinTxInput, BitcoinTxOutput,
-    Error as btc_error, PeerMessage, WatchedP2WSHOutput, WitnessScriptHash,
+    Error as btc_error, PeerMessage,
 };
 use crate::burnchains::indexer::{
     BurnBlockIPC, BurnHeaderIPC, BurnchainBlockDownloader, BurnchainBlockParser,
@@ -475,40 +475,12 @@ impl BitcoinBlockParser {
             }
         }
 
-        // Extract transactions with P2WSH outputs
-        let mut watched_p2wsh_outputs = vec![];
-        for tx in block.txdata.iter() {
-            for (vout_index, output) in tx.output.iter().enumerate() {
-                let Some(parsed_output) =
-                    BitcoinTxOutput::from_bitcoin_txout(self.network_id, output)
-                else {
-                    continue;
-                };
-                let BitcoinAddress::Segwit(SegwitBitcoinAddress::P2WSH(
-                    _network_id,
-                    witness_script_hash,
-                )) = parsed_output.address
-                else {
-                    continue;
-                };
-                watched_p2wsh_outputs.push(WatchedP2WSHOutput {
-                    witness_script_hash: WitnessScriptHash(witness_script_hash),
-                    amount: parsed_output.units,
-                    txid: Txid::from_bitcoin_tx_hash(&tx.txid()),
-                    vout: vout_index
-                        .try_into()
-                        .expect("FATAL: parsed bitcoin tx with greater than u32::MAX outputs"),
-                });
-            }
-        }
-
         BitcoinBlock {
             block_height,
             block_hash: BurnchainHeaderHash::from_bitcoin_hash(&block.bitcoin_hash()),
             parent_block_hash: BurnchainHeaderHash::from_bitcoin_hash(&block.header.prev_blockhash),
             txs: accepted_txs,
             timestamp: block.header.time as u64,
-            watched_p2wsh_outputs,
         }
     }
 
@@ -1088,7 +1060,6 @@ mod tests {
                             ]
                         }
                     ],
-                    watched_p2wsh_outputs: vec![],
                     timestamp: 1543267060,
                 })
             },
@@ -1244,7 +1215,6 @@ mod tests {
                             ]
                         }
                     ],
-                    watched_p2wsh_outputs: vec![],
                 })
             },
             BlockFixture {
```

### stackslib/src/burnchains/bitcoin/mod.rs
```diff
@@ -21,7 +21,6 @@ use std::{error, fmt, io};
 
 use stacks_common::deps_common::bitcoin::network::serialize::Error as btc_serialize_error;
 use stacks_common::types::chainstate::BurnchainHeaderHash;
-use stacks_common::util::serde_serializers::prefix_hex;
 use stacks_common::util::HexError as btc_hex_error;
 
 use crate::burnchains::bitcoin::address::BitcoinAddress;
@@ -226,28 +225,12 @@ pub struct BitcoinTransaction {
     pub outputs: Vec<BitcoinTxOutput>,
 }
 
-#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
-pub struct WitnessScriptHash(#[serde(with = "prefix_hex")] pub [u8; 32]);
-
-#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
-pub struct WatchedP2WSHOutput {
-    /// Watched outputs are all P2WSH. This field is the P2WSH.
-    pub witness_script_hash: WitnessScriptHash,
-    /// Satoshis paid to this output
-    pub amount: u64,
-    /// Identifies the transaction which contained this output
-    pub txid: Txid,
-    /// The output index (vout) in the transaction corresponding to this output
-    pub vout: u32,
-}
-
 #[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
 pub struct BitcoinBlock {
     pub block_height: u64,
     pub block_hash: BurnchainHeaderHash,
     pub parent_block_hash: BurnchainHeaderHash,
     pub txs: Vec<BitcoinTransaction>,
-    pub watched_p2wsh_outputs: Vec<WatchedP2WSHOutput>,
     pub timestamp: u64,
 }
 
@@ -263,7 +246,6 @@ impl BitcoinBlock {
             block_height: height,
             block_hash: hash.clone(),
             parent_block_hash: parent.clone(),
-            watched_p2wsh_outputs: Vec::new(),
             txs,
             timestamp,
         }
```

### stackslib/src/burnchains/burnchain.rs
```diff
@@ -230,6 +230,11 @@ impl BurnchainStateTransition {
         })
         .epoch_id;
 
+        // NOTE: deliberately uses the classic prepare-phase predicate, which includes the mod 0
+        // block. Under PoX-5 the mod 0 block is the first reward-paying block of the cycle, so
+        // the cycle-start sortition runs with a 1-block window (as it always has). This is a
+        // known, intentional asymmetry: the mod 0 sortition confers no privileged power, and
+        // widening its window would be a consensus change at every cycle boundary.
         if !burnchain.is_in_prepare_phase(parent_snapshot.block_height + 1)
             && !burnchain
                 .pox_constants
@@ -1136,8 +1141,6 @@ impl Burnchain {
             cur_epoch.epoch_id,
             first_pox_waterfall_block,
         )?;
-        let p2wsh_outputs =
-            BurnchainDB::get_watched_outputs_at_block(burnchain_db.conn(), &header.block_hash)?;
 
         let sortition_tip = SortitionDB::get_canonical_sortition_tip(db.conn())?;
 
@@ -1149,7 +1152,6 @@ impl Burnchain {
             false,
             &header,
             blockstack_txs,
-            p2wsh_outputs,
             burnchain,
             &sortition_tip,
             None,
```

### stackslib/src/burnchains/db.rs
```diff
@@ -22,9 +22,7 @@ use rusqlite::{params, Connection, OpenFlags, Row, Transaction};
 use serde_json;
 use stacks_common::types::chainstate::BurnchainHeaderHash;
 use stacks_common::types::sqlite::NO_PARAMS;
-use stacks_common::util::hash::{hex_bytes, to_hex};
 
-use crate::burnchains::bitcoin::{WatchedP2WSHOutput, WitnessScriptHash};
 use crate::burnchains::{
     Burnchain, BurnchainBlock, BurnchainBlockHeader, Error as BurnchainError, Txid,
 };
@@ -51,10 +49,6 @@ static MIGRATIONS: &[Migration] = &[
         version: 3,
         statements: SCHEMA_3,
     },
-    Migration {
-        version: 4,
-        statements: SCHEMA_4,
-    },
 ];
 
 pub struct BurnchainDB {
@@ -68,7 +62,6 @@ pub struct BurnchainDBTransaction<'a> {
 pub struct BurnchainBlockData {
     pub header: BurnchainBlockHeader,
     pub ops: Vec<BlockstackOperationType>,
-    pub p2wsh_outputs: Vec<WatchedP2WSHOutput>,
 }
 
 /// A trait for reading burnchain block headers
@@ -103,46 +96,6 @@ pub struct BlockCommitMetadata {
     pub anchor_block_descendant: Option<u64>,
 }
 
-impl rusqlite::ToSql for WitnessScriptHash {
-    fn to_sql(&self) -> rusqlite::Result<rusqlite::types::ToSqlOutput<'_>> {
-        Ok(rusqlite::types::ToSqlOutput::Owned(
-            rusqlite::types::Value::Text(to_hex(&self.0)),
-        ))
-    }
-}
-
-impl rusqlite::types::FromSql for WitnessScriptHash {
-    fn column_result(value: rusqlite::types::ValueRef<'_>) -> rusqlite::types::FromSqlResult<Self> {
-        let hex_str = value.as_str()?;
-        let bytes = hex_bytes(hex_str).map_err(|e| {
-            warn!("Bad hex string read for witness-script-hash from SQLite DB"; "err" => %e);
-            rusqlite::types::FromSqlError::InvalidType
-        })?;
-        let script_hash = bytes.try_into().map_err(|_e| {
-            warn!("Bad witness script hash stored in SQLite DB, length should be 32 bytes");
-            rusqlite::types::FromSqlError::InvalidType
-        })?;
-        Ok(WitnessScriptHash(script_hash))
-    }
-}
-
-impl FromRow<WatchedP2WSHOutput> for WatchedP2WSHOutput {
-    fn from_row(row: &Row) -> Result<WatchedP2WSHOutput, DBError> {
-        let txid: Txid = row.get("txid")?;
-        let vout: u32 = row.get("vout")?;
-        let witness_script_hash: WitnessScriptHash = row.get("witness_script_hash")?;
-        let amount_i64: i64 = row.get("amount")?;
-
-        Ok(WatchedP2WSHOutput {
-            witness_script_hash,
-            amount: u64::try_from(amount_i64)
-                .expect("FATAL: negative amount stored in watched_p2wsh_outputs"),
-            txid,
-            vout,
-        })
-    }
-}
-
 impl FromRow<BlockCommitMetadata> for BlockCommitMetadata {
     fn from_row(row: &Row) -> Result<BlockCommitMetadata, DBError> {
         let burn_block_hash = BurnchainHeaderHash::from_column(row, "burn_block_hash")?;
@@ -386,26 +339,6 @@ pub static SCHEMA_3: &[&str] = &[
     "INSERT INTO db_config (version) VALUES (3);",
 ];
 
-const BURNCHAIN_DB_SCHEMA_4: &[&str] = &[
-    r#"
-    CREATE TABLE IF NOT EXISTS watched_p2wsh_outputs (
-        txid TEXT NOT NULL,
-        vout INTEGER NOT NULL,
-        block_hash TEXT NOT NULL,
-        block_height INTEGER NOT NULL,
-        witness_script_hash TEXT NOT NULL,
-        amount INTEGER NOT NULL,
-        PRIMARY KEY(txid, vout, block_hash),
-        FOREIGN KEY(block_hash) REFERENCES burnchain_db_block_headers(block_hash)
-    );
-    "#,
-    r#"CREATE INDEX IF NOT EXISTS index_watched_outputs_block_hash
-       ON watched_p2wsh_outputs(block_hash);"#,
-    "INSERT OR REPLACE INTO db_config (version) VALUES (4);",
-];
-
-pub static SCHEMA_4: &[&str] = BURNCHAIN_DB_SCHEMA_4;
-
 impl BurnchainDBTransaction<'_> {
     /// Store a burnchain block header into the burnchain database.
     /// Returns the row ID on success.
@@ -535,65 +468,6 @@ impl BurnchainDBTransaction<'_> {
         Ok(())
     }
 
-    /// Store watched outputs for a burnchain block.
-    /// Watched outputs are P2WSH outputs extracted from Bitcoin blocks.
-    pub(crate) fn store_watched_outputs(
-        &self,
-        block_header: &BurnchainBlockHeader,
-        watched_p2wsh_outputs: &[WatchedP2WSHOutput],
-    ) -> Result<(), BurnchainError> {
-        if watched_p2wsh_outputs.is_empty() {
-            return Ok(());
-        }
-
-        let sql = "INSERT INTO watched_p2wsh_outputs
-                   (txid, vout, block_hash, block_height, witness_script_hash, amount)
-                   VALUES (?1, ?2, ?3, ?4, ?5, ?6)";
-
-        for output in watched_p2wsh_outputs {
-            let args = params![
-                &output.txid,
-                output.vout,
-                &block_header.block_hash,
-                u64_to_sql(block_header.block_height)?,
-                &output.witness_script_hash,
-                u64_to_sql(output.amount)?,
-            ];
-
-            self.sql_tx.execute(sql, args)?;
-        }
-
-        test_debug!(
-            "Stored {} watched outputs for block {} at height {}",
-            watched_p2wsh_outputs.len(),
-            &block_header.block_hash,
-            block_header.block_height
-        );
-
-        Ok(())
-    }
-
-    /// Prune watched outputs whose block height is older than 1.5 reward cycles
-    /// before `current_block_height`.
-    pub fn prune_watched_outputs(
-        &self,
-        reward_cycle_length: u32,
-        current_block_height: u64,
-    ) -> Result<(), BurnchainError> {
-        let window = (3u64 * u64::from(reward_cycle_length)) / 2;
-        let threshold = current_block_height.saturating_sub(window);
-        let sql = "DELETE FROM watched_p2wsh_outputs WHERE block_height < ?1";
-        let deleted = self.sql_tx.execute(sql, [u64_to_sql(threshold)?])?;
-        if deleted > 0 {
-            test_debug!(
-                "Pruned {} watched outputs older than block height {}",
-                deleted,
-                threshold
-            );
-        }
-        Ok(())
-    }
-
     pub fn commit(self) -> Result<(), BurnchainError> {
         self.sql_tx.commit().map_err(BurnchainError::from)
     }
@@ -619,7 +493,7 @@ impl BurnchainDBTransaction<'_> {
 
 impl BurnchainDB {
     /// The current schema version of the burnchain DB.
-    pub const SCHEMA_VERSION: u32 = 4;
+    pub const SCHEMA_VERSION: u32 = 3;
 
     /// Returns the schema version of the database
     fn get_schema_version(conn: &Connection) -> Result<u32, BurnchainError> {
@@ -883,13 +757,7 @@ impl BurnchainDB {
             .ok_or_else(|| BurnchainError::UnknownBlock(block.clone()))?;
         let ops = query_rows(conn, block_ops_qry, params![block])?;
 
-        let p2wsh_outputs = Self::get_watched_outputs_at_block(conn, block)?;
-
-        Ok(BurnchainBlockData {
-            header,
-            ops,
-            p2wsh_outputs,
-        })
+        Ok(BurnchainBlockData { header, ops })
     }
 
     fn inner_get_burnchain_op(
@@ -1124,27 +992,16 @@ impl BurnchainDB {
         );
         apply_blockstack_txs_safety_checks(header.block_height, &mut blockstack_ops);
 
-        // Extract watched outputs from the block
-        let watched_p2wsh_outputs = match block {
-            BurnchainBlock::Bitcoin(bitcoin_block) => &bitcoin_block.watched_p2wsh_outputs,
-        };
-
-        // Store block header, blockstack ops, and watched outputs in a single transaction
+        // Store block header and blockstack ops in a single transaction
         let db_tx = self.tx_begin()?;
         test_debug!(
-            "Store block {},{} with {} ops and {} watched outputs",
+            "Store block {},{} with {} ops",
             &header.block_hash,
             header.block_height,
             blockstack_ops.len(),
-            watched_p2wsh_outputs.len()
         );
         db_tx.store_burnchain_db_entry(&header)?;
         db_tx.store_blockstack_ops(&header, &blockstack_ops)?;
-        db_tx.store_watched_outputs(&header, watched_p2wsh_outputs)?;
-        db_tx.prune_watched_outputs(
-            burnchain.pox_constants.reward_cycle_length,
-            header.block_height,
-        )?;
         db_tx.commit()?;
 
         Ok(blockstack_ops)
@@ -1164,18 +1021,6 @@ impl BurnchainDB {
         }
     }
 
-    /// Get all watched outputs for a specific Bitcoin block
-    pub fn get_watched_outputs_at_block(
-        conn: &DBConn,
-        block_hash: &BurnchainHeaderHash,
-    ) -> Result<Vec<WatchedP2WSHOutput>, BurnchainError> {
-        let sql = "SELECT txid, vout, witness_script_hash, amount
-                   FROM watched_p2wsh_outputs
-                   WHERE block_hash = ?1
-                   ORDER BY txid, vout";
-        query_rows(conn, sql, [block_hash]).map_err(BurnchainError::DBError)
-    }
-
     pub fn get_commit_in_block_at(
         conn: &DBConn,
         header_hash: &BurnchainHeaderHash,
```
