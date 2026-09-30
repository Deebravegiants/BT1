# [?] Merge branch 'devnet-ready' into fix-crowdloan-reentrancy

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-26
Source: https://github.com/RaoFoundation/subtensor/commit/aecf5a1d38f385e8c5b8f896a88880023bc0fbbb
Type: security-commit

## Details
Merge branch 'devnet-ready' into fix-crowdloan-reentrancy

## Patch
### .github/workflows/contract-tests.yml
```diff
@@ -1,61 +0,0 @@
-name: Contract E2E Tests
-
-on:
-  pull_request:
-
-  ## Allow running workflow manually from the Actions tab
-  workflow_dispatch:
-    inputs:
-      verbose:
-        description: "Output more information when triggered manually"
-        required: false
-        default: ""
-
-concurrency:
-  group: evm-tests-${{ github.ref }}
-  cancel-in-progress: true
-
-env:
-  CARGO_TERM_COLOR: always
-  VERBOSE: ${{ github.events.input.verbose }}
-
-permissions:
-  contents: read
-
-jobs:
-  run:
-    runs-on: [self-hosted, fireactions-light]
-    env:
-      RUST_BACKTRACE: full
-    steps:
-      - name: Check-out repository under $GITHUB_WORKSPACE
-        uses: actions/checkout@v4
-
-      - name: Install Rust
-        uses: actions-rs/toolchain@v1
-        with:
-          toolchain: stable
-
-      - name: Utilize Shared Rust Cache
-        uses: Swatinem/rust-cache@v2
-
-      - name: Set up Node.js
-        uses: actions/setup-node@v4
-        with:
-          node-version: "22"
-
-      - name: Install dependencies
-        run: |
-          sudo DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a apt-get update
-          sudo DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a apt-get install -y --no-install-recommends -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" build-essential clang curl libssl-dev llvm libudev-dev protobuf-compiler nodejs pkg-config
-
-      - name: Run tests
-        uses: nick-fields/retry@v3
-        with:
-          timeout_minutes: 120
-          max_attempts: 3
-          retry_wait_seconds: 60
-          command: |
-            cd ${{ github.workspace }}
-            npm install --global yarn
-            ./contract-tests/run-ci.sh
```

### .github/workflows/typescript-e2e.yml
```diff
@@ -107,6 +107,8 @@ jobs:
             binary: fast
           - test: zombienet_subnets
             binary: fast
+          - test: zombienet_evm
+            binary: fast
 
     name: "typescript-e2e-${{ matrix.test }}"
 
```

### Cargo.lock
```diff
@@ -10230,23 +10230,6 @@ dependencies = [
  "sp-mmr-primitives",
 ]
 
-[[package]]
-name = "pallet-multi-collective"
-version = "1.0.0"
-dependencies = [
- "frame-benchmarking",
- "frame-support",
- "frame-system",
- "impl-trait-for-tuples",
- "num-traits",
- "parity-scale-codec",
- "scale-info",
- "sp-core",
- "sp-io",
- "sp-runtime",
- "subtensor-runtime-common",
-]
-
 [[package]]
 name = "pallet-multisig"
 version = "41.0.0"
@@ -10780,23 +10763,6 @@ dependencies = [
  "subtensor-runtime-common",
 ]
 
-[[package]]
-name = "pallet-signed-voting"
-version = "1.0.0"
-dependencies = [
- "frame-benchmarking",
- "frame-support",
- "frame-system",
- "log",
- "parity-scale-codec",
- "scale-info",
- "sp-core",
- "sp-io",
- "sp-runtime",
- "subtensor-macros",
- "subtensor-runtime-common",
-]
-
 [[package]]
 name = "pallet-skip-feeless-payment"
 version = "16.0.0"
@@ -18572,7 +18538,6 @@ dependencies = [
  "approx",
  "environmental",
  "frame-support",
- "impl-trait-for-tuples",
  "num-traits",
  "parity-scale-codec",
  "polkadot-runtime-common",
```

