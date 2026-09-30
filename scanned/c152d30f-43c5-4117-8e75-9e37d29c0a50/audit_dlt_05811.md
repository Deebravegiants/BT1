# [?] Prevent unsoundness in environments with broken `madvise(MADV_DONTNEED)` (#11722)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2022-06-28
Source: https://github.com/paritytech/substrate/commit/ee3eb8f2448cc1bb978c5d1564febd351c128bb0
Type: security-commit

## Details
Prevent unsoundness in environments with broken `madvise(MADV_DONTNEED)` (#11722)

* Prevend unsoundness in environments with broken `madvise(MADV_DONTNEED)`

* Add the `std` feature to `rustix` dependency

Apparently not having this breaks compilation on non-nightly toolchains.

* Autodetect the page size when checking whether `madvise` works

* Only make sure that the madvice check doesn't return `Err`

## Patch
### Cargo.lock
```diff
@@ -3113,6 +3113,12 @@ version = "0.5.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "ec58677acfea8a15352d42fc87d11d63596ade9239e0a7c9352914417515dbe6"
 
+[[package]]
+name = "io-lifetimes"
+version = "0.7.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "24c3f4eff5495aee4c0399d7b6a0dc2b6e81be84242ffbfcf253ebacccc1d0cb"
+
 [[package]]
 name = "ip_network"
 version = "0.4.1"
@@ -3411,9 +3417,9 @@ checksum = "3576a87f2ba00f6f106fdfcd16db1d698d648a26ad8e0573cad8537c3c362d2a"
 
 [[package]]
 name = "libc"
-version = "0.2.121"
+version = "0.2.126"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "efaa7b300f3b5fe8eb6bf21ce3895e1751d9665086af2d64b42f19701015ff4f"
+checksum = "349d5a591cd28b49e1d1037471617a32ddcda5731b99419008085f72d5a53836"
 
 [[package]]
 name = "libgit2-sys"
@@ -4108,6 +4114,12 @@ version = "0.0.42"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "5284f00d480e1c39af34e72f8ad60b94f47007e3481cd3b731c1d67190ddc7b7"
 
+[[package]]
+name = "linux-raw-sys"
+version = "0.0.46"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "d4d2456c373231a208ad294c33dc5bff30051eafd954cd4caae83a712b12854d"
+
 [[package]]
 name = "lite-json"
 version = "0.1.3"
@@ -6712,7 +6724,7 @@ dependencies = [
  "libc",
  "redox_syscall",
  "smallvec",
- "windows-sys",
+ "windows-sys 0.32.0",
 ]
 
 [[package]]
@@ -7850,12 +7862,26 @@ checksum = "938a344304321a9da4973b9ff4f9f8db9caf4597dfd9dda6a60b523340a0fff0"
 dependencies = [
  "bitflags",
  "errno",
- "io-lifetimes",
+ "io-lifetimes 0.5.3",
  "libc",
- "linux-raw-sys",
+ "linux-raw-sys 0.0.42",
  "winapi",
 ]
 
+[[package]]
+name = "rustix"
+version = "0.35.6"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "ef258c11e17f5c01979a10543a30a4e12faef6aab217a74266e747eefa3aed88"
+dependencies = [
+ "bitflags",
+ "errno",
+ "io-lifetimes 0.7.2",
+ "libc",
+ "linux-raw-sys 0.0.46",
+ "windows-sys 0.36.1",
+]
+
 [[package]]
 name = "rustls"
 version = "0.20.2"
@@ -8479,9 +8505,11 @@ dependencies = [
  "cfg-if 1.0.0",
  "libc",
  "log",
+ "once_cell",
  "parity-scale-codec",
  "parity-wasm 0.42.2",
  "paste 1.0.6",
+ "rustix 0.35.6",
  "sc-allocator",
  "sc-executor-common",
  "sc-runtime-test",
@@ -11972,7 +12000,7 @@ dependencies = [
  "directories-next",
  "file-per-thread-logger",
  "log",
- "rustix",
+ "rustix 0.33.7",
  "serde",
  "sha2 0.9.8",
  "toml",
@@ -12038,7 +12066,7 @@ dependencies = [
  "object 0.28.3",
  "region 2.2.0",
  "rustc-demangle",
- "rustix",
+ "rustix 0.33.7",
  "serde",
  "target-lexicon",
  "thiserror",
@@ -12056,7 +12084,7 @@ checksum = "e6d5dd480cc6dc0a401653e45b79796a3317f8228990d84bc2271bdaf0810071"
 dependencies = [
  "lazy_static",
  "object 0.28.3",
- "rustix",
+ "rustix 0.33.7",
 ]
 
 [[package]]
@@ -12078,7 +12106,7 @@ dependencies = [
  "more-asserts",
  "rand 0.8.4",
  "region 2.2.0",
- "rustix",
+ "rustix 0.33.7",
  "thiserror",
  "wasmtime-environ",
  "wasmtime-jit-debug",
@@ -12226,6 +12254,19 @@ dependencies = [
  "windows_x86_64_msvc 0.32.0",
 ]
 
+[[package]]
+name = "windows-sys"
+version = "0.36.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "ea04155a16a59f9eab786fe12a4a450e75cdb175f9e0d80da1e17db09f55b8d2"
+dependencies = [
+ "windows_aarch64_msvc 0.36.1",
+ "windows_i686_gnu 0.36.1",
+ "windows_i686_msvc 0.36.1",
+ "windows_x86_64_gnu 0.36.1",
+ "windows_x86_64_msvc 0.36.1",
+]
+
 [[package]]
 name = "windows_aarch64_msvc"
 version = "0.29.0"
@@ -12238,6 +12279,12 @@ version = "0.32.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d8e92753b1c443191654ec532f14c199742964a061be25d77d7a96f09db20bf5"
 
+[[package]]
+name = "windows_aarch64_msvc"
+version = "0.36.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "9bb8c3fd39ade2d67e9874ac4f3db21f0d710bee00fe7cab16949ec184eeaa47"
+
 [[package]]
 name = "windows_i686_gnu"
 version = "0.29.0"
@@ -12250,6 +12297,12 @@ version = "0.32.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "6a711c68811799e017b6038e0922cb27a5e2f43a2ddb609fe0b6f3eeda9de615"
 
+[[package]]
+name = "windows_i686_gnu"
+version = "0.36.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "180e6ccf01daf4c426b846dfc66db1fc518f074baa793aa7d9b9aaeffad6a3b6"
+
 [[package]]
 name = "windows_i686_msvc"
 version = "0.29.0"
@@ -12262,6 +12315,12 @@ version = "0.32.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "146c11bb1a02615db74680b32a68e2d61f553cc24c4eb5b4ca10311740e44172"
 
+[[package]]
+name = "windows_i686_msvc"
+version = "0.36.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "e2e7917148b2812d1eeafaeb22a97e4813dfa60a3f8f78ebe204bcc88f12f024"
+
 [[package]]
 name = "windows_x86_64_gnu"
 version = "0.29.0"
@@ -12274,6 +12333,12 @@ version = "0.32.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c912b12f7454c6620635bbff3450962753834be2a594819bd5e945af18ec64bc"
 
+[[package]]
+name = "windows_x86_64_gnu"
+version = "0.36.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "4dcd171b8776c41b97521e5da127a2d86ad280114807d0b2ab1e462bc764d9e1"
+
 [[package]]
 name = "windows_x86_64_msvc"
 version = "0.29.0"
@@ -12286,6 +12351,12 @@ version = "0.32.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "504a2476202769977a040c6364301a3f65d0cc9e3fb08600b2bda150a0488316"
 
+[[package]]
+name = "windows_x86_64_msvc"
+version = "0.36.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "c811ca4a8c853ef420abd8592ba53ddbbac90410fab6903b3e79972a631f7680"
+
 [[package]]
 name = "winreg"
 version = "0.7.0"
```

### client/executor/wasmtime/Cargo.toml
```diff
@@ -32,6 +32,10 @@ sp-runtime-interface = { version = "6.0.0", path = "../../../primitives/runtime-
 sp-sandbox = { version = "0.10.0-dev", path = "../../../primitives/sandbox" }
 sp-wasm-interface = { version = "6.0.0", features = ["wasmtime"], path = "../../../primitives/wasm-interface" }
 
+[target.'cfg(target_os = "linux")'.dependencies]
+rustix = { version = "0.35.6", default-features = false, features = ["std", "mm", "fs", "param"] }
+once_cell = "1.12.0"
+
 [dev-dependencies]
 wat = "1.0"
 sc-runtime-test = { version = "2.0.0", path = "../runtime-test" }
```

### client/executor/wasmtime/src/runtime.rs
```diff
@@ -21,7 +21,7 @@
 use crate::{
 	host::HostState,
 	instance_wrapper::{EntryPoint, InstanceWrapper},
-	util,
+	util::{self, replace_strategy_if_broken},
 };
 
 use sc_allocator::FreeingBumpHeapAllocator;
@@ -411,6 +411,7 @@ fn common_config(semantics: &Semantics) -> std::result::Result<wasmtime::Config,
 /// See [here][stack_height] for more details of the instrumentation
 ///
 /// [stack_height]: https://github.com/paritytech/wasm-utils/blob/d9432baf/src/stack_height/mod.rs#L1-L50
+#[derive(Clone)]
 pub struct DeterministicStackLimit {
 	/// A number of logical "values" that can be pushed on the wasm stack. A trap will be triggered
 	/// if exceeded.
@@ -468,6 +469,7 @@ enum InternalInstantiationStrategy {
 	Builtin,
 }
 
+#[derive(Clone)]
 pub struct Semantics {
 	/// The instantiation strategy to use.
 	pub instantiation_strategy: InstantiationStrategy,
@@ -598,11 +600,13 @@ where
 /// [`create_runtime_from_artifact`] to get more details.
 unsafe fn do_create_runtime<H>(
 	code_supply_mode: CodeSupplyMode<'_>,
-	config: Config,
+	mut config: Config,
 ) -> std::result::Result<WasmtimeRuntime, WasmError>
 where
 	H: HostFunctions,
 {
+	replace_strategy_if_broken(&mut config.semantics.instantiation_strategy);
+
 	let mut wasmtime_config = common_config(&config.semantics)?;
 	if let Some(ref cache_path) = config.cache_path {
 		if let Err(reason) = setup_wasmtime_caching(cache_path, &mut wasmtime_config) {
@@ -719,9 +723,12 @@ pub fn prepare_runtime_artifact(
 	blob: RuntimeBlob,
 	semantics: &Semantics,
 ) -> std::result::Result<Vec<u8>, WasmError> {
-	let blob = prepare_blob_for_compilation(blob, semantics)?;
+	let mut semantics = semantics.clone();
+	replace_strategy_if_broken(&mut semantics.instantiation_strategy);
+
+	let blob = prepare_blob_for_compilation(blob, &semantics)?;
 
-	let engine = Engine::new(&common_config(semantics)?)
+	let engine = Engine::new(&common_config(&semantics)?)
 		.map_err(|e| WasmError::Other(format!("cannot create the engine: {}", e)))?;
 
 	engine
```

### client/executor/wasmtime/src/util.rs
```diff
@@ -16,7 +16,7 @@
 // You should have received a copy of the GNU General Public License
 // along with this program. If not, see <https://www.gnu.org/licenses/>.
 
-use crate::runtime::StoreData;
+use crate::{runtime::StoreData, InstantiationStrategy};
 use sc_executor_common::{
 	error::{Error, Result},
 	util::checked_range,
@@ -98,3 +98,94 @@ pub(crate) fn write_memory_from(
 	memory[range].copy_from_slice(data);
 	Ok(())
 }
+
+/// Checks whether the `madvise(MADV_DONTNEED)` works as expected.
+///
+/// In certain environments (e.g. when running under the QEMU user-mode emulator)
+/// this syscall is broken.
+#[cfg(target_os = "linux")]
+fn is_madvise_working() -> std::result::Result<bool, String> {
+	let page_size = rustix::param::page_size();
+
+	unsafe {
+		// Allocate two memory pages.
+		let pointer = rustix::mm::mmap_anonymous(
+			std::ptr::null_mut(),
+			2 * page_size,
+			rustix::mm::ProtFlags::READ | rustix::mm::ProtFlags::WRITE,
+			rustix::mm::MapFlags::PRIVATE,
+		)
+		.map_err(|error| format!("mmap failed: {}", error))?;
+
+		// Dirty them both.
+		std::ptr::write_volatile(pointer.cast::<u8>(), b'A');
+		std::ptr::write_volatile(pointer.cast::<u8>().add(page_size), b'B');
+
+		// Clear the first page.
+		let result_madvise =
+			rustix::mm::madvise(pointer, page_size, rustix::mm::Advice::LinuxDontNeed)
+				.map_err(|error| format!("madvise failed: {}", error));
+
+		// Fetch the values.
+		let value_1 = std::ptr::read_volatile(pointer.cast::<u8>());
+		let value_2 = std::ptr::read_volatile(pointer.cast::<u8>().add(page_size));
+
+		let result_munmap = rustix::mm::munmap(pointer, 2 * page_size)
+			.map_err(|error| format!("munmap failed: {}", error));
+
+		result_madvise?;
+		result_munmap?;
+
+		// Verify that the first page was cleared, while the second one was not.
+		Ok(value_1 == 0 && value_2 == b'B')
+	}
+}
+
+#[cfg(test)]
+#[cfg(target_os = "linux")]
+#[test]
+fn test_is_madvise_working_check_does_not_fail() {
+	assert!(is_madvise_working().is_ok());
+}
+
+/// Checks whether a given instantiation strategy can be safely used, and replaces
+/// it with a slower (but sound) alternative if it isn't.
+#[cfg(target_os = "linux")]
+pub(crate) fn replace_strategy_if_broken(strategy: &mut InstantiationStrategy) {
+	let replacement_strategy = match *strategy {
+		// These strategies don't need working `madvise`.
+		InstantiationStrategy::Pooling | InstantiationStrategy::RecreateInstance => return,
+
+		// These strategies require a working `madvise` to be sound.
+		InstantiationStrategy::PoolingCopyOnWrite => InstantiationStrategy::Pooling,
+		InstantiationStrategy::RecreateInstanceCopyOnWrite |
+		InstantiationStrategy::LegacyInstanceReuse => InstantiationStrategy::RecreateInstance,
+	};
+
+	use once_cell::sync::OnceCell;
+	static IS_OK: OnceCell<bool> = OnceCell::new();
+
+	let is_ok = IS_OK.get_or_init(|| {
+		let is_ok = match is_madvise_working() {
+			Ok(is_ok) => is_ok,
+			Err(error) => {
+				// This should never happen.
+				log::warn!("Failed to check whether `madvise(MADV_DONTNEED)` works: {}", error);
+				false
+			}
+		};
+
+		if !is_ok {
+			log::warn!("You're running on a system with a broken `madvise(MADV_DONTNEED)` implementation. This will result in lower performance.");
+		}
+
+		is_ok
+	});
+
+	if !is_ok {
+		*strategy = replacement_strategy;
+	}
+}
+
+#[cfg(not(target_os = "linux"))]
+pub(crate) fn replace_strategy_if_broken(_: &mut InstantiationStrategy) {}
```
