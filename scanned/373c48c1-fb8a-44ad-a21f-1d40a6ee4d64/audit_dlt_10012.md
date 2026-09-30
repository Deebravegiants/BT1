# [?] Merge remote-tracking branch 'origin/master' into tgmichel-vulnerability-fix

## Summary
Severity: Unknown
Chain: Moonbeam
Component: moonbeam-foundation/moonbeam
Published: 2020-09-24
Source: https://github.com/moonbeam-foundation/moonbeam/commit/539d520b4ebc9b9f79ef1efe5a0a6a24337897c7
Type: security-commit

## Details
Merge remote-tracking branch 'origin/master' into tgmichel-vulnerability-fix

# Conflicts:
#	.github/workflows/tests.yml
#	Cargo.lock

## Patch
### .github/workflows/tests.yml
```diff
@@ -9,18 +9,15 @@ jobs:
     - uses: actions/checkout@v2
     - name: Submodules
       run: git submodule update --init --recursive
-    - name: Cache Rust dependencies
-      uses: actions/cache@v1.1.2
-      with:
-        path: target
-        key: ${{ runner.OS }}-build-${{ hashFiles('**/Cargo.lock') }}
-        restore-keys: |
-          ${{ runner.OS }}-build-
-    - uses: actions-rs/toolchain@v1
-      with:
-        target: wasm32-unknown-unknown
-        toolchain: nightly-2020-08-01
-        default: true
+    - name: Init
+      run: |
+        scripts/init.sh
+        cargo --version
+        rustc --version
+        cargo +$WASM_BUILD_TOOLCHAIN --version
+        rustc +$WASM_BUILD_TOOLCHAIN --version
+      env:
+        WASM_BUILD_TOOLCHAIN: nightly-2020-05-14
     - name: Build
       run: cargo build --verbose --all
     - name: Run tests
```

### .gitmodules
```diff
@@ -1,6 +1,3 @@
-[submodule "vendor/ethereum"]
-	path = vendor/ethereum
-	url = https://github.com/rust-blockchain/ethereum.git
 [submodule "vendor/frontier"]
 	path = vendor/frontier
 	url = https://github.com/PureStake/frontier
```

### Cargo.toml
```diff
@@ -1,12 +1,11 @@
 [workspace]
 members = [
-    'node',
-    'runtime',
+    'node/standalone',
+    'runtime/standalone',
+    'node/parachain',
+    'runtime/parachain',
 ]
 exclude = ["vendor"]
 
 [profile.release]
 panic = 'unwind'
-
-[patch.crates-io]
-ethereum = { path = "vendor/ethereum" }
```

### node/Cargo.toml
```diff
@@ -1,57 +0,0 @@
-[package]
-authors = ['PureStake']
-build = 'build.rs'
-description = 'Substrate Moonbeam Node '
-edition = '2018'
-homepage = 'https://moonbeam.network'
-license = 'Unlicense'
-name = 'node-moonbeam'
-repository = 'https://github.com/PureStake/moonbeam/'
-version = '0.1.1'
-
-[package.metadata.docs.rs]
-targets = ["x86_64-unknown-linux-gnu"]
-
-[dependencies]
-futures = "0.3.4"
-log = "0.4.8"
-structopt = "0.3.8"
-jsonrpc-core = "14.0.3"
-
-sp-api = { version = "2.0.0-dev", path = "../vendor/frontier/vendor/substrate/primitives/api" }
-sp-blockchain = { version = "2.0.0-dev", path = "../vendor/frontier/vendor/substrate/primitives/blockchain" }
-sc-rpc-api = { version = "0.8.0-dev", path = "../vendor/frontier/vendor/substrate/client/rpc-api" }
-sc-rpc = { version = "2.0.0-dev", path = "../vendor/frontier/vendor/substrate/client/rpc" }
-substrate-frame-rpc-system = { version = "2.0.0-dev", path = "../vendor/frontier/vendor/substrate/utils/frame/rpc/system" }
-pallet-transaction-payment-rpc = { version = "2.0.0-dev", path = "../vendor/frontier/vendor/substrate/frame/transaction-payment/rpc/" }
-sc-cli = { version = "0.8.0-dev", path = "../vendor/frontier/vendor/substrate/client/cli" }
-sp-core = { version = "2.0.0-dev", path = "../vendor/frontier/vendor/substrate/primitives/core" }
-sc-executor = { version = "0.8.0-dev", path = "../vendor/frontier/vendor/substrate/client/executor" }
-sc-service = { version = "0.8.0-dev", path = "../vendor/frontier/vendor/substrate/client/service" }
-sp-inherents = { version = "2.0.0-dev", path = "../vendor/frontier/vendor/substrate/primitives/inherents" }
-sc-transaction-pool = { version = "2.0.0-dev", path = "../vendor/frontier/vendor/substrate/client/transaction-pool" }
-sp-transaction-pool = { version = "2.0.0-dev", path = "../vendor/frontier/vendor/substrate/primitives/transaction-pool" }
-sc-network = { version = "0.8.0-dev", path = "../vendor/frontier/vendor/substrate/client/network" }
-sc-consensus-aura = { version = "0.8.0-dev", path = "../vendor/frontier/vendor/substrate/client/consensus/aura" }
-sp-consensus-aura = { version = "0.8.0-dev", path = "../vendor/frontier/vendor/substrate/primitives/consensus/aura" }
-sc-consensus-manual-seal = { path = "../vendor/frontier/vendor/substrate/client/consensus/manual-seal" }
-sp-consensus = { version = "0.8.0-dev", path = "../vendor/frontier/vendor/substrate/primitives/consensus/common" }
-sc-consensus = { version = "0.8.0-dev", path = "../vendor/frontier/vendor/substrate/client/consensus/common" }
-sp-timestamp = { version = "2.0.0-dev", default-features = false, path = "../vendor/frontier/vendor/substrate/primitives/timestamp" }
-evm = { version = "2.0.0-dev", package = "pallet-evm", path = "../vendor/frontier/vendor/substrate/frame/evm" }
-ethereum = { version = "0.1.0", package = "pallet-ethereum", path = "../vendor/frontier/frame/ethereum" }
-sc-finality-grandpa = { version = "0.8.0-dev", path = "../vendor/frontier/vendor/substrate/client/finality-grandpa" }
-sp-finality-grandpa = { version = "2.0.0-dev", path = "../vendor/frontier/vendor/substrate/primitives/finality-grandpa" }
-sc-client-api = { version = "2.0.0-dev", path = "../vendor/frontier/vendor/substrate/client/api" }
-sp-runtime = { version = "2.0.0-dev", path = "../vendor/frontier/vendor/substrate/primitives/runtime" }
-sc-basic-authorship = { path = "../vendor/frontier/vendor/substrate/client/basic-authorship" }
-sp-block-builder = { path = "../vendor/frontier/vendor/substrate/primitives/block-builder" }
-
-moonbeam-runtime = { path = "../runtime" }
-
-frontier-consensus = { version = "0.1.0", path = "../vendor/frontier/consensus" }
-frontier-rpc = { version = "0.1.0", path = "../vendor/frontier/rpc" }
-frontier-rpc-primitives = { version = "0.1.0", path = "../vendor/frontier/rpc/primitives" }
-
-[build-dependencies]
-substrate-build-script-utils = { version = "2.0.0-dev", path = "../vendor/frontier/vendor/substrate/utils/build-script-utils" }
```