### Cargo.toml
```diff
@@ -64,7 +64,6 @@ pallet-subtensor = { path = "pallets/subtensor", default-features = false }
 pallet-subtensor-swap = { path = "pallets/swap", default-features = false }
 pallet-subtensor-swap-runtime-api = { path = "pallets/swap/runtime-api", default-features = false }
 pallet-subtensor-swap-rpc = { path = "pallets/swap/rpc", default-features = false }
-pallet-multi-collective = { path = "pallets/multi-collective", default-features = false }
 procedural-fork = { path = "support/procedural-fork", default-features = false }
 safe-bigmath = { package = "safe-bigmath", default-features = false, git = "https://github.com/sam0x17/safe-bigmath", rev = "013c49984910e1c9a23289e8c85e7a856e263a02" }
 safe-math = { path = "primitives/safe-math", default-features = false }
```

### common/Cargo.toml
```diff
@@ -14,7 +14,6 @@ targets = ["x86_64-unknown-linux-gnu"]
 codec = { workspace = true, features = ["derive"] }
 environmental.workspace = true
 frame-support.workspace = true
-impl-trait-for-tuples.workspace = true
 num-traits = { workspace = true, features = ["libm"] }
 scale-info.workspace = true
 serde.workspace = true
```

### common/src/lib.rs
```diff
@@ -9,19 +9,17 @@ use runtime_common::prod_or_fast;
 use scale_info::TypeInfo;
 use serde::{Deserialize, Serialize};
 use sp_runtime::{
-    MultiSignature, Perbill, Vec,
+    MultiSignature, Vec,
     traits::{IdentifyAccount, Verify},
 };
 use subtensor_macros::freeze_struct;
 
 pub use currency::*;
 pub use evm_context::*;
-pub use traits::*;
 pub use transaction_error::*;
 
 mod currency;
 mod evm_context;
-mod traits;
 mod transaction_error;
 
 /// Balance of an account.
@@ -525,35 +523,6 @@ impl TypeInfo for NetUidStorageIndex {
     }
 }
 
-#[derive(
-    Encode,
-    Decode,
-    DecodeWithMemTracking,
-    MaxEncodedLen,
-    PartialEq,
-    Eq,
-    Clone,
-    Copy,
-    TypeInfo,
-    Debug,
-)]
-#[freeze_struct("51505f4d98347bff")]
-pub struct VoteTally {
-    pub approval: Perbill,
-    pub rejection: Perbill,
-    pub abstention: Perbill,
-}
-
-impl Default for VoteTally {
-    fn default() -> Self {
-        Self {
-            approval: Perbill::zero(),
-            rejection: Perbill::zero(),
-            abstention: Perbill::one(),
-        }
-    }
-}
-
 #[cfg(test)]
 mod tests {
     use super::*;
```

