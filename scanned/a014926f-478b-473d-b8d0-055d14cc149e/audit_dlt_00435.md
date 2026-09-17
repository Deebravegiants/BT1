# [?] fix(grandpa): GRANDPA panic when a change block is finalized concurrently during justification import (#12506)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2026-08-18
Source: https://github.com/paritytech/polkadot-sdk/commit/34a14dab9628f029a0ef0c457f4fa3a51cd6669a
Type: security-commit

## Details
fix(grandpa): GRANDPA panic when a change block is finalized concurrently during justification import (#12506)

#### Description
A GRANDPA node can panic during block import with:
```
panicked at 'returns Ok when no authority set change should be enacted; qed;', /root/.cargo/git/checkouts/polkadot-sdk-dee0edd6eefa0594/2e4dd0b/substrate/client/consensus/grandpa/src/import.rs:859
```
This is a time-of-check/time-of-use race in
`GrandpaBlockImport::import_justification`. When importing a
justification for a block that enacts a standard authority set change,
the method:

1. reads the current set id and authorities and verifies the
justification against them (acquiring and **releasing** the
authority-set lock), then
2. separately calls `environment::finalize_block`, which re-acquires the
lock to enact the change.

If another finalizer (the voter acting on a gossiped commit, or a
justification imported via sync) finalizes the **same** block in the
window between (1) and (2), then `finalize_block` short-circuits on its
"already finalized in the canonical chain" guard and returns `Ok(())`,
while the caller was told the block enacts a change (`enacts_change ==
true`). The `Ok(_)` arm then trips `assert!(!enacts_change)` and the
node panics.

The window is widened by anything that delays block import relative to
finality — e.g. a `BlockAnnounceValidator` that returns an error/skip
for a while — which lines the two finalizers up on a session-rotation
(change-enacting) block. Observed in logs as the import-path
`finalize_block` hitting the re-finalization guard right after the voter
applied the change:

```
2026-06-29 13:56:48 2026-06-29 11:56:48.072 DEBUG tokio-rt-worker grandpa: Completed round 20, state = State { prevote_ghost: Some((0x8852da3251a16eddb6b583e0e7fdf7c1eeb627b275a12b90c5fefba29d6d95cd, 26)), finalized: Some((0x8852da3251a16eddb6b583e0e7fdf7c1eeb627b275a12b90c5fefba29d6d95cd, 26)), estimate: Some((0x8852da3251a16eddb6b583e0e7fdf7c1eeb627b275a12b90c5fefba29d6d95cd, 26)), completable: true }, step = None    
2026-06-29 13:56:48 2026-06-29 11:56:48.072 DEBUG tokio-rt-worker grandpa: Round 20: prevotes: 3/3/3 weight, 3/3 actual    
2026-06-29 13:56:48 2026-06-29 11:56:48.072 DEBUG tokio-rt-worker grandpa: Round 20: precommits: 3/3/3 weight, 3/3 actual    
2026-06-29 13:56:48 2026-06-29 11:56:48.072 DEBUG tokio-rt-worker grandpa: Voter cool-camp-1893 concluded round 20 in set 5. Estimate = Some(26), Finalized in round = Some(26)    
2026-06-29 13:56:48 2026-06-29 11:56:48.074  INFO tokio-rt-worker grandpa: 👴 Applying authority set change scheduled at block #27    
2026-06-29 13:56:48 2026-06-29 11:56:48.074 DEBUG tokio-rt-worker grandpa: Finalizing blocks up to (27, 0x254d…ff4c)    
2026-06-29 13:56:48 2026-06-29 11:56:48.074  INFO tokio-rt-worker grandpa: 👴 Applying GRANDPA set change to new set [(Public(d17c2d7823ebf260fd138f2d7e27d114c0145d968b5ff5006125f2414fadae69 (5GoNkf6W...)), 1), (Public(439660b36c6c03afafca027b910b4fecf99801834c62a5e6006f27d978de234f (5DbKjhNL...)), 1), (Public(88dc3417d5058ec4b4503e0c12ea1a0a89be200fe98922423d4334014fa6b0ee (5FA9nQDV...)), 1)]    
2026-06-29 13:56:48 2026-06-29 11:56:48.074  INFO tokio-rt-worker substrate: 🏆 Imported #27 (0x8852…95cd → 0x254d…ff4c)    
2026-06-29 13:56:48 2026-06-29 11:56:48.075 DEBUG tokio-rt-worker sync: Reannouncing block 0x254da93bc9de56fd122fd860479234621221d9635aaad9ec384db8de3a87ff4c is_best: true    
2026-06-29 13:56:48 2026-06-29 11:56:48.075 DEBUG tokio-rt-worker sync: New best block imported 0x254da93bc9de56fd122fd860479234621221d9635aaad9ec384db8de3a87ff4c/#27    
2026-06-29 13:56:48 2026-06-29 11:56:48.075  WARN tokio-rt-worker grandpa: Re-finalized block #0x254da93bc9de56fd122fd860479234621221d9635aaad9ec384db8de3a87ff4c (27) in the canonical chain, current best finalized is #27    
2026-06-29 13:56:48 2026-06-29 11:56:48.075 DEBUG tokio-rt-worker grandpa: cool-camp-1893: Starting new voter with set ID 6    
2026-06-29 13:56:48 2026-06-29 11:56:48.078  INFO tokio-rt-worker committee-membership: Session 6: this node IS NOT in the committee for this session (local AURA keys: ["0xb0eb82cbdf9f92c384d88ea14de34aa38f7d05b0131b7b9bc21bb3f395920c22"], committee size: 3).    
2026-06-29 13:56:48 
2026-06-29 13:56:48 ====================
2026-06-29 13:56:48 
2026-06-29 13:56:48 Version: 2.0.0-ceb0a384
2026-06-29 13:56:48 
2026-06-29 13:56:48    0: sp_panic_handler::set::{{closure}}
2026-06-29 13:56:48    1: <alloc::boxed::Box<dyn for<'a, 'b> core::ops::function::Fn<(&'a std::panic::PanicHookInfo<'b>,), Output = ()> + core::marker::Sync + core::marker::Send> as core::ops::function::Fn<(&std::panic::PanicHookInfo,)>>::call
2026-06-29 13:56:48              at rustc/59807616e1fa2540724bfbac14d7976d7e4a3860/library/alloc/src/boxed.rs:2254:9
2026-06-29 13:56:48       std::panicking::panic_with_hook
2026-06-29 13:56:48              at rustc/59807616e1fa2540724bfbac14d7976d7e4a3860/library/std/src/panicking.rs:833:13
2026-06-29 13:56:48    2: std::panicking::panic_handler::{closure#0}
2026-06-29 13:56:48              at rustc/59807616e1fa2540724bfbac14d7976d7e4a3860/library/std/src/panicking.rs:691:13
2026-06-29 13:56:48    3: std::sys::backtrace::__rust_end_short_backtrace::<std::panicking::panic_handler::{closure#0}, !>
2026-06-29 13:56:48              at rustc/59807616e1fa2540724bfbac14d7976d7e4a3860/library/std/src/sys/backtrace.rs:182:18
2026-06-29 13:56:48    4: __rustc::rust_begin_unwind
2026-06-29 13:56:48              at rustc/59807616e1fa2540724bfbac14d7976d7e4a3860/library/std/src/panicking.rs:689:5
2026-06-29 13:56:48    5: core::panicking::panic_fmt
2026-06-29 13:56:48              at rustc/59807616e1fa2540724bfbac14d7976d7e4a3860/library/core/src/panicking.rs:80:14
2026-06-29 13:56:48    6: sc_consensus_grandpa::import::GrandpaBlockImport<BE,Block,Client,SC>::import_justification
2026-06-29 13:56:48    7: <sc_consensus_grandpa::import::GrandpaBlockImport<BE,Block,Client,SC> as sc_consensus::block_import::BlockImport<Block>>::import_block::{{closure}}
2026-06-29 13:56:48    8: <alloc::boxed::Box<dyn sc_consensus::block_import::BlockImport<B>+Error = sp_consensus::error::Error+core::marker::Sync+core::marker::Send> as sc_consensus::block_import::BlockImport<B>>::import_block::{{closure}}
2026-06-29 13:56:48    9: futures_util::future::future::FutureExt::poll_unpin
2026-06-29 13:56:48   10: sc_consensus::import_queue::basic_queue::BlockImportWorker<B>::new::{{closure}}
2026-06-29 13:56:48   11: <futures_util::future::future::map::Map<Fut,F> as core::future::future::Future>::poll
2026-06-29 13:56:48   12: <sc_service::task_manager::prometheus_future::PrometheusFuture<T> as core::future::future::Future>::poll
2026-06-29 13:56:48   13: <tracing_futures::Instrumented<T> as core::future::future::Future>::poll
2026-06-29 13:56:48   14: tokio::runtime::context::runtime::enter_runtime
2026-06-29 13:56:48   15: <tokio::runtime::blocking::task::BlockingTask<T> as core::future::future::Future>::poll
2026-06-29 13:56:48   16: tokio::runtime::task::core::Core<T,S>::poll
2026-06-29 13:56:48   17: tokio::runtime::task::harness::Harness<T,S>::poll
2026-06-29 13:56:48   18: tokio::runtime::blocking::pool::Inner::run
2026-06-29 13:56:48   19: std::sys::backtrace::__rust_begin_short_backtrace
2026-06-29 13:56:48   20: core::ops::function::FnOnce::call_once{{vtable.shim}}
2026-06-29 13:56:48   21: <alloc::boxed::Box<dyn core::ops::function::FnOnce<(), Output = ()> + core::marker::Send> as core::ops::function::FnOnce<()>>::call_once
2026-06-29 13:56:48              at rustc/59807616e1fa2540724bfbac14d7976d7e4a3860/library/alloc/src/boxed.rs:2240:9
2026-06-29 13:56:48       <std::sys::thread::unix::Thread>::new::thread_start
2026-06-29 13:56:48              at rustc/59807616e1fa2540724bfbac14d7976d7e4a3860/library/std/src/sys/thread/unix.rs:118:17
2026-06-29 13:56:48   22: start_thread
2026-06-29 13:56:48   23: thread_start
2026-06-29 13:56:48 
2026-06-29 13:56:48 
2026-06-29 13:56:48 Thread 'tokio-rt-worker' panicked at 'returns Ok when no authority set change should be enacted; qed;', /root/.cargo/git/checkouts/polkadot-sdk-dee0edd6eefa0594/2e4dd0b/substrate/client/consensus/grandpa/src/import.rs:859
```

We do not know all possible paths to reproduce that, but the way we hit
it was with custom `BlockAnnounceValidator` returning for a while from
[BlockAnnounceValidator::validate](https://rustdocs.bsx.fi/sp_consensus/block_validation/trait.BlockAnnounceValidator.html#tymethod.validate)
an error, which is by sync mapped to `Skip` action
https://github.com/paritytech/polkadot-sdk/blob/9107f88f83300b98af2d212463c83c659596261c/substrate/client/network/sync/src/block_announce_validator.rs#L210
If this gap is long enough to casually go through session boundary, then
there occurs mentioned race condition once `BlockAnnounceValidator`
stabilizes and sync/grandpa start to fill the gap generated during that
period.

We propose to move the lock of VoterSet a bit earlier to cover a bit
wider scope. Also we made a quick demo test to show the evidence of this
behavior, but it currently modifies few functions visibility.

Also the test is not ideal, it tries to extract the most narrowed scope
for it and is running concurrently both finalization paths, but of
course it may not reproduce always. For that purpose we added additional
check if finalization was executed only once, which for NOK scenario
should either panic or return 1 != 2 mismatch.

Currently by default used among polkadot-sdk
[DefaultBlockAnnounceValidator](https://github.com/paritytech/polkadot-sdk/blob/9107f88f83300b98af2d212463c83c659596261c/substrate/primitives/consensus/common/src/block_validation.rs#L78)
does not follow the error path, but projects utilizing announce
validator more may be affected, I am not convinced it is the only path
that may hit the panic, I will appreciate if you will help me identify
additional ones.

Looks like also associated with
https://github.com/paritytech/substrate/issues/7668

---------

Signed-off-by: Tomasz Bartos <tomasz.bartos@shielded.io>

### prdoc/pr_12506.prdoc
```diff
@@ -0,0 +1,21 @@
+title: 'grandpa: fix panic when a change block is finalized concurrently during justification import'
+
+doc:
+- audience: [Node Dev, Node Operator]
+  description: |-
+    Fixes a node panic (`returns Ok when no authority set change should be enacted; qed;`)
+    that could occur while importing a justification for a block enacting an authority set
+    change.
+
+    `GrandpaBlockImport::import_justification` verified the justification against the current
+    authority set and then enacted the change via `environment::finalize_block` under two
+    separate acquisitions of the authority-set lock. If another finalizer (the voter acting on
+    a gossiped commit, or a justification imported via sync) finalized the same block in the
+    window between the verification and the enactment, `finalize_block` short-circuited on its
+    "already finalized" guard and returned `Ok(())` while the caller still expected the change
+    to be enacted, tripping the assertion. The window was widened by anything delaying block
+    import relative to finality, making it most likely at session-rotation blocks.
+
+crates:
+- name: sc-consensus-grandpa
+  bump: minor
```

### substrate/client/consensus/grandpa/src/authorities.rs
```diff
@@ -110,11 +110,7 @@ where
 
 	/// Get the current authorities and their weights (for the current set ID).
 	pub fn current_authorities(&self) -> VoterSet<AuthorityId> {
-		VoterSet::new(self.inner().current_authorities.iter().cloned()).expect(
-			"current_authorities is non-empty and weights are non-zero; \
-			 constructor and all mutating operations on `AuthoritySet` ensure this; \
-			 qed.",
-		)
+		self.inner().current_voter_set()
 	}
 
 	/// Clone the inner `AuthoritySet`.
@@ -221,6 +217,15 @@ where
 		(self.set_id, &self.current_authorities[..])
 	}
 
+	/// Get the current authorities as a [`VoterSet`].
+	pub(crate) fn current_voter_set(&self) -> VoterSet<AuthorityId> {
+		VoterSet::new(self.current_authorities.iter().cloned()).expect(
+			"current_authorities is non-empty and weights are non-zero; \
+			 constructor and all mutating operations on `AuthoritySet` ensure this; \
+			 qed.",
+		)
+	}
+
 	/// Revert to a specified block given its `hash` and `number`.
 	/// This removes all the authority set changes that were announced after
 	/// the revert point.
```

### substrate/client/consensus/grandpa/src/environment.rs
```diff
@@ -31,7 +31,7 @@ use finality_grandpa::{
 use futures::prelude::*;
 use futures_timer::Delay;
 use log::{debug, warn};
-use parking_lot::RwLock;
+use parking_lot::{MappedMutexGuard, RwLock};
 use prometheus_endpoint::{register, Counter, Gauge, PrometheusError, U64};
 
 use sc_client_api::{
@@ -1100,7 +1100,7 @@ where
 	) -> Result<(), Self::Error> {
 		let result = finalize_block(
 			self.client.clone(),
-			&self.authority_set,
+			self.authority_set.inner(),
 			Some(self.config.justification_generation_period),
 			hash,
 			number,
@@ -1365,9 +1365,19 @@ where
 /// authority set change is enacted then a justification is created (if not
 /// given) and stored with the block when finalizing it.
 /// This method assumes that the block being finalized has already been imported.
+///
+/// NOTE: the caller must pass in the *already locked* authority set. The lock
+/// must be held for the whole duration of finalization (i.e. through writing to
+/// the DB) to avoid races, and it also implicitly synchronizes the check for the
+/// last finalized number below. Crucially, callers that take a decision based on
+/// authority-set state *before* calling this function (e.g. verifying a
+/// justification against the current set id, or computing whether a block enacts
+/// a change) must either keep holding the lock or revalidate that authority-set
+/// state after re-acquiring it before calling here, so that the decision and its
+/// enactment are consistent with respect to other finalizers (e.g. the voter).
 pub(crate) fn finalize_block<BE, Block, Client>(
 	client: Arc<Client>,
-	authority_set: &SharedAuthoritySet<Block::Hash, NumberFor<Block>>,
+	mut authority_set: MappedMutexGuard<'_, AuthoritySet<Block::Hash, NumberFor<Block>>>,
 	justification_generation_period: Option<u32>,
 	hash: Block::Hash,
 	number: NumberFor<Block>,
@@ -1381,11 +1391,6 @@ where
 	BE: BackendT<Block>,
 	Client: ClientForGrandpa<Block, BE>,
 {
-	// NOTE: lock must be held through writing to DB to avoid race. this lock
-	//       also implicitly synchronizes the check for last finalized number
-	//       below.
-	let mut authority_set = authority_set.inner();
-
 	let status = client.info();
 
 	if number <= status.finalized_number && client.hash(number)? == Some(hash) {
```

### substrate/client/consensus/grandpa/src/import.rs
```diff
@@ -815,7 +815,7 @@ where
 	///
 	/// If `enacts_change` is set to true, then finalizing this block *must*
 	/// enact an authority set change, the function will panic otherwise.
-	fn import_justification(
+	pub(crate) fn import_justification(
 		&self,
 		hash: Block::Hash,
 		number: NumberFor<Block>,
@@ -832,28 +832,29 @@ where
 			return Ok(());
 		}
 
-		let justification = GrandpaJustification::decode_and_verify_finalizes(
-			&justification.1,
-			(hash, number),
-			self.authority_set.set_id(),
-			&self.authority_set.current_authorities(),
-		);
-
-		let justification = match justification {
-			Err(e) => {
-				return match e {
-					sp_blockchain::Error::OutdatedJustification => {
-						Err(ConsensusError::OutdatedJustification)
-					},
-					_ => Err(ConsensusError::ClientImport(e.to_string())),
-				};
-			},
-			Ok(justification) => justification,
-		};
+		// Decode without holding the authority-set lock; verification must happen
+		// under the lock so it is atomic with the finalization below.
+		let justification = GrandpaJustification::decode(&justification.1)
+			.map_err(|e| ConsensusError::ClientImport(e.to_string()))?;
+
+		let authority_set = self.authority_set.inner();
+
+		justification
+			.verify_finalizes(
+				(hash, number),
+				authority_set.set_id,
+				&authority_set.current_voter_set(),
+			)
+			.map_err(|e| match e {
+				sp_blockchain::Error::OutdatedJustification => {
+					ConsensusError::OutdatedJustification
+				},
+				_ => ConsensusError::ClientImport(e.to_string()),
+			})?;
 
 		let result = environment::finalize_block(
 			self.inner.clone(),
-			&self.authority_set,
+			authority_set,
 			None,
 			hash,
 			number,
@@ -889,6 +890,9 @@ where
 				})
 			},
 			Ok(_) => {
+				// Verification above and finalization below share the same authority-set
+				// lock, so a competing finalizer cannot advance the set in between.
+				// Reaching this arm with `enacts_change` set would be a genuine bug.
 				assert!(
 					!enacts_change,
 					"returns Ok when no authority set change should be enacted; qed;"
```

### substrate/client/consensus/grandpa/src/justification.rs
```diff
@@ -125,6 +125,33 @@ impl<Block: BlockT> GrandpaJustification<Block> {
 		Ok(sp_consensus_grandpa::GrandpaJustification { round, commit, votes_ancestries }.into())
 	}
 
+	/// Decode a GRANDPA justification from its SCALE encoding.
+	pub fn decode(encoded: &[u8]) -> Result<Self, ClientError> {
+		GrandpaJustification::<Block>::decode_all(&mut &*encoded)
+			.map_err(|_| ClientError::JustificationDecode)
+	}
+
+	/// Validate that this justification finalizes the given block and that its
+	/// commit and ancestry proofs are valid for the given voter set.
+	pub fn verify_finalizes(
+		&self,
+		finalized_target: (Block::Hash, NumberFor<Block>),
+		set_id: u64,
+		voters: &VoterSet<AuthorityId>,
+	) -> Result<(), ClientError>
+	where
+		NumberFor<Block>: finality_grandpa::BlockNumberOps,
+	{
+		if (self.justification.commit.target_hash, self.justification.commit.target_number) !=
+			finalized_target
+		{
+			let msg = "invalid commit target in grandpa justification".to_string();
+			return Err(ClientError::BadJustification(msg));
+		}
+
+		self.verify_with_voter_set(set_id, voters)
+	}
+
 	/// Decode a GRANDPA justification and validate the commit and the votes'
 	/// ancestry proofs finalize the given block.
 	pub fn decode_and_verify_finalizes(
@@ -136,19 +163,9 @@ impl<Block: BlockT> GrandpaJustification<Block> {
 	where
 		NumberFor<Block>: finality_grandpa::BlockNumberOps,
 	{
-		let justification = GrandpaJustification::<Block>::decode_all(&mut &*encoded)
-			.map_err(|_| ClientError::JustificationDecode)?;
-
-		if (
-			justification.justification.commit.target_hash,
-			justification.justification.commit.target_number,
-		) != finalized_target
-		{
-			let msg = "invalid commit target in grandpa justification".to_string();
-			Err(ClientError::BadJustification(msg))
-		} else {
-			justification.verify_with_voter_set(set_id, voters).map(|_| justification)
-		}
+		let justification = Self::decode(encoded)?;
+		justification.verify_finalizes(finalized_target, set_id, voters)?;
+		Ok(justification)
 	}
 
 	/// Validate the commit and the votes' ancestry proofs.
```

### substrate/client/consensus/grandpa/src/observer.rs
```diff
@@ -124,7 +124,7 @@ where
 			// commit is valid, finalize the block it targets
 			match environment::finalize_block(
 				client.clone(),
-				&authority_set,
+				authority_set.inner(),
 				None,
 				finalized_hash,
 				finalized_number,
```

### substrate/client/consensus/grandpa/src/tests.rs
```diff
@@ -2472,3 +2472,149 @@ async fn observer_finalizes_through_authority_set_change() {
 	let wait_for = futures::future::join_all(finality_notifications);
 	run_until_complete(wait_for, &net).await;
 }
+
+#[tokio::test]
+async fn concurrent_finalization_of_change_block_doesnt_panic() {
+	// Regression test for a panic in `GrandpaBlockImport::import_justification`:
+	//
+	//     'returns Ok when no authority set change should be enacted; qed;'
+	//
+	// When importing a block that enacts a standard authority set change,
+	// `import_justification` verifies the block's justification against the current
+	// set id and then calls `environment::finalize_block` to enact the change. If
+	// another finalizer (the GRANDPA voter acting on a gossiped commit, or a
+	// justification imported via sync) finalizes the *same* block in the window
+	// between the verification and `finalize_block` acquiring the authority set lock,
+	// then `finalize_block` short-circuits on its "already finalized in the canonical
+	// chain" guard and returns `Ok(())` — while `import_justification` was told the
+	// block enacts a change (`enacts_change == true`), tripping the assertion.
+	//
+	// The fix decodes the justification without holding the authority-set lock and
+	// verifies it under the lock used for finalization. This test drives two
+	// drives two justification importers at the same change block concurrently. It
+	// does not force the exact historical interleaving, but it checks the intended
+	// stable outcome: one importer enacts the change, while the importer that lost
+	// the race observes its old-set justification as stale instead of panicking or
+	// finalizing the change twice.
+	let peers = &[Ed25519Keyring::Alice];
+	let voters = make_ids(peers);
+	let api = TestApi::new(voters);
+	let mut net = GrandpaTestNet::new(api.clone(), 1, 0);
+
+	let client = net.peer(0).client().clone();
+	let full_client = client.as_client();
+	let backend = client.as_backend();
+
+	// build a raw `GrandpaBlockImport` so we can drive `import_justification`
+	// (with `enacts_change = true`) directly, mirroring the internal `import_block`
+	// path that hits the assertion.
+	let (block_import, link) = block_import(
+		full_client.clone(),
+		JUSTIFICATION_IMPORT_PERIOD,
+		&api,
+		LongestChain::new(backend.clone()),
+		None,
+	)
+	.unwrap();
+
+	// build block #1 scheduling an immediate (delay 0) authority set change.
+	let mut builder = BlockBuilderBuilder::new(&*full_client)
+		.on_parent_block(full_client.chain_info().best_hash)
+		.fetch_parent_block_number(&*full_client)
+		.unwrap()
+		.build()
+		.unwrap();
+	add_scheduled_change(
+		&mut builder,
+		ScheduledChange { next_authorities: make_ids(peers), delay: 0 },
+	);
+	let block = builder.build().unwrap().block;
+	let hash = block.hash();
+	let number = *block.header.number();
+
+	// import the change block *without* a justification: this registers the pending
+	// standard change in the shared authority set (set id stays 0). `import_block`
+	// reports `needs_justification == true` for it.
+	let mut import = BlockImportParams::new(BlockOrigin::File, block.header);
+	import.body = Some(block.extrinsics);
+	import.fork_choice = Some(ForkChoiceStrategy::LongestChain);
+	assert_matches!(
+		block_import.import_block(import).await.unwrap(),
+		ImportResult::Imported(ImportedAux { needs_justification: true, .. })
+	);
+
+	// a valid justification for the change block, signed by the current (set 0)
+	// authorities — exactly what a finalizer verifies before calling `finalize_block`.
+	let justification = {
+		let set_id = 0;
+		let round = 1;
+		let precommit = finality_grandpa::Precommit { target_hash: hash, target_number: number };
+		let msg = finality_grandpa::Message::Precommit(precommit.clone());
+		let encoded = sp_consensus_grandpa::localized_payload(round, set_id, &msg);
+		let signature = peers[0].sign(&encoded[..]).into();
+		let precommit = finality_grandpa::SignedPrecommit {
+			precommit,
+			signature,
+			id: peers[0].public().into(),
+		};
+		let commit = finality_grandpa::Commit {
+			target_hash: hash,
+			target_number: number,
+			precommits: vec![precommit],
+		};
+		GrandpaJustification::from_commit(&full_client, round, commit).unwrap()
+	};
+	let justification = justification.encode();
+
+	// Drive two justification importers at the same change block concurrently:
+	//  - one with `enacts_change = false`, standing in for a sync justification import that
+	//    finalizes the block and enacts the change;
+	//  - one with `enacts_change = true`, standing in for the block-import path that expects to
+	//    enact the change and which carries the assertion.
+	// Both go through `finalize_block` against the same shared authority set. The
+	// `enacts_change = true` path must not be able to verify against set 0, get
+	// overtaken, and then trip the assertion.
+	let barrier = std::sync::Arc::new(std::sync::Barrier::new(2));
+
+	let other_finalizer = {
+		let block_import = block_import.clone();
+		let justification = justification.clone();
+		let barrier = barrier.clone();
+		std::thread::spawn(move || {
+			barrier.wait();
+			block_import.import_justification(
+				hash,
+				number,
+				(GRANDPA_ENGINE_ID, justification),
+				false,
+				false,
+			)
+		})
+	};
+
+	barrier.wait();
+	let import_result = block_import.import_justification(
+		hash,
+		number,
+		(GRANDPA_ENGINE_ID, justification),
+		true,
+		false,
+	);
+
+	// `join().unwrap()` would surface a panic on the other thread; the assertion would
+	// surface a panic on this one. Neither must happen.
+	let other_result = other_finalizer.join().unwrap();
+
+	// exactly one finalizer enacts the change; the one that was overtaken sees the
+	// already-advanced set id and rejects its now-stale justification.
+	let outcomes = [import_result, other_result];
+	assert_eq!(outcomes.iter().filter(|r| r.is_ok()).count(), 1, "exactly one finalizer enacts");
+	assert!(
+		outcomes.iter().any(|r| matches!(r, Err(ConsensusError::OutdatedJustification))),
+		"the overtaken finalizer rejects its stale justification",
+	);
+
+	// the authority set change was enacted exactly once and the block is finalized.
+	assert_eq!(link.shared_authority_set().set_id(), 1);
+	assert_eq!(full_client.info().finalized_number, number);
+}
```
