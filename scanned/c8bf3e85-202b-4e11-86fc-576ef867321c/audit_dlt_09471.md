# [?] Merge pull request #2388 from opentensor/fix-node-panic

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-02-02
Source: https://github.com/RaoFoundation/subtensor/commit/a8d2ad019e18ecbc010a4b5e04524c05c15bab8a
Type: security-commit

## Details
Merge pull request #2388 from opentensor/fix-node-panic

Bump psdk/frontier with patch to prevent node panic

## Patch
### Cargo.toml
```diff
@@ -234,35 +234,35 @@ polkadot-sdk = { git = "https://github.com/paritytech/polkadot-sdk.git", tag = "
 runtime-common = { package = "polkadot-runtime-common", git = "https://github.com/paritytech/polkadot-sdk.git", tag = "polkadot-stable2503-6", default-features = false }
 
 # Frontier
-fp-evm = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-fp-rpc = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-fp-self-contained = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-fp-account = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-fc-storage = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-fc-db = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-fc-consensus = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-fp-consensus = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-fp-dynamic-fee = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-fc-api = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-fc-rpc = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-fc-rpc-core = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-fc-aura = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-fc-babe = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-fc-mapping-sync = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-precompile-utils = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
+fp-evm = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+fp-rpc = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+fp-self-contained = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+fp-account = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+fc-storage = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+fc-db = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+fc-consensus = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+fp-consensus = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+fp-dynamic-fee = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+fc-api = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+fc-rpc = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+fc-rpc-core = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+fc-aura = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+fc-babe = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+fc-mapping-sync = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+precompile-utils = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
 
 # Frontier FRAME
-pallet-base-fee = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-pallet-dynamic-fee = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-pallet-ethereum = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-pallet-evm = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-pallet-evm-precompile-dispatch = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-pallet-evm-chain-id = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-pallet-evm-precompile-modexp = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-pallet-evm-precompile-sha3fips = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-pallet-evm-precompile-simple = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-pallet-evm-precompile-bn128 = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
-pallet-hotfix-sufficients = { git = "https://github.com/opentensor/frontier", rev = "1748fe6dda5ccd4b644cac6c897a4970c27e1a8b", default-features = false }
+pallet-base-fee = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+pallet-dynamic-fee = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+pallet-ethereum = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+pallet-evm = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+pallet-evm-precompile-dispatch = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+pallet-evm-chain-id = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+pallet-evm-precompile-modexp = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+pallet-evm-precompile-sha3fips = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+pallet-evm-precompile-simple = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+pallet-evm-precompile-bn128 = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
+pallet-hotfix-sufficients = { git = "https://github.com/opentensor/frontier", rev = "6dc7c0400cfee2a1acb62ae17149c4d3a983e58d", default-features = false }
 
 #DRAND
 pallet-drand = { path = "pallets/drand", default-features = false }
@@ -318,190 +318,190 @@ w3f-bls = { git = "https://github.com/opentensor/bls", branch = "fix-no-std" }
 # NOTE: The Diener will patch unnecesarry crates while this is waiting to be merged: <https://github.com/paritytech/diener/pull/46>.
 # You may install diener from `liamaharon:ignore-unused-flag` if you like in the meantime.
 [patch."https://github.com/paritytech/polkadot-sdk"]
-frame-support = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-binary-merkle-tree = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-core = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-crypto-hashing = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-crypto-hashing-proc-macro = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-debug-derive = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-externalities = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-storage = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-runtime-interface = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-runtime-interface-proc-macro = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-std = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-tracing = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-wasm-interface = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-io = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-keystore = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-state-machine = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-panic-handler = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-trie = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-runtime = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-application-crypto = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-arithmetic = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-weights = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-api-proc-macro = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-metadata-ir = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-version = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-version-proc-macro = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-block-builder = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-block-builder = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-inherents = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-blockchain = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-consensus = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-database = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-client-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-substrate-prometheus-endpoint = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-executor = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-executor-common = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-allocator = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-maybe-compressed-blob = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-executor-polkavm = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-executor-wasmtime = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-substrate-wasm-builder = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-tracing = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-tracing-proc-macro = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-rpc = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-frame-executive = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-frame-system = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-frame-try-runtime = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-balances = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-frame-benchmarking = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-frame-support-procedural = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-frame-support-procedural-tools = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-frame-support-procedural-tools-derive = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-client-db = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-state-db = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-polkadot-sdk-frame = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-frame-system-benchmarking = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-frame-system-rpc-runtime-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-consensus-aura = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-consensus-slots = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-timestamp = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-consensus-grandpa = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-genesis-builder = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-keyring = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-offchain = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-session = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-staking = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-transaction-pool = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-polkadot-sdk = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-cumulus-primitives-core = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-polkadot-core-primitives = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-polkadot-parachain-primitives = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-polkadot-primitives = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-authority-discovery = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-staging-xcm = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-xcm-procedural = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-cumulus-primitives-parachain-inherent = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-cumulus-primitives-proof-size-hostfunction = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-message-queue = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-polkadot-runtime-parachains = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-authority-discovery = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-session = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-timestamp = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-authorship = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-babe = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-consensus-babe = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-frame-election-provider-support = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-frame-election-provider-solution-type = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-npos-elections = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-offences = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-staking = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-bags-list = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-staking-reward-curve = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-broker = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-mmr = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-mmr-primitives = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-polkadot-runtime-metrics = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-staging-xcm-executor = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-keystore = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-staging-xcm-builder = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-asset-conversion = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-transaction-payment = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-grandpa = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-sudo = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-transaction-payment-rpc-runtime-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-vesting = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-polkadot-runtime-common = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-asset-rate = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-election-provider-multi-phase = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-election-provider-support-benchmarking = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-fast-unstake = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-identity = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-staking-reward-fn = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-treasury = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-utility = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-root-testing = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-slot-range-helper = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-cumulus-primitives-storage-weight-reclaim = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-aura = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-cumulus-test-relay-sproof-builder = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-chain-spec = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-chain-spec-derive = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-network = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-network-common = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-network-types = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-utils = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-telemetry = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-cli = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-mixnet = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-transaction-pool-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-mixnet = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-service = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-consensus = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-informant = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-network-sync = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-fork-tree = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-network-light = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-network-transactions = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-rpc = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-rpc-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-statement-store = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-transaction-pool = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-rpc-server = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-rpc-spec-v2 = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-sysinfo = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-transaction-storage-proof = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-cumulus-relay-chain-interface = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-polkadot-overseer = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-tracing-gum = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-tracing-gum-proc-macro = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-polkadot-node-metrics = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-polkadot-node-primitives = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-polkadot-node-subsystem-types = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-polkadot-node-network-protocol = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-authority-discovery = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-polkadot-statement-table = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-frame-benchmarking-cli = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-cumulus-client-parachain-inherent = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-runtime-utilities = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-frame-metadata-hash-extension = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-nomination-pools = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-membership = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-multisig = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-nomination-pools-runtime-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-preimage = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-proxy = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-scheduler = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-staking-runtime-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-offchain = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-consensus-babe = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-consensus-epochs = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-consensus-slots = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-transaction-payment-rpc = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-consensus-babe-rpc = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-network-gossip = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-consensus-grandpa = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-consensus-grandpa-rpc = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-substrate-frame-rpc-system = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-basic-authorship = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-proposer-metrics = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-substrate-build-script-utils = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-consensus-aura = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-insecure-randomness-collective-flip = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-pallet-safe-mode = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sc-consensus-manual-seal = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-sp-crypto-ec-utils = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
-substrate-bip39 = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "58add17a1232888db9cfb70f4afb6dc7fd7b3a79" }
+frame-support = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+binary-merkle-tree = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-core = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-crypto-hashing = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-crypto-hashing-proc-macro = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-debug-derive = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-externalities = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-storage = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-runtime-interface = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-runtime-interface-proc-macro = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-std = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-tracing = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-wasm-interface = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-io = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-keystore = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-state-machine = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-panic-handler = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-trie = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-runtime = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-application-crypto = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-arithmetic = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-weights = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-api-proc-macro = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-metadata-ir = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-version = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-version-proc-macro = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-block-builder = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-block-builder = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-inherents = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-blockchain = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-consensus = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-database = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-client-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+substrate-prometheus-endpoint = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-executor = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-executor-common = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-allocator = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-maybe-compressed-blob = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-executor-polkavm = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-executor-wasmtime = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+substrate-wasm-builder = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-tracing = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-tracing-proc-macro = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-rpc = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+frame-executive = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+frame-system = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+frame-try-runtime = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-balances = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+frame-benchmarking = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+frame-support-procedural = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+frame-support-procedural-tools = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+frame-support-procedural-tools-derive = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-client-db = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-state-db = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+polkadot-sdk-frame = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+frame-system-benchmarking = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+frame-system-rpc-runtime-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-consensus-aura = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-consensus-slots = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-timestamp = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-consensus-grandpa = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-genesis-builder = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-keyring = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-offchain = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-session = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-staking = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-transaction-pool = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+polkadot-sdk = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+cumulus-primitives-core = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+polkadot-core-primitives = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+polkadot-parachain-primitives = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+polkadot-primitives = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-authority-discovery = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+staging-xcm = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+xcm-procedural = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+cumulus-primitives-parachain-inherent = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+cumulus-primitives-proof-size-hostfunction = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-message-queue = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+polkadot-runtime-parachains = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-authority-discovery = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-session = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-timestamp = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-authorship = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-babe = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-consensus-babe = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+frame-election-provider-support = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+frame-election-provider-solution-type = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-npos-elections = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-offences = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-staking = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-bags-list = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-staking-reward-curve = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-broker = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-mmr = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-mmr-primitives = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+polkadot-runtime-metrics = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+staging-xcm-executor = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-keystore = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+staging-xcm-builder = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-asset-conversion = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-transaction-payment = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-grandpa = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-sudo = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-transaction-payment-rpc-runtime-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-vesting = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+polkadot-runtime-common = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-asset-rate = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-election-provider-multi-phase = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-election-provider-support-benchmarking = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-fast-unstake = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-identity = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-staking-reward-fn = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-treasury = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-utility = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-root-testing = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+slot-range-helper = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+cumulus-primitives-storage-weight-reclaim = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-aura = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+cumulus-test-relay-sproof-builder = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-chain-spec = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-chain-spec-derive = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-network = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-network-common = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-network-types = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-utils = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-telemetry = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-cli = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-mixnet = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-transaction-pool-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-mixnet = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-service = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-consensus = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-informant = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-network-sync = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+fork-tree = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-network-light = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-network-transactions = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-rpc = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-rpc-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-statement-store = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-transaction-pool = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-rpc-server = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-rpc-spec-v2 = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-sysinfo = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-transaction-storage-proof = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+cumulus-relay-chain-interface = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+polkadot-overseer = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+tracing-gum = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+tracing-gum-proc-macro = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+polkadot-node-metrics = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+polkadot-node-primitives = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+polkadot-node-subsystem-types = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+polkadot-node-network-protocol = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-authority-discovery = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+polkadot-statement-table = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+frame-benchmarking-cli = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+cumulus-client-parachain-inherent = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-runtime-utilities = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+frame-metadata-hash-extension = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-nomination-pools = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-membership = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-multisig = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-nomination-pools-runtime-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-preimage = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-proxy = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-scheduler = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-staking-runtime-api = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-offchain = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-consensus-babe = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-consensus-epochs = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-consensus-slots = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-transaction-payment-rpc = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-consensus-babe-rpc = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-network-gossip = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-consensus-grandpa = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-consensus-grandpa-rpc = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+substrate-frame-rpc-system = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-basic-authorship = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-proposer-metrics = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+substrate-build-script-utils = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-consensus-aura = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-insecure-randomness-collective-flip = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+pallet-safe-mode = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sc-consensus-manual-seal = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+sp-crypto-ec-utils = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
+substrate-bip39 = { git = "https://github.com/opentensor/polkadot-sdk.git", rev = "df2f9b531e05ab2fa58a25113627c02d6fe96aaa" }
```