### node/parachain/Cargo.toml
```diff
@@ -0,0 +1,102 @@
+[package]
+name = 'moonbase-testnet'
+description = 'Moonbase Parachain Collator'
+homepage = 'https://moonbeam.network'
+license = 'Unlicense'
+version = '0.1.0'
+authors = ["PureStake"]
+build = 'build.rs'
+edition = '2018'
+
+[[bin]]
+name = 'moonbase-testnet'
+path = 'src/main.rs'
+
+[dependencies]
+derive_more = '0.15.0'
+exit-future = '0.1.4'
+futures = { version = "0.3.1", features = ["compat"] }
+log = '0.4.8'
+parking_lot = '0.9.0'
+trie-root = '0.15.2'
+codec = { package = 'parity-scale-codec', version = '1.0.0' }
+structopt = "0.3.3"
+ansi_term = "0.12.1"
+serde = { version = "1.0.101", features = ["derive"] }
+jsonrpc-core = "14.0.3"
+
+# Parachain dependencies
+moonbase-runtime = { path = "../../runtime/parachain" }
+
+# Substrate dependencies
+sp-runtime = { git = "https://github.com/paritytech/substrate", default-features = false, branch = "rococo-branch" }
+sp-io = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sp-api = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sp-core = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sp-inherents = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sp-consensus = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sc-consensus = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sc-cli = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sc-client-api = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sc-client-db = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sc-executor = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sc-service = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sc-transaction-pool = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sp-transaction-pool = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sc-network = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sc-basic-authorship = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch", version = "0.8.0-rc5" }
+sp-timestamp = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sp-trie = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sc-finality-grandpa = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sc-informant = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sc-chain-spec = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+
+sp-blockchain = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sc-rpc-api = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sc-rpc = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+substrate-frame-rpc-system = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+pallet-transaction-payment-rpc = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sp-block-builder = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+sc-consensus-manual-seal = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+evm = { package = "pallet-evm", git = "https://github.com/purestake/substrate", branch = "tgmichel-rococo-branch" }
+
+ethereum = { version = "0.1.0", package = "pallet-ethereum", path = "../../vendor/frontier/frame/ethereum" }
+
+frontier-rpc = { version = "0.1.0", path = "../../vendor/frontier/rpc" }
+frontier-rpc-primitives = { version = "0.1.0", path = "../../vendor/frontier/rpc/primitives" }
+frontier-consensus = { version = "0.1.0", path = "../../vendor/frontier/consensus" }
+
+# Cumulus dependencies
+cumulus-consensus = { git = "https://github.com/paritytech/cumulus", rev = '8a445a425086fc927f946a72b245e829fba200d0' }
+cumulus-collator = { git = "https://github.com/paritytech/cumulus", rev = '8a445a425086fc927f946a72b245e829fba200d0' }
+cumulus-network = { git = "https://github.com/paritytech/cumulus", rev = '8a445a425086fc927f946a72b245e829fba200d0' }
+cumulus-primitives = { git = "https://github.com/paritytech/cumulus", rev = '8a445a425086fc927f946a72b245e829fba200d0' }
+cumulus-service = { git = "https://github.com/paritytech/cumulus", rev = '8a445a425086fc927f946a72b245e829fba200d0' }
+
+# Polkadot dependencies
+polkadot-primitives = { git = "https://github.com/paritytech/polkadot", branch = "rococo-branch" }
+polkadot-collator = { git = "https://github.com/paritytech/polkadot", branch = "rococo-branch" }
+polkadot-service = { git = "https://github.com/paritytech/polkadot", branch = "rococo-branch" }
+polkadot-cli = { git = "https://github.com/paritytech/polkadot", branch = "rococo-branch" }
+polkadot-test-service = { git = "https://github.com/paritytech/polkadot", branch = "rococo-branch" }
+polkadot-parachain = { git = "https://github.com/paritytech/polkadot", branch = "rococo-branch" }
+
+[build-dependencies]
+substrate-build-script-utils = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+
+[dev-dependencies]
+assert_cmd = "0.12"
+nix = "0.17"
+rand = "0.7.3"
+tokio = { version = "0.2.13", features = ["macros"] }
+
+# Polkadot dependencies
+polkadot-runtime-common = { git = "https://github.com/paritytech/polkadot", branch = "rococo-branch" }
+polkadot-test-runtime = { git = "https://github.com/paritytech/polkadot", branch = "rococo-branch" }
+polkadot-test-runtime-client = { git = "https://github.com/paritytech/polkadot", branch = "rococo-branch" }
+polkadot-test-service = { git = "https://github.com/paritytech/polkadot", branch = "rococo-branch" }
+
+# Substrate dependencies
+pallet-sudo = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+substrate-test-client = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
+substrate-test-runtime-client = { git = "https://github.com/paritytech/substrate", branch = "rococo-branch" }
```