### common/src/traits.rs
```diff
@@ -1,136 +0,0 @@
-use super::VoteTally;
-use frame_support::pallet_prelude::*;
-use sp_runtime::Vec;
-
-pub trait SetLike<T> {
-    fn contains(&self, item: &T) -> bool;
-    fn len(&self) -> u32;
-    fn is_initialized(&self) -> bool;
-    fn is_empty(&self) -> bool {
-        self.len() == 0
-    }
-    /// Materialize the set as a `Vec`. Used by signed-voting to snapshot
-    /// the voter set at poll creation. Implementations must return each
-    /// distinct member exactly once; ordering is unspecified.
-    fn to_vec(&self) -> Vec<T>;
-}
-
-/// Poll provider seen from the voting pallet's side. Carries the
-/// read-only queries plus the tally-update notification fired when a
-/// vote moves the tally.
-pub trait Polls<AccountId> {
-    type Index: Parameter + Copy + MaxEncodedLen;
-    type VotingScheme: PartialEq;
-    type VoterSet: SetLike<AccountId>;
-
-    fn is_ongoing(index: Self::Index) -> bool;
-    fn voting_scheme_of(index: Self::Index) -> Option<Self::VotingScheme>;
-    fn voter_set_of(index: Self::Index) -> Option<Self::VoterSet>;
-
-    fn on_tally_updated(index: Self::Index, tally: &VoteTally);
-    /// Worst-case upper bound on `on_tally_updated`'s weight.
-    fn on_tally_updated_weight() -> Weight;
-}
-
-/// Notification fired when a poll is created.
-///
-/// # Producer contract
-///
-/// Implementations are entitled to assume:
-///
-/// 1. `on_poll_created(p)` is called at most once per `(p, lifecycle)`,
-///    where `lifecycle` is the span between this hook and the matching
-///    `OnPollCompleted::on_poll_completed(p)`. A second call for the
-///    same index without an intervening completion is a contract
-///    violation: implementations should treat it as a no-op (so a buggy
-///    producer cannot silently clobber tallies) but are not required to
-///    detect every form of misuse.
-/// 2. `Polls::is_ongoing(p)` and `Polls::voting_scheme_of(p)` return
-///    consistent values for the duration of the lifecycle.
-/// 3. `Polls::voter_set_of(p)` may be queried during this hook.
-pub trait OnPollCreated<PollIndex> {
-    fn on_poll_created(poll_index: PollIndex);
-    /// Returns the worst-case upper bound on `on_poll_created`'s weight.
-    fn weight() -> Weight;
-}
-
-/// Notification fired when a poll reaches a terminal status.
-///
-/// # Producer contract
-///
-/// Implementations are entitled to assume:
-///
-/// 1. `on_poll_completed(p)` is called at most once per `(p, lifecycle)`.
-/// 2. The producer may have already updated `p`'s status to a terminal
-///    value before firing this hook, so `Polls::voting_scheme_of(p)` is
-///    not required to return `Some` here. Implementations that need to
-///    distinguish polls owned by a specific scheme should rely on
-///    locally-stored state rather than re-querying the producer.
-/// 3. `on_poll_completed` must not synchronously call back into the
-///    producer in a way that would re-enter `OnPollCreated`.
-pub trait OnPollCompleted<PollIndex> {
-    fn on_poll_completed(poll_index: PollIndex);
-    /// Returns the worst-case upper bound on `on_poll_completed`'s weight.
-    fn weight() -> Weight;
-}
-
-#[impl_trait_for_tuples::impl_for_tuples(10)]
-impl<I: Copy> OnPollCreated<I> for Tuple {
-    fn on_poll_created(poll_index: I) {
-        for_tuples!( #( Tuple::on_poll_created(poll_index); )* );
-    }
-
-    fn weight() -> Weight {
-        #[allow(clippy::let_and_return)]
-        let mut weight = Weight::zero();
-        for_tuples!( #( weight.saturating_accrue(Tuple::weight()); )* );
-        weight
-    }
-}
-
-#[impl_trait_for_tuples::impl_for_tuples(10)]
-impl<I: Copy> OnPollCompleted<I> for Tuple {
-    fn on_poll_completed(poll_index: I) {
-        for_tuples!( #( Tuple::on_poll_completed(poll_index); )* );
-    }
-
-    fn weight() -> Weight {
-        #[allow(clippy::let_and_return)]
-        let mut weight = Weight::zero();
-        for_tuples!( #( weight.saturating_accrue(Tuple::weight()); )* );
-        weight
-    }
-}
-
-/// Handler for when the members of a collective have changed.
-pub trait OnMembersChanged<CollectiveId, AccountId> {
-    /// A collective's members have changed, `incoming` members have joined and
-    /// `outgoing` members have left.
-    fn on_members_changed(
-        collective_id: CollectiveId,
-        incoming: &[AccountId],
-        outgoing: &[AccountId],
-    );
-    /// Worst-case upper bound on `on_members_changed`'s weight. The
-    /// implementation is responsible for bounding its own iteration over
-    /// `incoming`/`outgoing` against the relevant `MaxMembers` constant.
-    fn weight() -> Weight;
-}
-
-#[impl_trait_for_tuples::impl_for_tuples(10)]
-impl<CollectiveId: Clone, AccountId> OnMembersChanged<CollectiveId, AccountId> for Tuple {
-    fn on_members_changed(
-        collective_id: CollectiveId,
-        incoming: &[AccountId],
-        outgoing: &[AccountId],
-    ) {
-        for_tuples!( #( Tuple::on_members_changed(collective_id.clone(), incoming, outgoing); )* );
-    }
-
-    fn weight() -> Weight {
-        #[allow(clippy::let_and_return)]
-        let mut weight = Weight::zero();
-        for_tuples!( #( weight.saturating_accrue(Tuple::weight()); )* );
-        weight
-    }
-}
```

