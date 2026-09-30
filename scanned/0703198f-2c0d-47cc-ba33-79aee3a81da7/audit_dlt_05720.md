# [?] fix(rpc): reserve header and tx count space in block templates (GHSA-95m2-vx53-v2jw)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-17
Source: https://github.com/ZcashFoundation/zebra/commit/b23dfeacdce82c5505f4c0f2590b329c98786c5f
Type: security-commit

## Details
fix(rpc): reserve header and tx count space in block templates (GHSA-95m2-vx53-v2jw)

The ZIP-317 transaction selector budgeted mempool transactions against
the full MAX_BLOCK_BYTES, subtracting only the coinbase transaction.
The block header (1,487 bytes on Mainnet and Testnet) and the
transaction-count CompactSize also count toward MAX_BLOCK_BYTES, so a
template whose transactions filled that margin assembled into a block
over the consensus size limit, and every node rejected the solved
block, wasting the miner's proof-of-work.

Reserve the network-specific serialized header size and the widest
transaction count a full block can reach before admitting the coinbase
and mempool transactions.

Adds Header::serialized_size and Solution::serialized_size to
zebra-chain, a test pinning them to real header serialization on all
networks, and boundary tests proving a transaction exactly filling the
safe budget is selected while one byte more is not.

## Patch
### CHANGELOG.md
```diff
@@ -5,6 +5,14 @@ All notable changes to Zebra are documented in this file.
 The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
 and this project adheres to [Semantic Versioning](https://semver.org).
 
+## [Unreleased]
+
+### Security
+
+- Reserve space for the block header and transaction count when selecting block template
+  transactions, so blocks mined from Zebra's templates can no longer exceed the consensus size
+  limit ([GHSA-95m2-vx53-v2jw](https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-95m2-vx53-v2jw)).
+
 ## [Zebra 6.0.0](https://github.com/ZcashFoundation/zebra/releases/tag/v6.0.0) - 2026-07-10
 
 ### Added
```

### zebra-chain/CHANGELOG.md
```diff
@@ -5,6 +5,13 @@ All notable changes to this project will be documented in this file.
 The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
 and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
 
+## [Unreleased]
+
+### Added
+
+- `block::Header::serialized_size`
+- `work::equihash::Solution::serialized_size`
+
 ## [11.1.0] - 2026-07-10
 
 ### Added
```

### zebra-chain/src/block/header.rs
```diff
@@ -139,6 +139,15 @@ impl Header {
     pub fn hash(&self) -> Hash {
         Hash::from(self)
     }
+
+    /// Returns the size of a serialized block header on `network`, in bytes.
+    ///
+    /// Every header field has a fixed size, except the Equihash solution,
+    /// whose size is constant per network, so this is also constant per network.
+    pub fn serialized_size(network: &Network) -> usize {
+        // The fields before the nonce, the 32-byte nonce, and the length-prefixed solution.
+        Solution::INPUT_LENGTH + 32 + Solution::serialized_size(network)
+    }
 }
 
 /// A header with a count of the number of transactions in its block.
```

### zebra-chain/src/block/tests/vectors.rs
```diff
@@ -188,6 +188,46 @@ fn blockheader_serialization() {
     }
 }
 
+/// Checks that [`Header::serialized_size`] matches the actual size of serialized headers
+/// on every network.
+#[test]
+fn blockheader_serialized_size() {
+    let _init_guard = zebra_test::init();
+
+    // `BLOCKS` contains Mainnet and Testnet blocks, whose headers have the same size.
+    for block in zebra_test::vectors::BLOCKS.iter() {
+        let mut header = block[..Header::serialized_size(&Network::Mainnet)]
+            .zcash_deserialize_into::<Header>()
+            .expect("blockheader test vector should deserialize");
+
+        let serialized_header = header
+            .zcash_serialize_to_vec()
+            .expect("blockheader test vector should serialize");
+
+        assert_eq!(
+            serialized_header.len(),
+            Header::serialized_size(&Network::Mainnet),
+            "serialized header size should match Header::serialized_size on Mainnet"
+        );
+
+        // Regtest headers only differ in the size of the Equihash solution.
+        header.solution = crate::work::equihash::Solution::from_bytes(
+            &[0; crate::work::equihash::REGTEST_SOLUTION_SIZE],
+        )
+        .expect("Regtest solution size should be valid");
+
+        let serialized_header = header
+            .zcash_serialize_to_vec()
+            .expect("Regtest blockheader should serialize");
+
+        assert_eq!(
+            serialized_header.len(),
+            Header::serialized_size(&Network::new_regtest(Default::default())),
+            "serialized header size should match Header::serialized_size on Regtest"
+        );
+    }
+}
+
 #[test]
 fn round_trip_blocks() {
     let _init_guard = zebra_test::init();
```