### node/parachain/build.rs
```diff
@@ -0,0 +1,22 @@
+// Copyright 2019 Parity Technologies (UK) Ltd.
+// This file is part of Cumulus.
+
+// Substrate is free software: you can redistribute it and/or modify
+// it under the terms of the GNU General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+
+// Substrate is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
+// GNU General Public License for more details.
+
+// You should have received a copy of the GNU General Public License
+// along with Cumulus.  If not, see <http://www.gnu.org/licenses/>.
+
+use substrate_build_script_utils::{generate_cargo_keys, rerun_if_git_head_changed};
+
+fn main() {
+	generate_cargo_keys();
+	rerun_if_git_head_changed();
+}
```

### node/parachain/src/chain_spec.rs
```diff
@@ -0,0 +1,135 @@
+// Copyright 2020 Parity Technologies (UK) Ltd.
+
+use cumulus_primitives::ParaId;
+use moonbase_runtime::{
+	AccountId, BalancesConfig, GenesisConfig, Signature, SudoConfig, SystemConfig,
+	ParachainInfoConfig, WASM_BINARY, EVMConfig, EthereumConfig,
+};
+use sc_chain_spec::{ChainSpecExtension, ChainSpecGroup};
+use sc_service::ChainType;
+use serde::{Deserialize, Serialize};
+use sp_core::{sr25519, Pair, Public};
+use sp_runtime::traits::{IdentifyAccount, Verify};
+use std::collections::BTreeMap;
+
+/// Specialized `ChainSpec`. This is a specialization of the general Substrate ChainSpec type.
+pub type ChainSpec = sc_service::GenericChainSpec<GenesisConfig, Extensions>;
+
+/// Helper function to generate a crypto pair from seed
+pub fn get_from_seed<TPublic: Public>(seed: &str) -> <TPublic::Pair as Pair>::Public {
+	TPublic::Pair::from_string(&format!("//{}", seed), None)
+		.expect("static values are valid; qed")
+		.public()
+}
+
+/// The extensions for the [`ChainSpec`].
+#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, ChainSpecGroup, ChainSpecExtension)]
+#[serde(deny_unknown_fields)]
+pub struct Extensions {
+	/// The relay chain of the Parachain.
+	pub relay_chain: String,
+	/// The id of the Parachain.
+	pub para_id: u32,
+}
+
+impl Extensions {
+	/// Try to get the extension from the given `ChainSpec`.
+	pub fn try_get(chain_spec: &Box<dyn sc_service::ChainSpec>) -> Option<&Self> {
+		sc_chain_spec::get_extension(chain_spec.extensions())
+	}
+}
+
+type AccountPublic = <Signature as Verify>::Signer;
+
+/// Helper function to generate an account ID from seed
+pub fn get_account_id_from_seed<TPublic: Public>(seed: &str) -> AccountId
+where
+	AccountPublic: From<<TPublic::Pair as Pair>::Public>,
+{
+	AccountPublic::from(get_from_seed::<TPublic>(seed)).into_account()
+}
+
+pub fn get_chain_spec(id: ParaId) -> ChainSpec {
+	ChainSpec::from_genesis(
+		"Moonbase Parachain Local Testnet",
+		"local_testnet",
+		ChainType::Local,
+		move || {
+			testnet_genesis(
+				get_account_id_from_seed::<sr25519::Public>("Alice"),
+				vec![
+					get_account_id_from_seed::<sr25519::Public>("Alice"),
+					get_account_id_from_seed::<sr25519::Public>("Bob"),
+					get_account_id_from_seed::<sr25519::Public>("Charlie"),
+					get_account_id_from_seed::<sr25519::Public>("Dave"),
+					get_account_id_from_seed::<sr25519::Public>("Eve"),
+					get_account_id_from_seed::<sr25519::Public>("Ferdie"),
+					get_account_id_from_seed::<sr25519::Public>("Alice//stash"),
+					get_account_id_from_seed::<sr25519::Public>("Bob//stash"),
+					get_account_id_from_seed::<sr25519::Public>("Charlie//stash"),
+					get_account_id_from_seed::<sr25519::Public>("Dave//stash"),
+					get_account_id_from_seed::<sr25519::Public>("Eve//stash"),
+					get_account_id_from_seed::<sr25519::Public>("Ferdie//stash"),
+				],
+				id,
+			)
+		},
+		vec![],
+		None,
+		None,
+		None,
+		Extensions {
+			relay_chain: "local_testnet".into(),
+			para_id: id.into(),
+		},
+	)
+}
+
+pub fn staging_test_net(id: ParaId) -> ChainSpec {
+	ChainSpec::from_genesis(
+		"Moonbase Parachain Testnet",
+		"staging_testnet",
+		ChainType::Live,
+		move || {
+			testnet_genesis(
+				get_account_id_from_seed::<sr25519::Public>("Alice"),
+				vec![get_account_id_from_seed::<sr25519::Public>("Alice")],
+				id,
+			)
+		},
+		Vec::new(),
+		None,
+		None,
+		None,
+		Extensions {
+			relay_chain: "rococo_local_testnet".into(),
+			para_id: id.into(),
+		},
+	)
+}
+
+fn testnet_genesis(
+	root_key: AccountId,
+	endowed_accounts: Vec<AccountId>,
+	id: ParaId,
+) -> GenesisConfig {
+	GenesisConfig {
+		frame_system: Some(SystemConfig {
+			code: WASM_BINARY.to_vec(),
+			changes_trie_config: Default::default(),
+		}),
+		pallet_balances: Some(BalancesConfig {
+			balances: endowed_accounts
+				.iter()
+				.cloned()
+				.map(|k| (k, 1 << 60))
+				.collect(),
+		}),
+		pallet_sudo: Some(SudoConfig { key: root_key }),
+		parachain_info: Some(ParachainInfoConfig { parachain_id: id }),
+		pallet_evm: Some(EVMConfig {
+			accounts: BTreeMap::new(),
+		}),
+		ethereum: Some(EthereumConfig {}),
+	}
+}
```

