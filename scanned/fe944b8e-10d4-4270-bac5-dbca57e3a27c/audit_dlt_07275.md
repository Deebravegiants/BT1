# [?] Fix timer panics in the wasm light client (#4561)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2020-02-10
Source: https://github.com/paritytech/substrate/commit/ae03ee918e6338a3afc5dbd3742f5b8d7fa35271
Type: security-commit

## Details
Fix timer panics in the wasm light client (#4561)

* Make WASM browser thing compile

* Fix

* updated exit-future (github repo)

* Switch to broadcast crate

* Migrate client/cli

* Switch exit-future to modernize branch

* Small changes

* Switch to cargo version and fix fg tests

* fix basic-authorship

* Fix crash on grafana macro

* Fix grafana macro

* Switch node python version

* Disable record_metrics_slice in grafana macro on wasm

* Update client/grafana-data-source/src/lib.rs

* Revert "Update client/grafana-data-source/src/lib.rs"

This reverts commit 888009a8e0b7051bd4bfbbfdb0448bcf2e2aae93.

* Add wasm support for state machine

* Switch to my own libp2p version

* Revert "Switch to my own libp2p version"

This reverts commit ce613871b59264b3165b45c37943e6560240daa7.

* Revert "Add wasm support for state machine"

This reverts commit de7eaa0694d9534fc3b164621737968e9a6a7c5f.

* Add sc-browser

* Squash

* remove sc-browser

* Fix keystore on wasm

* stubs for removed functions to make env compatible with old runtimes

* Add test (that doesn't work)

* Fix build scripts

* Revert basic-authorship due to no panics

* Revert cli/informant

* Revert consensus

* revert offchain

* Update utils/browser/Cargo.toml

Co-Authored-By: Benjamin Kampmann <ben@gnunicorn.org>

* export console functions

* Add new chainspec

* Fix ws in chain spec

* revert chainspec

* Fix chainspec

* Use an Option<PathBuf> in keystore instead of cfg flags

* Remove crud

* Only use wasm-timer for instant and systemtime

* Remove telemetry changes

* Assuming this is ok

* Add a KeystoreConfig

* Add stubs back in

* Update libp2p

* Revert "Add stubs back in"

This reverts commit 4690cf1882aa0f99f7f00a58c4080c8aa9b77c36.

* Remove commented js again

* Bump kvdb-web version

* Fix cli

* Switch branch on futures-timer

* Fix tests

* Remove sc-client test build in check-web-wasm because there isn't a good way to build futures-timer with wasm-bindgen support in the build

* Remove more things ^^

* Switch branch on futures-timer back

* Put DB io stats behind a cfg flag

* Fix things

* Don't timeout transports on wasm

* Update branch of futures-timer and fix bad merge

* Spawn informant

* Fix network test

* Fix delay resets

* Changes

* Fix tests

* use wasm_timer for transaction pool

* Fixes

* Switch futures-timer to crates

* Only diagnose futures on native

* Fix sc-network-test tests

* Select log level in js

* Fix syncing ;^)

* Allow disabling colours in the informant

* Use OutputFormat enum for informant

* MallocSizeOf impl on transaction pool broke stuff because wasm_timer::Instant doesnt impl it so just revert the transaction pool to master

* Update futures-diagnose

* Revert "MallocSizeOf impl on transaction pool broke stuff because wasm_timer::Instant doesnt impl it so just revert the transaction pool to master"

This reverts commit baa4ffc94fd968b6660a2c17ba8113e06af15548.

* Pass whole chain spec in start_client

* Get Instant::now to work in transaction pool again

* Informant dep reordering

Co-authored-by: Pierre Krieger <pierre.krieger1708@gmail.com>
Co-authored-by: Bastian Köcher <bkchr@users.noreply.github.com>
Co-authored-by: Svyatoslav Nikolsky <svyatonik@gmail.com>
Co-authored-by: Benjamin Kampmann <ben.kampmann@googlemail.com>
Co-authored-by: Demi Obenour <48690212+DemiMarie-parity@users.noreply.github.com>

## Patch
### Cargo.lock
```diff
@@ -425,18 +425,21 @@ dependencies = [
 name = "browser-utils"
 version = "0.8.0"
 dependencies = [
+ "chrono",
  "clear_on_drop",
  "console_error_panic_hook",
  "console_log",
  "futures 0.1.29",
  "futures 0.3.4",
+ "futures-timer 3.0.1",
  "js-sys",
  "kvdb-web",
  "libp2p",
  "log 0.4.8",
  "rand 0.6.5",
  "rand 0.7.3",
  "sc-chain-spec",
+ "sc-informant",
  "sc-network",
  "sc-service",
  "wasm-bindgen",
@@ -595,10 +598,12 @@ version = "0.4.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "31850b4a4d6bae316f7a09e691c944c28299298837edc0a03f755618c23cbc01"
 dependencies = [
+ "js-sys",
  "num-integer",
  "num-traits",
  "serde",
  "time",
+ "wasm-bindgen",
 ]
 
 [[package]]
@@ -1717,20 +1722,19 @@ checksum = "7b0a34e53cf6cdcd0178aa573aed466b646eb3db769570841fda0c7ede375a27"
 
 [[package]]
 name = "futures-timer"
-version = "0.4.0"
+version = "2.0.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "878f1d2fc31355fa02ed2372e741b0c17e58373341e6a122569b4623a14a7d33"
-dependencies = [
- "futures-core-preview",
- "futures-util-preview",
- "pin-utils",
-]
+checksum = "a1de7508b218029b0f01662ed8f61b1c964b3ae99d6f25462d0f55a595109df6"
 
 [[package]]
 name = "futures-timer"
-version = "2.0.2"
+version = "3.0.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a1de7508b218029b0f01662ed8f61b1c964b3ae99d6f25462d0f55a595109df6"
+checksum = "3de1a2b2a2a33d9e60e17980b60ee061eeaae96a5abe9121db0fdb9af167a1c5"
+dependencies = [
+ "gloo-timers",
+ "send_wrapper 0.4.0",
+]
 
 [[package]]
 name = "futures-util"
@@ -1873,6 +1877,19 @@ dependencies = [
  "regex",
 ]
 
+[[package]]
+name = "gloo-timers"
+version = "0.2.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "0b2d17dbd803c2fc86cb1b613adf63192046a7176f383a8302594654752c4c4a"
+dependencies = [
+ "futures-channel",
+ "futures-core",
+ "js-sys",
+ "wasm-bindgen",
+ "web-sys",
+]
+
 [[package]]
 name = "goblin"
 version = "0.1.3"
@@ -1891,7 +1908,7 @@ dependencies = [
  "async-std",
  "chrono",
  "derive_more",
- "futures-timer 2.0.2",
+ "futures-timer 3.0.1",
  "futures-util",
  "hyper 0.13.2",
  "lazy_static",
@@ -1907,7 +1924,7 @@ name = "grafana-data-source-test"
 version = "2.0.0"
 dependencies = [
  "futures 0.3.4",
- "futures-timer 2.0.2",
+ "futures-timer 3.0.1",
  "grafana-data-source",
  "rand 0.7.3",
 ]
@@ -5450,7 +5467,7 @@ dependencies = [
  "derive_more",
  "env_logger 0.7.1",
  "futures 0.3.4",
- "futures-timer 2.0.2",
+ "futures-timer 3.0.1",
  "libp2p",
  "log 0.4.8",
  "parity-scale-codec",
@@ -5554,6 +5571,7 @@ dependencies = [
  "regex",
  "rpassword",
  "sc-client-api",
+ "sc-informant",
  "sc-network",
  "sc-service",
  "sc-telemetry",
@@ -5678,7 +5696,7 @@ dependencies = [
  "env_logger 0.7.1",
  "futures 0.1.29",
  "futures 0.3.4",
- "futures-timer 0.4.0",
+ "futures-timer 3.0.1",
  "log 0.4.8",
  "parity-scale-codec",
  "parking_lot 0.10.0",
@@ -5718,7 +5736,7 @@ dependencies = [
  "fork-tree",
  "futures 0.1.29",
  "futures 0.3.4",
- "futures-timer 0.4.0",
+ "futures-timer 3.0.1",
  "log 0.4.8",
  "merlin",
  "num-bigint",
@@ -5824,7 +5842,7 @@ name = "sc-consensus-slots"
 version = "0.8.0"
 dependencies = [
  "futures 0.3.4",
- "futures-timer 2.0.2",
+ "futures-timer 3.0.1",
  "log 0.4.8",
  "parity-scale-codec",
  "parking_lot 0.10.0",
@@ -5950,7 +5968,7 @@ dependencies = [
  "fork-tree",
  "futures 0.1.29",
  "futures 0.3.4",
- "futures-timer 2.0.2",
+ "futures-timer 3.0.1",
  "log 0.4.8",
  "parity-scale-codec",
  "parking_lot 0.10.0",
@@ -5981,6 +5999,22 @@ dependencies = [
  "tokio 0.1.22",
 ]
 
+[[package]]
+name = "sc-informant"
+version = "0.8.0"
+dependencies = [
+ "ansi_term 0.12.1",
+ "futures 0.3.4",
+ "log 0.4.8",
+ "parity-util-mem",
+ "sc-client-api",
+ "sc-network",
+ "sc-service",
+ "sp-blockchain",
+ "sp-runtime",
+ "wasm-timer",
+]
+
 [[package]]
 name = "sc-keystore"
 version = "2.0.0"
@@ -6009,7 +6043,7 @@ dependencies = [
  "fnv",
  "fork-tree",
  "futures 0.3.4",
- "futures-timer 0.4.0",
+ "futures-timer 3.0.1",
  "futures_codec",
  "libp2p",
  "linked-hash-map",
@@ -6043,6 +6077,7 @@ dependencies = [
  "tempfile",
  "unsigned-varint",
  "void",
+ "wasm-timer",
  "zeroize 1.1.0",
 ]
 
@@ -6052,13 +6087,14 @@ version = "0.8.0"
 dependencies = [
  "futures 0.1.29",
  "futures 0.3.4",
- "futures-timer 0.4.0",
+ "futures-timer 3.0.1",
  "libp2p",
  "log 0.4.8",
  "lru 0.1.17",
  "parking_lot 0.10.0",
  "sc-network",
  "sp-runtime",
+ "wasm-timer",
 ]
 
 [[package]]
@@ -6068,7 +6104,7 @@ dependencies = [
  "env_logger 0.7.1",
  "futures 0.1.29",
  "futures 0.3.4",
- "futures-timer 0.4.0",
+ "futures-timer 3.0.1",
  "libp2p",
  "log 0.4.8",
  "parking_lot 0.10.0",
@@ -6097,7 +6133,7 @@ dependencies = [
  "fnv",
  "futures 0.1.29",
  "futures 0.3.4",
- "futures-timer 2.0.2",
+ "futures-timer 3.0.1",
  "hyper 0.12.35",
  "hyper-rustls",
  "log 0.4.8",
@@ -6129,6 +6165,7 @@ dependencies = [
  "log 0.4.8",
  "rand 0.7.3",
  "serde_json",
+ "wasm-timer",
 ]
 
 [[package]]
@@ -6225,7 +6262,7 @@ dependencies = [
  "futures 0.1.29",
  "futures 0.3.4",
  "futures-diagnose",
- "futures-timer 2.0.2",
+ "futures-timer 3.0.1",
  "grafana-data-source",
  "lazy_static",
  "log 0.4.8",
@@ -6267,6 +6304,7 @@ dependencies = [
  "tokio 0.2.11",
  "tokio-executor 0.1.10",
  "tracing",
+ "wasm-timer",
 ]
 
 [[package]]
@@ -6306,7 +6344,7 @@ version = "2.0.0"
 dependencies = [
  "bytes 0.5.4",
  "futures 0.3.4",
- "futures-timer 2.0.2",
+ "futures-timer 3.0.1",
  "libp2p",
  "log 0.4.8",
  "parking_lot 0.10.0",
@@ -6318,6 +6356,7 @@ dependencies = [
  "slog-scope",
  "take_mut",
  "void",
+ "wasm-timer",
 ]
 
 [[package]]
@@ -6353,6 +6392,7 @@ dependencies = [
  "sp-runtime",
  "sp-transaction-pool",
  "substrate-test-runtime",
+ "wasm-timer",
 ]
 
 [[package]]
@@ -6376,6 +6416,7 @@ dependencies = [
  "sp-transaction-pool",
  "substrate-test-runtime-client",
  "substrate-test-runtime-transaction-pool",
+ "wasm-timer",
 ]
 
 [[package]]
@@ -6505,6 +6546,12 @@ version = "0.3.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "686ef91cf020ad8d4aca9a7047641fd6add626b7b89e14546c2b6a76781cf822"
 
+[[package]]
+name = "send_wrapper"
+version = "0.4.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "f638d531eccd6e23b980caf34876660d38e265409d8e99b397ab71eb3612fad0"
+
 [[package]]
 name = "serde"
 version = "1.0.104"
@@ -6854,7 +6901,7 @@ dependencies = [
  "derive_more",
  "futures 0.3.4",
  "futures-diagnose",
- "futures-timer 0.4.0",
+ "futures-timer 3.0.1",
  "libp2p",
  "log 0.4.8",
  "parity-scale-codec",
@@ -7235,6 +7282,7 @@ dependencies = [
  "sp-inherents",
  "sp-runtime",
  "sp-std",
+ "wasm-timer",
 ]
 
 [[package]]
```

### Cargo.toml
```diff
@@ -35,6 +35,7 @@ members = [
 	"client/executor/wasmtime",
 	"client/executor/runtime-test",
 	"client/finality-grandpa",
+	"client/informant",
 	"client/tracing",
 	"client/keystore",
 	"client/network",
```

### bin/node/cli/browser-demo/index.html
```diff
@@ -15,11 +15,12 @@
 async function start() {
 	log('Loading WASM');
 	await init('./pkg/node_cli_bg.wasm');
-	log('Successfully loaded WASM');
+	log('Fetching chain spec');
+	const chain_spec_response = await fetch("https://raw.githubusercontent.com/paritytech/substrate/master/bin/node/cli/res/flaming-fir.json");
+	const chain_spec_text = await chain_spec_response.text();
 
 	// Build our client.
-	log('Starting client');
-	let client = await start_client(ws());
+	let client = await start_client(chain_spec_text, 'info', ws());
 	log('Client started');
 
 	client.rpcSubscribe('{"method":"chain_subscribeNewHead","params":[],"id":1,"jsonrpc":"2.0"}',
```

### bin/node/cli/src/browser.rs
```diff
@@ -14,28 +14,28 @@
 // You should have received a copy of the GNU General Public License
 // along with Substrate.  If not, see <http://www.gnu.org/licenses/>.
 
-use crate::ChainSpec;
+use crate::chain_spec::ChainSpec;
 use log::info;
 use wasm_bindgen::prelude::*;
 use sc_service::Configuration;
 use browser_utils::{
 	Transport, Client,
 	browser_configuration, set_console_error_panic_hook, init_console_log,
 };
+use std::str::FromStr;
 
 /// Starts the client.
 #[wasm_bindgen]
-pub async fn start_client(wasm_ext: Transport) -> Result<Client, JsValue> {
-	start_inner(wasm_ext)
+pub async fn start_client(chain_spec: String, log_level: String, wasm_ext: Transport) -> Result<Client, JsValue> {
+	start_inner(chain_spec, log_level, wasm_ext)
 		.await
 		.map_err(|err| JsValue::from_str(&err.to_string()))
 }
 
-async fn start_inner(wasm_ext: Transport) -> Result<Client, Box<dyn std::error::Error>> {
+async fn start_inner(chain_spec: String, log_level: String, wasm_ext: Transport) -> Result<Client, Box<dyn std::error::Error>> {
 	set_console_error_panic_hook();
-	init_console_log(log::Level::Info)?;
-
-	let chain_spec = ChainSpec::FlamingFir.load()
+	init_console_log(log::Level::from_str(&log_level)?)?;
+	let chain_spec = ChainSpec::from_json_bytes(chain_spec.as_bytes().to_vec())
 		.map_err(|e| format!("{:?}", e))?;
 
 	let config: Configuration<_, _> = browser_configuration(wasm_ext, chain_spec)
```

### client/authority-discovery/Cargo.toml
```diff
@@ -14,7 +14,7 @@ bytes = "0.4.12"
 codec = { package = "parity-scale-codec", default-features = false, version = "1.0.3" }
 derive_more = "0.99.2"
 futures = "0.3.1"
-futures-timer = "2.0"
+futures-timer = "3.0.1"
 libp2p = { version = "0.15.0", default-features = false, features = ["secp256k1", "libp2p-websocket"] }
 log = "0.4.8"
 prost = "0.6.1"
```

### client/cli/Cargo.toml
```diff
@@ -21,6 +21,7 @@ tokio = { version = "0.2.9", features = [ "signal", "rt-core", "rt-threaded" ] }
 futures = "0.3.1"
 fdlimit = "0.1.1"
 serde_json = "1.0.41"
+sc-informant = { version = "0.8", path = "../informant" }
 sp-panic-handler = { version = "2.0.0", path = "../../primitives/panic-handler" }
 sc-client-api = { version = "2.0.0", path = "../api" }
 sp-blockchain = { version = "2.0.0", path = "../../primitives/blockchain" }
```

### client/cli/src/lib.rs
```diff
@@ -24,7 +24,6 @@ mod traits;
 mod params;
 mod execution_strategy;
 pub mod error;
-pub mod informant;
 mod runtime;
 mod node_key;
 
```

### client/cli/src/runtime.rs
```diff
@@ -21,7 +21,6 @@ use futures::select;
 use futures::pin_mut;
 use sc_service::{AbstractService, Configuration};
 use crate::error;
-use crate::informant;
 
 #[cfg(target_family = "unix")]
 async fn main<F, E>(func: F) -> Result<(), Box<dyn std::error::Error>>
@@ -124,7 +123,7 @@ where
 
 	let service = service_builder(config)?;
 
-	let informant_future = informant::build(&service);
+	let informant_future = sc_informant::build(&service, sc_informant::OutputFormat::Coloured);
 	let _informant_handle = runtime.spawn(informant_future);
 
 	// we eagerly drop the service so that the internal exit future is fired,
```

### client/consensus/aura/Cargo.toml
```diff
@@ -16,7 +16,7 @@ codec = { package = "parity-scale-codec", version = "1.0.0" }
 sp-consensus = { version = "0.8", path = "../../../primitives/consensus/common" }
 derive_more = "0.99.2"
 futures = "0.3.1"
-futures-timer = "0.4.0"
+futures-timer = "3.0.1"
 sp-inherents = { version = "2.0.0", path = "../../../primitives/inherents" }
 sc-keystore = { version = "2.0.0", path = "../../keystore" }
 log = "0.4.8"
```

### client/consensus/babe/Cargo.toml
```diff
@@ -32,7 +32,7 @@ sc-consensus-slots = { version = "0.8", path = "../slots" }
 sp-runtime = { version = "2.0.0", path = "../../../primitives/runtime" }
 fork-tree = { version = "2.0.0", path = "../../../utils/fork-tree" }
 futures = "0.3.1"
-futures-timer = "0.4.0"
+futures-timer = "3.0.1"
 parking_lot = "0.10.0"
 log = "0.4.8"
 schnorrkel = { version = "0.8.5", features = ["preaudit_deprecated"] }
```

### client/consensus/slots/Cargo.toml
```diff
@@ -19,7 +19,7 @@ sc-telemetry = { version = "2.0.0", path = "../../telemetry" }
 sp-consensus = { version = "0.8", path = "../../../primitives/consensus/common" }
 sp-inherents = { version = "2.0.0", path = "../../../primitives/inherents" }
 futures = "0.3.1"
-futures-timer = "2.0"
+futures-timer = "3.0.1"
 parking_lot = "0.10.0"
 log = "0.4.8"
 
```

### client/finality-grandpa/Cargo.toml
```diff
@@ -8,7 +8,7 @@ license = "GPL-3.0"
 [dependencies]
 fork-tree = { version = "2.0.0", path = "../../utils/fork-tree" }
 futures = "0.3.1"
-futures-timer = "2.0.2"
+futures-timer = "3.0.1"
 log = "0.4.8"
 parking_lot = "0.10.0"
 rand = "0.7.2"
```