### contract-tests/.gitignore
```diff
@@ -1,3 +0,0 @@
-node_modules
-.papi
-.env
```

### contract-tests/README.md
```diff
@@ -1,52 +0,0 @@
-# type-test
-
-The contract-tests folder includes all typescript code to test the basic EVM function
-like token transfer, and all precompile contracts in Subtensor. It is
-implemented in typescript, use both ethers and viem lib to interact with
-contracts. The polkadot API is used to call extrinsic, get storage in Subtensor
-. The developers can use it to verify the code change in precompile contracts.
-
-The Ink contract tests also are included in the contract-tests folder.
-There is an Ink project in the bittensor folder, which include all functions defined
-in the runtime extension. The test file for it is wasm.contract.test.ts.
-
-The whole test process is also included in the CI, all test cases are executed for new
-commit. CI flow can get catch any failed test cases. The polkadot API get the
-latest metadata from the runtime, the case also can find out any incompatibility
-between runtime and precompile contracts.
-
-## polkadot api
-
-You need `polkadot-api` globally installed:
-
-```bash
-$ npm i -g polkadot-api
-```
-
-To get the metadata, you need start the localnet via run
-`./scripts/localnet.sh`. then run following command to get metadata, a folder
-name .papi will be created, which include the metadata and type definitions.
-
-```bash
-npx papi add devnet -w ws://localhost:9944
-```
-
-## get the new metadata
-
-If the runtime is upgrade, need to get the metadata again.
-
-```bash
-sh get-metadata.sh
-```
-
-## run all tests
-
-```bash
-yarn run test
-```
-
-## To run a particular test case, you can pass an argument with the name or part of the name. For example:
-
-```bash
-yarn run test -- -g "Can set subnet parameter"
-```
```

### contract-tests/get-metadata.sh
```diff
@@ -1,3 +0,0 @@
-rm -rf .papi
-npx papi add devnet -w ws://localhost:9944
-npx papi ink add ./bittensor/target/ink/bittensor.json 
\ No newline at end of file
```

### contract-tests/package.json
```diff
@@ -1,35 +0,0 @@
-{
-  "scripts": {
-    "test": "TS_NODE_PREFER_TS_EXTS=1 TS_NODE_TRANSPILE_ONLY=1 mocha --timeout 999999 --retries 3 --file src/setup.ts --require ts-node/register --extension ts \"test/**/*.ts\""
-  },
-  "keywords": [],
-  "author": "",
-  "license": "ISC",
-  "dependencies": {
-    "@polkadot-api/descriptors": "file:.papi/descriptors",
-    "@polkadot-api/ink-contracts": "^0.4.1",
-    "@polkadot-api/sdk-ink": "^0.5.1",
-    "@polkadot-labs/hdkd": "^0.0.25",
-    "@polkadot-labs/hdkd-helpers": "^0.0.25",
-    "@polkadot/api": "^16.4.6",
-    "@polkadot/util-crypto": "^14.0.1",
-    "@types/mocha": "^10.0.10",
-    "dotenv": "17.2.1",
-    "ethers": "^6.13.5",
-    "mocha": "^11.1.0",
-    "polkadot-api": "^1.22.0",
-    "rxjs": "^7.8.2",
-    "scale-ts": "^1.6.1",
-    "viem": "2.23.4",
-    "ws": "^8.18.2"
-  },
-  "devDependencies": {
-    "@types/chai": "^5.0.1",
-    "@types/node": "^22.18.0",
-    "assert": "^2.1.0",
-    "chai": "^6.0.1",
-    "prettier": "^3.3.3",
-    "ts-node": "^10.9.2",
-    "typescript": "^5.7.2"
-  }
-}
```