### node/parachain/src/cli.rs
```diff
@@ -0,0 +1,112 @@
+// Copyright 2020 Parity Technologies (UK) Ltd.
+
+use std::path::PathBuf;
+
+use sc_cli;
+use structopt::StructOpt;
+
+/// Sub-commands supported by the collator.
+#[derive(Debug, StructOpt)]
+pub enum Subcommand {
+	#[structopt(flatten)]
+	Base(sc_cli::Subcommand),
+
+	/// Export the genesis state of the parachain.
+	#[structopt(name = "export-genesis-state")]
+	ExportGenesisState(ExportGenesisStateCommand),
+
+	/// Export the genesis wasm of the parachain.
+	#[structopt(name = "export-genesis-wasm")]
+	ExportGenesisWasm(ExportGenesisWasmCommand),
+}
+
+/// Command for exporting the genesis state of the parachain
+#[derive(Debug, StructOpt)]
+pub struct ExportGenesisStateCommand {
+	/// Output file name or stdout if unspecified.
+	#[structopt(parse(from_os_str))]
+	pub output: Option<PathBuf>,
+
+	/// Id of the parachain this state is for.
+	#[structopt(long, default_value = "200")]
+	pub parachain_id: u32,
+
+	/// The name of the chain for that the genesis state should be exported.
+	#[structopt(long)]
+	pub chain: Option<String>,
+}
+
+/// Command for exporting the genesis wasm file.
+#[derive(Debug, StructOpt)]
+pub struct ExportGenesisWasmCommand {
+	/// Output file name or stdout if unspecified.
+	#[structopt(parse(from_os_str))]
+	pub output: Option<PathBuf>,
+
+	/// The name of the chain for that the genesis wasm file should be exported.
+	#[structopt(long)]
+	pub chain: Option<String>,
+}
+
+#[derive(Debug, StructOpt)]
+pub struct RunCmd {
+	#[structopt(flatten)]
+	pub base: sc_cli::RunCmd,
+
+	/// Id of the parachain this collator collates for.
+	#[structopt(long)]
+	pub parachain_id: Option<u32>,
+}
+
+impl std::ops::Deref for RunCmd {
+	type Target = sc_cli::RunCmd;
+
+	fn deref(&self) -> &Self::Target {
+		&self.base
+	}
+}
+
+#[derive(Debug, StructOpt)]
+#[structopt(settings = &[
+	structopt::clap::AppSettings::GlobalVersion,
+	structopt::clap::AppSettings::ArgsNegateSubcommands,
+	structopt::clap::AppSettings::SubcommandsNegateReqs,
+])]
+pub struct Cli {
+	#[structopt(subcommand)]
+	pub subcommand: Option<Subcommand>,
+
+	#[structopt(flatten)]
+	pub run: RunCmd,
+
+	/// Relaychain arguments
+	#[structopt(raw = true)]
+	pub relaychain_args: Vec<String>,
+}
+
+#[derive(Debug)]
+pub struct RelayChainCli {
+	/// The actual relay chain cli object.
+	pub base: polkadot_cli::RunCmd,
+
+	/// Optional chain id that should be passed to the relay chain.
+	pub chain_id: Option<String>,
+
+	/// The base path that should be used by the relay chain.
+	pub base_path: Option<PathBuf>,
+}
+
+impl RelayChainCli {
+	/// Create a new instance of `Self`.
+	pub fn new<'a>(
+		base_path: Option<PathBuf>,
+		chain_id: Option<String>,
+		relay_chain_args: impl Iterator<Item = &'a String>,
+	) -> Self {
+		Self {
+			base_path,
+			chain_id,
+			base: polkadot_cli::RunCmd::from_iter(relay_chain_args),
+		}
+	}
+}
```