### zebra-chain/src/work/equihash.rs
```diff
@@ -7,6 +7,7 @@ use serde_big_array::BigArray;
 
 use crate::{
     block::Header,
+    parameters::Network,
     serialization::{
         zcash_deserialize_bytes_external_count, zcash_serialize_bytes, CompactSizeMessage,
         SerializationError, ZcashDeserialize, ZcashDeserializeInto, ZcashSerialize,
@@ -112,6 +113,20 @@ impl Solution {
         }
     }
 
+    /// Returns the size of the serialized solution on `network`, in bytes,
+    /// including its CompactSize length prefix.
+    ///
+    /// The solution size is constant per network, so this is also constant per network.
+    pub fn serialized_size(network: &Network) -> usize {
+        if network.is_regtest() {
+            // The 36-byte Regtest solution has a 1-byte CompactSize length prefix.
+            1 + REGTEST_SOLUTION_SIZE
+        } else {
+            // The 1344-byte solution has a 3-byte CompactSize length prefix (`0xfd` + `u16`).
+            3 + SOLUTION_SIZE
+        }
+    }
+
     /// Returns a [`Solution`] of `[0; SOLUTION_SIZE]` to be used in block proposals.
     pub fn for_proposal() -> Self {
         // TODO: Accept network as an argument, and if it's Regtest, return the shorter null solution.
```

### zebra-rpc/CHANGELOG.md
```diff
@@ -5,6 +5,14 @@ All notable changes to this project will be documented in this file.
 The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
 and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
 
+## [Unreleased]
+
+### Fixed
+
+- Block template transaction selection now reserves space for the block header and the
+  transaction count, so assembled blocks can no longer exceed the consensus size limit
+  (GHSA-95m2-vx53-v2jw).
+
 ## [11.1.0] - 2026-07-10
 
 ### Changed
```

### zebra-rpc/src/methods/types/get_block_template/zip317.rs
```diff
@@ -15,9 +15,12 @@ use rand::{
 
 use zebra_chain::{
     amount::Amount,
-    block::{Height, MAX_BLOCK_BYTES},
+    block::{Header, Height, MAX_BLOCK_BYTES},
     parameters::Network,
-    transaction::{self, zip317::BLOCK_UNPAID_ACTION_LIMIT, VerifiedUnminedTx},
+    serialization::{CompactSizeMessage, ZcashSerialize},
+    transaction::{
+        self, zip317::BLOCK_UNPAID_ACTION_LIMIT, VerifiedUnminedTx, MIN_TRANSPARENT_TX_SIZE,
+    },
 };
 use zebra_consensus::MAX_BLOCK_SIGOPS;
 use zebra_node_services::mempool::TransactionDependencies;
@@ -96,6 +99,12 @@ pub fn select_mempool_transactions(
     let mut remaining_block_sigops = MAX_BLOCK_SIGOPS;
     let mut remaining_block_unpaid_actions: u32 = BLOCK_UNPAID_ACTION_LIMIT;
 
+    // `MAX_BLOCK_BYTES` limits the whole serialized block, so reserve space for the block header
+    // and the transaction count before budgeting transactions, or the assembled block could
+    // exceed the consensus size limit (GHSA-95m2-vx53-v2jw).
+    remaining_block_bytes -= Header::serialized_size(net);
+    remaining_block_bytes -= max_transaction_count_size();
+
     // Adjust the limits based on the coinbase transaction
     remaining_block_bytes -= fake_coinbase_tx.data.as_ref().len();
     remaining_block_sigops -= fake_coinbase_tx.sigops;
@@ -138,6 +147,25 @@ pub fn select_mempool_transactions(
     selected_txs
 }
 
+/// Returns the maximum possible serialized size of a block's transaction count, in bytes.
+///
+/// The transaction count is a CompactSize whose width grows with the count. A serialized
+/// transaction takes at least [`MIN_TRANSPARENT_TX_SIZE`] bytes, so a block can never contain
+/// more than `MAX_BLOCK_BYTES / MIN_TRANSPARENT_TX_SIZE` transactions, which bounds the width.
+fn max_transaction_count_size() -> usize {
+    let max_transaction_count: usize = (MAX_BLOCK_BYTES / MIN_TRANSPARENT_TX_SIZE)
+        .try_into()
+        .expect("fits in memory");
+
+    let max_transaction_count = CompactSizeMessage::try_from(max_transaction_count)
+        .expect("the maximum transaction count is below the CompactSize message limit");
+
+    max_transaction_count
+        .zcash_serialize_to_vec()
+        .expect("serialization into a vec can't fail")
+        .len()
+}
+
 /// Returns a fee-weighted index and the total weight of `transactions`.
 ///
 /// Returns `None` if there are no transactions, or if the weights are invalid.
```

