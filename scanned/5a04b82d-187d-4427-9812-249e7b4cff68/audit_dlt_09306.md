# [?] fix(forge): do not panic if create fork err (#10231)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2025-04-03
Source: https://github.com/foundry-rs/foundry/commit/58cae24dff2876f09433386b071c7bdb3ddafa50
Type: security-commit

## Details
fix(forge): do not panic if create fork err (#10231)

fix: propagate error on backend spawn fork

## Patch
### crates/cast/src/cmd/call.rs
```diff
@@ -198,8 +198,14 @@ impl CallArgs {
                     InternalTraceMode::None
                 })
                 .with_state_changes(shell::verbosity() > 4);
-            let mut executor =
-                TracingExecutor::new(env, fork, evm_version, trace_mode, odyssey, create2_deployer);
+            let mut executor = TracingExecutor::new(
+                env,
+                fork,
+                evm_version,
+                trace_mode,
+                odyssey,
+                create2_deployer,
+            )?;
 
             let value = tx.value.unwrap_or_default();
             let input = tx.inner.input.into_input().unwrap_or_default();
```

### crates/cast/src/cmd/run.rs
```diff
@@ -186,7 +186,7 @@ impl RunArgs {
             trace_mode,
             odyssey,
             create2_deployer,
-        );
+        )?;
         let mut env =
             EnvWithHandlerCfg::new_with_spec_id(Box::new(env.clone()), executor.spec_id());
 
```

### crates/chisel/src/executor.rs
```diff
@@ -133,7 +133,7 @@ impl SessionSource {
                 };
 
                 // Create a new runner
-                let mut runner = self.prepare_runner(final_pc).await;
+                let mut runner = self.prepare_runner(final_pc).await?;
 
                 // Return [ChiselResult] or bubble up error
                 runner.run(bytecode.into_owned())
@@ -311,7 +311,7 @@ impl SessionSource {
     /// ### Returns
     ///
     /// A configured [ChiselRunner]
-    async fn prepare_runner(&mut self, final_pc: usize) -> ChiselRunner {
+    async fn prepare_runner(&mut self, final_pc: usize) -> Result<ChiselRunner> {
         let env =
             self.config.evm_opts.evm_env().await.expect("Could not instantiate fork environment");
 
@@ -320,7 +320,7 @@ impl SessionSource {
             Some(backend) => backend,
             None => {
                 let fork = self.config.evm_opts.get_fork(&self.config.foundry_config, env.clone());
-                let backend = Backend::spawn(fork);
+                let backend = Backend::spawn(fork)?;
                 self.config.backend = Some(backend.clone());
                 backend
             }
@@ -346,7 +346,7 @@ impl SessionSource {
 
         // Create a [ChiselRunner] with a default balance of [U256::MAX] and
         // the sender [Address::zero].
-        ChiselRunner::new(executor, U256::MAX, Address::ZERO, self.config.calldata.clone())
+        Ok(ChiselRunner::new(executor, U256::MAX, Address::ZERO, self.config.calldata.clone()))
     }
 }
 
```

### crates/evm/core/src/backend/mod.rs
```diff
@@ -461,7 +461,7 @@ impl Backend {
     ///
     /// If `fork` is `Some` this will use a `fork` database, otherwise with an in-memory
     /// database.
-    pub fn spawn(fork: Option<CreateFork>) -> Self {
+    pub fn spawn(fork: Option<CreateFork>) -> eyre::Result<Self> {
         Self::new(MultiFork::spawn(), fork)
     }
 
@@ -471,7 +471,7 @@ impl Backend {
     /// database.
     ///
     /// Prefer using [`spawn`](Self::spawn) instead.
-    pub fn new(forks: MultiFork, fork: Option<CreateFork>) -> Self {
+    pub fn new(forks: MultiFork, fork: Option<CreateFork>) -> eyre::Result<Self> {
         trace!(target: "backend", forking_mode=?fork.is_some(), "creating executor backend");
         // Note: this will take of registering the `fork`
         let inner = BackendInner {
@@ -488,8 +488,7 @@ impl Backend {
         };
 
         if let Some(fork) = fork {
-            let (fork_id, fork, _) =
-                backend.forks.create_fork(fork).expect("Unable to create fork");
+            let (fork_id, fork, _) = backend.forks.create_fork(fork)?;
             let fork_db = ForkDB::new(fork);
             let fork_ids = backend.inner.insert_new_fork(
                 fork_id.clone(),
@@ -502,17 +501,21 @@ impl Backend {
 
         trace!(target: "backend", forking_mode=? backend.active_fork_ids.is_some(), "created executor backend");
 
-        backend
+        Ok(backend)
     }
 
     /// Creates a new instance of `Backend` with fork added to the fork database and sets the fork
     /// as active
-    pub(crate) fn new_with_fork(id: &ForkId, fork: Fork, journaled_state: JournaledState) -> Self {
-        let mut backend = Self::spawn(None);
+    pub(crate) fn new_with_fork(
+        id: &ForkId,
+        fork: Fork,
+        journaled_state: JournaledState,
+    ) -> eyre::Result<Self> {
+        let mut backend = Self::spawn(None)?;
         let fork_ids = backend.inner.insert_new_fork(id.clone(), fork.db, journaled_state);
         backend.inner.launched_with_fork = Some((id.clone(), fork_ids.0, fork_ids.1));
         backend.active_fork_ids = Some(fork_ids);
-        backend
+        Ok(backend)
     }
 
     /// Creates a new instance with a `BackendDatabase::InMemory` cache layer for the `CacheDB`
@@ -1944,7 +1947,7 @@ fn commit_transaction(
         let fork = fork.clone();
         let journaled_state = journaled_state.clone();
         let depth = journaled_state.depth;
-        let mut db = Backend::new_with_fork(fork_id, fork, journaled_state);
+        let mut db = Backend::new_with_fork(fork_id, fork, journaled_state)?;
 
         let mut evm = crate::utils::new_evm_with_inspector(&mut db as _, env, inspector);
         // Adjust inner EVM depth to ensure that inspectors receive accurate data.
@@ -2026,7 +2029,7 @@ mod tests {
             evm_opts,
         };
 
-        let backend = Backend::spawn(Some(fork));
+        let backend = Backend::spawn(Some(fork)).unwrap();
 
         // some rng contract from etherscan
         let address: Address = "63091244180ae240c87d1f528f5f269134cb07b3".parse().unwrap();
```

### crates/evm/evm/src/executors/trace.rs
```diff
@@ -20,9 +20,9 @@ impl TracingExecutor {
         trace_mode: TraceMode,
         odyssey: bool,
         create2_deployer: Address,
-    ) -> Self {
-        let db = Backend::spawn(fork);
-        Self {
+    ) -> eyre::Result<Self> {
+        let db = Backend::spawn(fork)?;
+        Ok(Self {
             // configures a bare version of the evm executor: no cheatcode inspector is enabled,
             // tracing will be enabled only for the targeted transaction
             executor: ExecutorBuilder::new()
@@ -31,7 +31,7 @@ impl TracingExecutor {
                 })
                 .spec_id(evm_spec_id(version.unwrap_or_default(), odyssey))
                 .build(env, db),
-        }
+        })
     }
 
     /// Returns the spec id of the executor
```

### crates/forge/src/cmd/test/mod.rs
```diff
@@ -471,7 +471,7 @@ impl TestArgs {
 
         // Run tests in a non-streaming fashion and collect results for serialization.
         if !self.gas_report && !self.summary && shell::is_json() {
-            let mut results = runner.test_collect(filter);
+            let mut results = runner.test_collect(filter)?;
             results.values_mut().for_each(|suite_result| {
                 for test_result in suite_result.test_results.values_mut() {
                     if verbosity >= 2 {
@@ -488,7 +488,7 @@ impl TestArgs {
         }
 
         if self.junit {
-            let results = runner.test_collect(filter);
+            let results = runner.test_collect(filter)?;
             sh_println!("{}", junit_xml_report(&results, verbosity).to_string()?)?;
             return Ok(TestOutcome::new(results, self.allow_failure));
         }
```

### crates/forge/src/multi_runner.rs
```diff
@@ -136,8 +136,11 @@ impl MultiContractRunner {
     /// The same as [`test`](Self::test), but returns the results instead of streaming them.
     ///
     /// Note that this method returns only when all tests have been executed.
-    pub fn test_collect(&mut self, filter: &dyn TestFilter) -> BTreeMap<String, SuiteResult> {
-        self.test_iter(filter).collect()
+    pub fn test_collect(
+        &mut self,
+        filter: &dyn TestFilter,
+    ) -> Result<BTreeMap<String, SuiteResult>> {
+        Ok(self.test_iter(filter)?.collect())
     }
 
     /// Executes _all_ tests that match the given `filter`.
@@ -148,10 +151,10 @@ impl MultiContractRunner {
     pub fn test_iter(
         &mut self,
         filter: &dyn TestFilter,
-    ) -> impl Iterator<Item = (String, SuiteResult)> {
+    ) -> Result<impl Iterator<Item = (String, SuiteResult)>> {
         let (tx, rx) = mpsc::channel();
-        self.test(filter, tx, false);
-        rx.into_iter()
+        self.test(filter, tx, false)?;
+        Ok(rx.into_iter())
     }
 
     /// Executes _all_ tests that match the given `filter`.
@@ -165,12 +168,12 @@ impl MultiContractRunner {
         filter: &dyn TestFilter,
         tx: mpsc::Sender<(String, SuiteResult)>,
         show_progress: bool,
-    ) {
+    ) -> Result<()> {
         let tokio_handle = tokio::runtime::Handle::current();
         trace!("running all tests");
 
         // The DB backend that serves all the data.
-        let db = Backend::spawn(self.fork.take());
+        let db = Backend::spawn(self.fork.take())?;
 
         let find_timer = Instant::now();
         let contracts = self.matching_contracts(filter).collect::<Vec<_>>();
@@ -221,6 +224,8 @@ impl MultiContractRunner {
                 let _ = tx.send((id.identifier(), result));
             })
         }
+
+        Ok(())
     }
 
     fn run_test_suite(
```

### crates/forge/tests/it/config.rs
```diff
@@ -46,7 +46,7 @@ impl TestConfig {
     }
 
     /// Executes the test runner
-    pub fn test(&mut self) -> BTreeMap<String, SuiteResult> {
+    pub fn test(&mut self) -> eyre::Result<BTreeMap<String, SuiteResult>> {
         self.runner.test_collect(&self.filter)
     }
 
@@ -60,7 +60,7 @@ impl TestConfig {
     ///    * filter matched 0 test cases
     ///    * a test results deviates from the configured `should_fail` setting
     pub async fn try_run(&mut self) -> eyre::Result<()> {
-        let suite_result = self.test();
+        let suite_result = self.test()?;
         if suite_result.is_empty() {
             eyre::bail!("empty test result");
         }
```

### crates/forge/tests/it/core.rs
```diff
@@ -13,7 +13,7 @@ use std::{collections::BTreeMap, env};
 async fn test_core() {
     let filter = Filter::new(".*", ".*", ".*core");
     let mut runner = TEST_DATA_DEFAULT.runner();
-    let results = runner.test_collect(&filter);
+    let results = runner.test_collect(&filter).unwrap();
 
     assert_multiple(
         &results,
@@ -77,7 +77,7 @@ async fn test_core() {
 async fn test_linking() {
     let filter = Filter::new(".*", ".*", ".*linking");
     let mut runner = TEST_DATA_DEFAULT.runner();
-    let results = runner.test_collect(&filter);
+    let results = runner.test_collect(&filter).unwrap();
 
     assert_multiple(
         &results,
@@ -111,7 +111,7 @@ async fn test_linking() {
 async fn test_logs() {
     let filter = Filter::new(".*", ".*", ".*logs");
     let mut runner = TEST_DATA_DEFAULT.runner();
-    let results = runner.test_collect(&filter);
+    let results = runner.test_collect(&filter).unwrap();
 
     assert_multiple(
         &results,
@@ -722,7 +722,7 @@ async fn test_env_vars() {
 async fn test_doesnt_run_abstract_contract() {
     let filter = Filter::new(".*", ".*", ".*Abstract.t.sol".to_string().as_str());
     let mut runner = TEST_DATA_DEFAULT.runner();
-    let results = runner.test_collect(&filter);
+    let results = runner.test_collect(&filter).unwrap();
     assert!(!results.contains_key("default/core/Abstract.t.sol:AbstractTestBase"));
     assert!(results.contains_key("default/core/Abstract.t.sol:AbstractTest"));
 }
@@ -731,7 +731,7 @@ async fn test_doesnt_run_abstract_contract() {
 async fn test_trace() {
     let filter = Filter::new(".*", ".*", ".*trace");
     let mut runner = TEST_DATA_DEFAULT.tracing_runner();
-    let suite_result = runner.test_collect(&filter);
+    let suite_result = runner.test_collect(&filter).unwrap();
 
     // TODO: This trace test is very basic - it is probably a good candidate for snapshot
     // testing.
@@ -764,7 +764,7 @@ async fn test_assertions_revert_false() {
     let mut runner = TEST_DATA_DEFAULT.runner_with(|config| {
         config.assertions_revert = false;
     });
-    let results = runner.test_collect(&filter);
+    let results = runner.test_collect(&filter).unwrap();
 
     assert_multiple(
         &results,
@@ -790,7 +790,7 @@ async fn test_legacy_assertions() {
     let mut runner = TEST_DATA_DEFAULT.runner_with(|config| {
         config.legacy_assertions = true;
     });
-    let results = runner.test_collect(&filter);
+    let results = runner.test_collect(&filter).unwrap();
 
     assert_multiple(
         &results,
@@ -809,7 +809,7 @@ async fn test_legacy_assertions() {
 #[tokio::test(flavor = "multi_thread")]
 async fn test_before_setup_with_selfdestruct() {
     let filter = Filter::new(".*", ".*BeforeTestSelfDestructTest", ".*");
-    let results = TEST_DATA_PARIS.runner().test_collect(&filter);
+    let results = TEST_DATA_PARIS.runner().test_collect(&filter).unwrap();
 
     assert_multiple(
         &results,
```

### crates/forge/tests/it/fork.rs
```diff
@@ -19,7 +19,7 @@ async fn test_cheats_fork_revert() {
         &format!(".*cheats{RE_PATH_SEPARATOR}Fork"),
     );
     let mut runner = TEST_DATA_DEFAULT.runner();
-    let suite_result = runner.test_collect(&filter);
+    let suite_result = runner.test_collect(&filter).unwrap();
     assert_eq!(suite_result.len(), 1);
 
     for (_, SuiteResult { test_results, .. }) in suite_result {
```

### crates/forge/tests/it/fuzz.rs
```diff
@@ -16,7 +16,7 @@ async fn test_fuzz() {
         .exclude_tests(r"invariantCounter|testIncrement\(address\)|testNeedle\(uint256\)|testSuccessChecker\(uint256\)|testSuccessChecker2\(int256\)|testSuccessChecker3\(uint32\)|testStorageOwner\(address\)|testImmutableOwner\(address\)")
         .exclude_paths("invariant");
     let mut runner = TEST_DATA_DEFAULT.runner();
-    let suite_result = runner.test_collect(&filter);
+    let suite_result = runner.test_collect(&filter).unwrap();
 
     assert!(!suite_result.is_empty());
 
@@ -53,7 +53,7 @@ async fn test_successful_fuzz_cases() {
         .exclude_tests(r"invariantCounter|testIncrement\(address\)|testNeedle\(uint256\)")
         .exclude_paths("invariant");
     let mut runner = TEST_DATA_DEFAULT.runner();
-    let suite_result = runner.test_collect(&filter);
+    let suite_result = runner.test_collect(&filter).unwrap();
 
     assert!(!suite_result.is_empty());
 
@@ -88,7 +88,7 @@ async fn test_fuzz_collection() {
         config.fuzz.runs = 1000;
         config.fuzz.seed = Some(U256::from(6u32));
     });
-    let results = runner.test_collect(&filter);
+    let results = runner.test_collect(&filter).unwrap();
 
     assert_multiple(
         &results,
@@ -122,6 +122,7 @@ async fn test_persist_fuzz_failure() {
             });
             runner
                 .test_collect(&filter)
+                .unwrap()
                 .get("default/fuzz/FuzzFailurePersist.t.sol:FuzzFailurePersistTest")
                 .unwrap()
                 .test_results
```

### crates/forge/tests/it/inline.rs
```diff
@@ -8,7 +8,7 @@ use foundry_test_utils::Filter;
 async fn inline_config_run_fuzz() {
     let filter = Filter::new(".*", ".*", ".*inline/FuzzInlineConf.t.sol");
     let mut runner = TEST_DATA_DEFAULT.runner();
-    let result = runner.test_collect(&filter);
+    let result = runner.test_collect(&filter).unwrap();
     let results = result
         .into_iter()
         .flat_map(|(path, r)| {
@@ -50,7 +50,7 @@ async fn inline_config_run_invariant() {
 
     let filter = Filter::new(".*", ".*", ".*inline/InvariantInlineConf.t.sol");
     let mut runner = TEST_DATA_DEFAULT.runner();
-    let result = runner.test_collect(&filter);
+    let result = runner.test_collect(&filter).unwrap();
 
     let suite_result_1 = result.get(&format!("{ROOT}:InvariantInlineConf")).expect("Result exists");
     let suite_result_2 =
```