### node/parachain/src/command.rs
```diff
@@ -0,0 +1,368 @@
+// Copyright 2020 Parity Technologies (UK) Ltd.
+
+use crate::{
+	chain_spec,
+	cli::{Cli, RelayChainCli, Subcommand},
+};
+use codec::Encode;
+use cumulus_primitives::ParaId;
+use log::info;
+use moonbase_runtime::Block;
+use polkadot_parachain::primitives::AccountIdConversion;
+use sc_cli::{
+	ChainSpec, CliConfiguration, ImportParams, KeystoreParams, NetworkParams, Result,
+	RuntimeVersion, SharedParams, SubstrateCli, DefaultConfigurationValues,
+};
+use sc_service::config::{BasePath, PrometheusConfig};
+use sp_core::hexdisplay::HexDisplay;
+use sp_runtime::traits::{Block as BlockT, Hash as HashT, Header as HeaderT, Zero};
+use std::{io::Write, net::SocketAddr, sync::Arc};
+
+impl SubstrateCli for Cli {
+	fn impl_name() -> String {
+		"Moonbase Parachain Collator".into()
+	}
+
+	fn impl_version() -> String {
+		env!("SUBSTRATE_CLI_IMPL_VERSION").into()
+	}
+
+	fn description() -> String {
+		format!(
+			"Moonbase Parachain Collator\n\nThe command-line arguments provided first will be \
+		passed to the parachain node, while the arguments provided after -- will be passed \
+		to the relaychain node.\n\n\
+		{} [parachain-args] -- [relaychain-args]",
+			Self::executable_name()
+		)
+	}
+
+	fn author() -> String {
+		env!("CARGO_PKG_AUTHORS").into()
+	}
+
+	fn support_url() -> String {
+		"https://github.com/paritytech/cumulus/issues/new".into()
+	}
+
+	fn copyright_start_year() -> i32 {
+		2017
+	}
+
+	fn load_spec(&self, id: &str) -> std::result::Result<Box<dyn sc_service::ChainSpec>, String> {
+		match id {
+			"staging" => Ok(Box::new(chain_spec::staging_test_net(
+				self.run.parachain_id.unwrap_or(200).into(),
+			))),
+			"" => Ok(Box::new(chain_spec::get_chain_spec(
+				self.run.parachain_id.unwrap_or(200).into(),
+			))),
+			path => Ok(Box::new(chain_spec::ChainSpec::from_json_file(
+				path.into(),
+			)?)),
+		}
+	}
+
+	fn native_runtime_version(_: &Box<dyn ChainSpec>) -> &'static RuntimeVersion {
+		&moonbase_runtime::VERSION
+	}
+}
+
+impl SubstrateCli for RelayChainCli {
+	fn impl_name() -> String {
+		"Moonbeam Parachain Collator".into()
+	}
+
+	fn impl_version() -> String {
+		env!("SUBSTRATE_CLI_IMPL_VERSION").into()
+	}
+
+	fn description() -> String {
+		"Moonbeam Parachain Collator\n\nThe command-line arguments provided first will be \
+		passed to the parachain node, while the arguments provided after -- will be passed \
+		to the relaychain node.\n\n\
+		parachain-collator [parachain-args] -- [relaychain-args]"
+			.into()
+	}
+
+	fn author() -> String {
+		env!("CARGO_PKG_AUTHORS").into()
+	}
+
+	fn support_url() -> String {
+		"https://github.com/paritytech/cumulus/issues/new".into()
+	}
+
+	fn copyright_start_year() -> i32 {
+		2017
+	}
+
+	fn load_spec(&self, id: &str) -> std::result::Result<Box<dyn sc_service::ChainSpec>, String> {
+		polkadot_cli::Cli::from_iter([RelayChainCli::executable_name().to_string()].iter())
+			.load_spec(id)
+	}
+
+	fn native_runtime_version(chain_spec: &Box<dyn ChainSpec>) -> &'static RuntimeVersion {
+		polkadot_cli::Cli::native_runtime_version(chain_spec)
+	}
+}
+
+pub fn generate_genesis_state(chain_spec: &Box<dyn sc_service::ChainSpec>) -> Result<Block> {
+	let storage = chain_spec.build_storage()?;
+
+	let child_roots = storage.children_default.iter().map(|(sk, child_content)| {
+		let state_root = <<<Block as BlockT>::Header as HeaderT>::Hashing as HashT>::trie_root(
+			child_content.data.clone().into_iter().collect(),
+		);
+		(sk.clone(), state_root.encode())
+	});
+	let state_root = <<<Block as BlockT>::Header as HeaderT>::Hashing as HashT>::trie_root(
+		storage.top.clone().into_iter().chain(child_roots).collect(),
+	);
+
+	let extrinsics_root =
+		<<<Block as BlockT>::Header as HeaderT>::Hashing as HashT>::trie_root(Vec::new());
+
+	Ok(Block::new(
+		<<Block as BlockT>::Header as HeaderT>::new(
+			Zero::zero(),
+			extrinsics_root,
+			state_root,
+			Default::default(),
+			Default::default(),
+		),
+		Default::default(),
+	))
+}
+
+fn extract_genesis_wasm(chain_spec: &Box<dyn sc_service::ChainSpec>) -> Result<Vec<u8>> {
+	let mut storage = chain_spec.build_storage()?;
+
+	storage
+		.top
+		.remove(sp_core::storage::well_known_keys::CODE)
+		.ok_or_else(|| "Could not find wasm file in genesis state!".into())
+}
+
+/// Parse command line arguments into service configuration.
+pub fn run() -> Result<()> {
+	let cli = Cli::from_args();
+
+	match &cli.subcommand {
+		Some(Subcommand::Base(subcommand)) => {
+			let runner = cli.create_runner(subcommand)?;
+
+			runner.run_subcommand(subcommand, |mut config| {
+				let params = crate::service::new_partial(&mut config)?;
+
+				Ok((
+					params.client,
+					params.backend,
+					params.import_queue,
+					params.task_manager,
+				))
+			})
+		}
+		Some(Subcommand::ExportGenesisState(params)) => {
+			sc_cli::init_logger("");
+
+			let block =
+				generate_genesis_state(&cli.load_spec(&params.chain.clone().unwrap_or_default())?)?;
+			let header_hex = format!("0x{:?}", HexDisplay::from(&block.header().encode()));
+
+			if let Some(output) = &params.output {
+				std::fs::write(output, header_hex)?;
+			} else {
+				println!("{}", header_hex);
+			}
+
+			Ok(())
+		}
+		Some(Subcommand::ExportGenesisWasm(params)) => {
+			sc_cli::init_logger("");
+
+			let wasm_file =
+				extract_genesis_wasm(&cli.load_spec(&params.chain.clone().unwrap_or_default())?)?;
+
+			if let Some(output) = &params.output {
+				std::fs::write(output, wasm_file)?;
+			} else {
+				std::io::stdout().write_all(&wasm_file)?;
+			}
+
+			Ok(())
+		}
+		None => {
+			let runner = cli.create_runner(&*cli.run)?;
+
+			runner.run_node_until_exit(|config| {
+				// TODO
+				let key = Arc::new(sp_core::Pair::generate().0);
+
+				let extension = chain_spec::Extensions::try_get(&config.chain_spec);
+				let relay_chain_id = extension.map(|e| e.relay_chain.clone());
+				let para_id = extension.map(|e| e.para_id);
+
+				let polkadot_cli = RelayChainCli::new(
+					config.base_path.as_ref().map(|x| x.path().join("polkadot")),
+					relay_chain_id,
+					[RelayChainCli::executable_name().to_string()]
+						.iter()
+						.chain(cli.relaychain_args.iter()),
+				);
+
+				let id = ParaId::from(cli.run.parachain_id.or(para_id).unwrap_or(200));
+
+				let parachain_account =
+					AccountIdConversion::<polkadot_primitives::v0::AccountId>::into_account(&id);
+
+				let block =
+					generate_genesis_state(&config.chain_spec).map_err(|e| format!("{:?}", e))?;
+				let genesis_state = format!("0x{:?}", HexDisplay::from(&block.header().encode()));
+
+				let task_executor = config.task_executor.clone();
+				let polkadot_config =
+					SubstrateCli::create_configuration(&polkadot_cli, &polkadot_cli, task_executor)
+						.map_err(|err| format!("Relay chain argument error: {}", err))?;
+
+				info!("Parachain id: {:?}", id);
+				info!("Parachain Account: {}", parachain_account);
+				info!("Parachain genesis state: {}", genesis_state);
+				info!(
+					"Is collating: {}",
+					if cli.run.base.validator { "yes" } else { "no" }
+				);
+
+				crate::service::run_node(
+					config,
+					key,
+					polkadot_config,
+					id,
+					cli.run.base.validator,
+				)
+				.map(|(x, _)| x)
+			})
+		}
+	}
+}
+
+impl DefaultConfigurationValues for RelayChainCli {
+	fn p2p_listen_port() -> u16 {
+		30334
+	}
+
+	fn rpc_ws_listen_port() -> u16 {
+		9945
+	}
+
+	fn rpc_http_listen_port() -> u16 {
+		9934
+	}
+
+	fn prometheus_listen_port() -> u16 {
+		9616
+	}
+}
+
+impl CliConfiguration<Self> for RelayChainCli {
+	fn shared_params(&self) -> &SharedParams {
+		self.base.base.shared_params()
+	}
+
+	fn import_params(&self) -> Option<&ImportParams> {
+		self.base.base.import_params()
+	}
+
+	fn network_params(&self) -> Option<&NetworkParams> {
+		self.base.base.network_params()
+	}
+
+	fn keystore_params(&self) -> Option<&KeystoreParams> {
+		self.base.base.keystore_params()
+	}
+
+	fn base_path(&self) -> Result<Option<BasePath>> {
+		Ok(self
+			.shared_params()
+			.base_path()
+			.or_else(|| self.base_path.clone().map(Into::into)))
+	}
+
+	fn rpc_http(&self, default_listen_port: u16) -> Result<Option<SocketAddr>> {
+		self.base.base.rpc_http(default_listen_port)
+	}
+
+	fn rpc_ipc(&self) -> Result<Option<String>> {
+		self.base.base.rpc_ipc()
+	}
+
+	fn rpc_ws(&self, default_listen_port: u16) -> Result<Option<SocketAddr>> {
+		self.base.base.rpc_ws(default_listen_port)
+	}
+
+	fn prometheus_config(&self, default_listen_port: u16) -> Result<Option<PrometheusConfig>> {
+		self.base.base.prometheus_config(default_listen_port)
+	}
+
+	fn init<C: SubstrateCli>(&self) -> Result<()> {
+		unreachable!("PolkadotCli is never initialized; qed");
+	}
+
+	fn chain_id(&self, is_dev: bool) -> Result<String> {
+		let chain_id = self.base.base.chain_id(is_dev)?;
+
+		Ok(if chain_id.is_empty() {
+			self.chain_id.clone().unwrap_or_default()
+		} else {
+			chain_id
+		})
+	}
+
+	fn role(&self, is_dev: bool) -> Result<sc_service::Role> {
+		self.base.base.role(is_dev)
+	}
+
+	fn transaction_pool(&self) -> Result<sc_service::config::TransactionPoolOptions> {
+		self.base.base.transaction_pool()
+	}
+
+	fn state_cache_child_ratio(&self) -> Result<Option<usize>> {
+		self.base.base.state_cache_child_ratio()
+	}
+
+	fn rpc_methods(&self) -> Result<sc_service::config::RpcMethods> {
+		self.base.base.rpc_methods()
+	}
+
+	fn rpc_ws_max_connections(&self) -> Result<Option<usize>> {
+		self.base.base.rpc_ws_max_connections()
+	}
+
+	fn rpc_cors(&self, is_dev: bool) -> Result<Option<Vec<String>>> {
+		self.base.base.rpc_cors(is_dev)
+	}
+
+	fn telemetry_external_transport(&self) -> Result<Option<sc_service::config::ExtTransport>> {
+		self.base.base.telemetry_external_transport()
+	}
+
+	fn default_heap_pages(&self) -> Result<Option<u64>> {
+		self.base.base.default_heap_pages()
+	}
+
+	fn force_authoring(&self) -> Result<bool> {
+		self.base.base.force_authoring()
+	}
+
+	fn disable_grandpa(&self) -> Result<bool> {
+		self.base.base.disable_grandpa()
+	}
+
+	fn max_runtime_instances(&self) -> Result<Option<usize>> {
+		self.base.base.max_runtime_instances()
+	}
+
+	fn announce_block(&self) -> Result<bool> {
+		self.base.base.announce_block()
+	}
+}
```