### zebra-rpc/src/methods/types/get_block_template/zip317/tests.rs
```diff
@@ -5,12 +5,18 @@
 use zcash_keys::address::Address;
 use zcash_transparent::address::TransparentAddress;
 
-use zebra_chain::{block::Height, parameters::Network, transaction, transparent::OutPoint};
+use zebra_chain::{
+    amount::Amount,
+    block::{Header, Height, MAX_BLOCK_BYTES},
+    parameters::Network,
+    transaction,
+    transparent::OutPoint,
+};
 use zebra_node_services::mempool::TransactionDependencies;
 
-use crate::methods::types::get_block_template::MinerParams;
+use crate::methods::types::{get_block_template::MinerParams, transaction::TransactionTemplate};
 
-use super::select_mempool_transactions;
+use super::{max_transaction_count_size, select_mempool_transactions};
 
 #[test]
 fn excludes_tx_with_unselected_dependencies() {
@@ -105,3 +111,62 @@ fn includes_tx_with_selected_dependencies() {
         "should return a dependency depth of 1 for the dependent tx"
     );
 }
+
+/// Checks that transaction selection reserves space for the block header and the transaction
+/// count, which [`MAX_BLOCK_BYTES`] covers: a transaction exactly filling the remaining safe
+/// budget is selected, and a transaction one byte larger is not (GHSA-95m2-vx53-v2jw).
+#[test]
+fn reserves_space_for_block_header_and_transaction_count() {
+    let network = Network::Mainnet;
+    let height = Height(1_000_000);
+    let miner_params =
+        MinerParams::from(Address::from(TransparentAddress::PublicKeyHash([0x7e; 20])));
+
+    let coinbase_tx_size =
+        TransactionTemplate::new_coinbase(&network, height, &miner_params, Amount::zero())
+            .expect("valid coinbase transaction template")
+            .data
+            .as_ref()
+            .len();
+
+    let safe_budget = usize::try_from(MAX_BLOCK_BYTES).expect("fits in memory")
+        - Header::serialized_size(&network)
+        - max_transaction_count_size()
+        - coinbase_tx_size;
+
+    let mut unmined_tx = network
+        .unmined_transactions_in_blocks(..)
+        .next()
+        .expect("should not be empty");
+
+    unmined_tx.transaction.size = safe_budget;
+
+    assert_eq!(
+        select_mempool_transactions(
+            &network,
+            height,
+            &miner_params,
+            vec![unmined_tx.clone()],
+            TransactionDependencies::default(),
+            None,
+        )
+        .len(),
+        1,
+        "should select a transaction exactly filling the safe block budget"
+    );
+
+    unmined_tx.transaction.size = safe_budget + 1;
+
+    assert_eq!(
+        select_mempool_transactions(
+            &network,
+            height,
+            &miner_params,
+            vec![unmined_tx],
+            TransactionDependencies::default(),
+            None,
+        ),
+        vec![],
+        "should not select a transaction one byte over the safe block budget"
+    );
+}
```
