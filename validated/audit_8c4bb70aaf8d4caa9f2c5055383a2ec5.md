Found it. There is a real analog here: in `modules/pallets/testsuite/src/tests/pallet_ismp.rs:487-501`, the test itself documents the bug class — when a source application's `on_timeout` module callback fails, `host.on_request_timeout` is never invoked, so the relayer-fee escrow held in `RELAYER_FEE_ACCOUNT` is never released back to the payer, permanently freezing the escrowed fee. This is structurally the same root cause as CVE-2024-35829: a later step in a resource-allocation flow can fail/short-circuit, and the caller does not clean up (refund/deallocate) the resource that was reserved earlier (deposit escrowed via `T::Currency::transfer` in `dispatch_request`, `modules/pallets/ismp/src/dispatcher.rs:96-106`). [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Relayer fee escrow permanently frozen when a POST/GET request's timeout module callback fails - (File: `modules/pallets/ismp/src/host.rs`)

### Summary
`pallet-ismp`'s request-timeout pipeline refunds the relayer fee escrowed at dispatch time (`RELAYER_FEE_ACCOUNT`) only if the destination application module's `on_timeout` callback succeeds. If the callback returns an error — which any application module can do, including third-party ISMP modules integrated on the chain, or simply an application bug — the pallet's `on_request_timeout` refund logic (which releases the escrowed fee back to `payer`) is never invoked. The escrowed relayer fee then sits in `RELAYER_FEE_ACCOUNT` indefinitely with no code path left to reclaim it, permanently freezing user funds. This mirrors the `lima_heap_alloc`/`lima_vm_map_bo` bug class: a resource is reserved up front (`T::Currency::transfer` into escrow in `dispatch_request`), and a later step in the same logical flow can fail without the earlier reservation being released.