### node/parachain/src/main.rs
```diff
@@ -0,0 +1,17 @@
+// Copyright 2020 Parity Technologies (UK) Ltd.
+
+//! Moonbase parachain collator
+
+#![warn(missing_docs)]
+#![warn(unused_extern_crates)]
+
+mod chain_spec;
+#[macro_use]
+mod service;
+mod cli;
+mod command;
+mod rpc;
+
+fn main() -> sc_cli::Result<()> {
+	command::run()
+}
```

### node/parachain/src/rpc.rs
```diff
@@ -0,0 +1,115 @@
+// This file is part of Frontier.
+
+// Copyright (C) 2019-2020 Parity Technologies (UK) Ltd.
+// SPDX-License-Identifier: Apache-2.0
+
+// Licensed under the Apache License, Version 2.0 (the "License");
+// you may not use this file except in compliance with the License.
+// You may obtain a copy of the License at
+//
+// 	http://www.apache.org/licenses/LICENSE-2.0
+//
+// Unless required by applicable law or agreed to in writing, software
+// distributed under the License is distributed on an "AS IS" BASIS,
+// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+// See the License for the specific language governing permissions and
+// limitations under the License.
+
+//! A collection of node-specific RPC methods.
+
+use std::{sync::Arc, fmt};
+
+use sc_consensus_manual_seal::rpc::{ManualSeal, ManualSealApi};
+use moonbase_runtime::{Hash, AccountId, Index, opaque::Block, Balance};
+use sp_api::ProvideRuntimeApi;
+use sp_transaction_pool::TransactionPool;
+use sp_blockchain::{Error as BlockChainError, HeaderMetadata, HeaderBackend};
+use sp_consensus::SelectChain;
+use sc_rpc_api::DenyUnsafe;
+use sc_client_api::backend::{StorageProvider, Backend, StateBackend, AuxStore};
+use sp_runtime::traits::BlakeTwo256;
+use sp_block_builder::BlockBuilder;
+
+/// Full client dependencies.
+pub struct FullDeps<C, P, SC> {
+	/// The client instance to use.
+	pub client: Arc<C>,
+	/// Transaction pool instance.
+	pub pool: Arc<P>,
+	/// The SelectChain Strategy
+	pub select_chain: SC,
+	/// Whether to deny unsafe calls
+	pub deny_unsafe: DenyUnsafe,
+	/// The Node authority flag
+	pub is_authority: bool,
+	/// Manual seal command sink
+	pub command_sink: Option<futures::channel::mpsc::Sender<sc_consensus_manual_seal::rpc::EngineCommand<Hash>>>,
+}
+
+/// Instantiate all Full RPC extensions.
+pub fn create_full<C, P, SC, BE>(
+	deps: FullDeps<C, P, SC>,
+) -> jsonrpc_core::IoHandler<sc_rpc::Metadata> where
+	BE: Backend<Block> + 'static,
+	BE::State: StateBackend<BlakeTwo256>,
+	C: ProvideRuntimeApi<Block> + StorageProvider<Block, BE> + AuxStore,
+	C: HeaderBackend<Block> + HeaderMetadata<Block, Error=BlockChainError> + 'static,
+	C: Send + Sync + 'static,
+	C::Api: substrate_frame_rpc_system::AccountNonceApi<Block, AccountId, Index>,
+	C::Api: BlockBuilder<Block>,
+	C::Api: pallet_transaction_payment_rpc::TransactionPaymentRuntimeApi<Block, Balance>,
+	C::Api: frontier_rpc_primitives::EthereumRuntimeRPCApi<Block>,
+	<C::Api as sp_api::ApiErrorExt>::Error: fmt::Debug,
+	P: TransactionPool<Block=Block> + 'static,
+	SC: SelectChain<Block> +'static,
+{
+	use substrate_frame_rpc_system::{FullSystem, SystemApi};
+	use pallet_transaction_payment_rpc::{TransactionPayment, TransactionPaymentApi};
+	use frontier_rpc::{EthApi, EthApiServer, NetApi, NetApiServer};
+
+	let mut io = jsonrpc_core::IoHandler::default();
+	let FullDeps {
+		client,
+		pool,
+		select_chain,
+		deny_unsafe,
+		is_authority,
+		command_sink
+	} = deps;
+
+	io.extend_with(
+		SystemApi::to_delegate(FullSystem::new(client.clone(), pool.clone(), deny_unsafe))
+	);
+	io.extend_with(
+		TransactionPaymentApi::to_delegate(TransactionPayment::new(client.clone()))
+	);
+	io.extend_with(
+		EthApiServer::to_delegate(EthApi::new(
+			client.clone(),
+			select_chain.clone(),
+			pool.clone(),
+			moonbase_runtime::TransactionConverter,
+			is_authority,
+		))
+	);
+
+	io.extend_with(
+		NetApiServer::to_delegate(NetApi::new(
+			client.clone(),
+			select_chain,
+		))
+	);
+
+	match command_sink {
+		Some(command_sink) => {
+			io.extend_with(
+				// We provide the rpc handler with the sending end of the channel to allow the rpc
+				// send EngineCommands to the background block authorship task.
+				ManualSealApi::to_delegate(ManualSeal::new(command_sink)),
+			);
+		}
+		_ => {}
+	}
+
+	io
+}
```
