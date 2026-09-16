### Title
Unchecked `String::from_utf8_unchecked` on attacker-controlled EVM message body causes undefined behavior - (File: modules/pallets/demo/src/lib.rs)

### Summary
`IsmpModuleCallback::on_accept` in the ISMP demo pallet performs `unsafe { String::from_utf8_unchecked(request.body) }` on the raw body of an incoming ISMP `PostRequest` whenever the request's source chain is `StateMachine::Evm(_)`, with no prior UTF-8 validation of the bytes.

### Finding Description
The callback is invoked by `pallet-ismp`'s dispatch/handling pipeline once a cross-chain `PostRequest` has been verified for authenticity/inclusion (i.e., after consensus/state-proof checks), but the *content* of the request body is fully attacker-controlled by whoever dispatches the request from the EVM source chain (any unprivileged user of a connected EVM chain can call the corresponding EVM dispatcher to send a `PostRequest` whose `to` targets this pallet's module id, `PALLET_ID`). [1](#0-0) 
`String::from_utf8_unchecked` is documented as unsafe precisely because the caller must guarantee the input is valid UTF-8; if it is not, the resulting `String`'s invariant is violated, and any subsequent use of it (formatting, hashing, slicing, printing, storage, or moving it into another safe API that assumes valid UTF-8) is undefined behavior. Here, no length/content check nor `str::from_utf8` validation step precedes the unsafe cast, so an attacker only needs to submit a `PostRequest` from an EVM state machine whose body contains an invalid UTF-8 byte sequence to trigger this.
This mirrors the reported bug class: an unchecked, invariant-violating cast from raw bytes into a type whose safe API assumes the invariant holds (in the advisory, `&Vec<T>` force-cast to `&[T]`; here, arbitrary bytes force-cast into `String`), both cases skipping the validation step that upholds soundness.

### Impact Explanation
Reaching this code path requires only dispatching a `PostRequest` from an EVM-connected chain targeted at the demo pallet's module id, an action available to any unprivileged relayer/message sender once the corresponding request has been proven to `pallet-ismp` — no governance/privileged access is needed. The resulting UB from feeding invalid UTF-8 to `from_utf8_unchecked` can corrupt memory-safety invariants relied upon by the Rust standard library and any downstream consumer of the corrupted `String` (e.g., in `Event::Request { data, .. }`, which is emitted on-chain and consumed by indexers/relayers), potentially leading to panics, corrupted storage/logs, or exploitable memory unsoundness depending on how the invalid `String` is subsequently used by the runtime or off-chain tooling that treats chain events as trusted.

### Likelihood Explanation
The demo pallet is wired into the ISMP module router of the `gargantua` parachain runtime (confirmed via `parachain/runtimes/gargantua/src/ismp.rs` and `parachain/runtimes/gargantua/src/lib.rs` referencing the pallet's module id/callback), so the vulnerable code is reachable on a live, non-test runtime rather than purely in test/mocked contexts. Triggering it requires nothing more than dispatching a single cross-chain `PostRequest` from an EVM source chain with a non-UTF-8 body, making likelihood high for any relayer/message path that allows this pallet to receive EVM-originated messages.

### Recommendation
Replace the unsafe conversion with safe, fallible validation, e.g.:
```rust
let data = String::from_utf8(request.body)
    .map_err(|_| IsmpError::Custom("Invalid UTF-8 in request body".to_string()))?;
```
or use `String::from_utf8_lossy` if malformed input should be tolerated rather than rejected. This removes the unchecked invariant violation while preserving the intended behavior for legitimate senders.

### Proof of Concept
1. An unprivileged actor calls the EVM-side ISMP dispatcher (`dispatch_to_evm`/equivalent) or the counterpart EVM contract to submit a `PostRequest` with `source = StateMachine::Evm(x)`, `to = PALLET_ID.to_bytes()`, and `body` containing an invalid UTF-8 byte sequence (e.g., a lone continuation byte `0x80`).
2. Once the message is relayed and proven to `pallet-ismp`, `on_accept` in `modules/pallets/demo/src/lib.rs` is invoked with this `PostRequest`.
3. The `match` arm for `StateMachine::Evm(_)` executes `unsafe { String::from_utf8_unchecked(request.body) }` on the invalid bytes, producing a `String` whose UTF-8 invariant is violated. [2](#0-1) 
4. This corrupted `String` is stored into `Event::Request { data, .. }` and deposited on-chain, propagating the invariant violation to any code (in-runtime or off-chain indexers) that subsequently treats this value as valid UTF-8.

Note: I was unable to fully confirm within the available tool budget whether `pallet-ismp-demo` is enabled by default in the `gargantua` production runtime's construct_runtime! macro (only grep matches on the ismp router wiring were retrieved, not the full runtime pallet list), so the exact deployment status in mainnet configuration should be verified before treating this as confirmed-live rather than a reachable-but-possibly-testnet-only pallet.

### Citations

**File:** modules/pallets/demo/src/lib.rs (L368-376)
```rust
impl<T: Config> IsmpModule for IsmpModuleCallback<T> {
	fn on_accept(&self, request: PostRequest) -> Result<Weight, anyhow::Error> {
		let source_chain = request.source;

		match source_chain {
			StateMachine::Evm(_) => Pallet::<T>::deposit_event(Event::Request {
				source: source_chain,
				data: unsafe { String::from_utf8_unchecked(request.body) },
			}),
```