### Finding Description
When an application dispatches a cross-chain request through `pallet-ismp`'s `IsmpDispatcher::dispatch_request`, any non-zero relayer fee is immediately transferred out of the payer's account into `RELAYER_FEE_ACCOUNT` as escrow: [2](#0-1) 

The only code path that releases this escrow back to the original payer is `IsmpHost::on_request_timeout`, which reads the `FeeMetadata` and performs the refund transfer: [3](#0-2) 

The handler pipeline that drives a timeout is: delete the request commitment, invoke the destination module's `IsmpModule::on_timeout` callback, and only then call `IsmpHost::on_request_timeout` to actually refund the fee. If the module's `on_timeout` implementation returns an `Err` (a legitimate, always-possible outcome for any application module, deliberate or accidental), the handler short-circuits before `on_request_timeout` runs, and the fee refund is skipped entirely. The repository's own regression test acknowledges this exact behavior as expected/observed, not defended against: [1](#0-0) 

There is no retry, sweep, or alternative reclaim mechanism for a request whose timeout callback failed once — the request commitment has already been deleted (replay protection), so the timeout cannot be resubmitted for that request, and the fee remains stuck in `RELAYER_FEE_ACCOUNT` forever. Any user or application that dispatches a request with a non-zero relayer fee to a destination module whose `on_timeout` can revert (application-level errors, insufficient module balance to complete secondary effects in the timeout handler, deliberately reverting logic in a buggy or malicious application module) can trigger this permanent freeze on their own escrowed fee.

### Impact Explanation
This is a permanent freezing-of-funds bug reachable by any unprivileged user who dispatches a fee-bearing POST or GET request via `pallet-ismp` (directly, or through any pallet built on top of it, e.g. `pallet-hyper-fungible-token`, `pallet-intents-coprocessor`). If the request times out and the destination application module's `on_timeout` callback errors for any reason, the escrowed relayer fee is irrecoverably locked in `RELAYER_FEE_ACCOUNT` — neither the original payer nor governance has a call path to release it. Given relayer fees can be arbitrarily large (users are incentivized to pay well to guarantee delivery) and any application module bug or edge case can cause `on_timeout` to fail, this is a systemic loss-of-funds vector with medium-to-high severity, matching the CVSS 5.5 (Availability/Integrity of funds impact, no confidentiality) profile of the reference CVE.

### Likelihood Explanation
Likelihood is moderate: it requires (1) a request to actually time out, and (2) the destination module's `on_timeout` to fail. Both are realistic — timeouts are a normal, expected outcome of cross-chain messaging (delivery windows expiring, relayers not showing up), and application-level `on_timeout` handlers performing balance transfers, storage lookups, or other fallible operations can legitimately fail (e.g., insufficient escrow balance for a partial refund, a paused/frozen destination asset, or simply a bug in a newly integrated ISMP module). No malicious privileged actor is required — a normal user's own request can end up in this state due to conditions outside their control.

### Recommendation
Decouple the relayer-fee refund from the success of the application module's `on_timeout` callback. Either (a) always execute the fee refund regardless of the module callback's outcome (treat fee release and app-level timeout notification as independent steps), or (b) if the module callback fails, retain the request metadata (instead of deleting it) so the timeout can be retried by a relayer later, similar to the existing retry pattern used for failed EVM-side timeout delivery in `dispatchTimeOut` (`evm/src/core/EvmHost.sol:885-906`, which re-stores `_requestCommitments[commitment]` on failure so it can be retried). At minimum, add a governance-gated sweep/rescue call to recover fees stuck in `RELAYER_FEE_ACCOUNT` for requests whose timeout module callback has permanently failed.

### Proof of Concept
1. An application module `M` dispatches a POST request via `pallet_ismp::Pallet::<T>::dispatch_request` with a non-zero relayer fee `F`, paid from `payer`. The fee is escrowed into `RELAYER_FEE_ACCOUNT` per `modules/pallets/ismp/src/dispatcher.rs:96-106`.
2. The request never gets delivered before its `timeout_timestamp`.
3. A relayer submits the timeout proof; the handler pipeline calls `host.delete_request_commitment(&request)` (replay protection, `modules/pallets/ismp/src/host.rs:236-243`) followed by `M::on_timeout(request)`.
4. `M::on_timeout` returns `Err(..)` — this is demonstrated directly in the existing test at `modules/pallets/testsuite/src/tests/pallet_ismp.rs:493-498` using `ERROR_MODULE_ID`, whose module intentionally errors on `on_timeout`.
5. Because the callback errored, `host.on_request_timeout(&request, meta)` (the only refund path, `modules/pallets/ismp/src/host.rs:322-335`) is never called.
6. `Balances::balance(&RELAYER_FEE_ACCOUNT.into_account_truncating())` remains at the escrowed amount forever (asserted directly by the test at line 501), with the request commitment already deleted so no retry or resubmission of the timeout is possible for that request — the fee is permanently frozen.

### Citations

**File:** modules/pallets/testsuite/src/tests/pallet_ismp.rs (L486-501)
```rust

		// Second dispatch lives at the next MMR leaf. Failing inner callback
		// means `on_request_timeout` is never reached, so the escrow stays
		// in place.
		let Leaf::Request(request) = Mmr::intermediate_leaves(1).unwrap() else {
			panic!("Leaf not found!")
		};
		let _meta = host.delete_request_commitment(&request).unwrap();
		host.ismp_router()
			.module_for_id(ERROR_MODULE_ID.to_vec())
			.unwrap()
			.on_timeout(request.clone())
			.unwrap_err();

		// pallet-ismp still has it
		assert_eq!(Balances::balance(&RELAYER_FEE_ACCOUNT.into_account_truncating()), 10 * UNIT);
```

**File:** modules/pallets/ismp/src/dispatcher.rs (L92-106)
```rust
	fn dispatch_request(
		&self,
		request: DispatchRequest,
		fee: FeeMetadata<T>,
	) -> Result<H256, anyhow::Error> {
		// collect payment for the request
		if fee.fee != Zero::zero() {
			T::Currency::transfer(
				&fee.payer,
				&RELAYER_FEE_ACCOUNT.into_account_truncating(),
				fee.fee,
				Preservation::Expendable,
			)
			.map_err(|err| IsmpError::Custom(format!("Error withdrawing request fees: {err:?}")))?;
		}
```

**File:** modules/pallets/ismp/src/host.rs (L322-335)
```rust
	fn on_request_timeout(&self, _req: &Request, meta: Vec<u8>) -> Result<(), Error> {
		let leaf_meta = RequestMetadata::<T>::decode(&mut &*meta)
			.map_err(|_| Error::Custom("Failed to decode leaf metadata".to_string()))?;
		if leaf_meta.fee.fee > Zero::zero() {
			T::Currency::transfer(
				&RELAYER_FEE_ACCOUNT.into_account_truncating(),
				&leaf_meta.fee.payer,
				leaf_meta.fee.fee,
				Preservation::Expendable,
			)
			.map_err(|err| Error::Custom(format!("Failed to refund relayer fee: {err:?}")))?;
		}
		Ok(())
	}
```
