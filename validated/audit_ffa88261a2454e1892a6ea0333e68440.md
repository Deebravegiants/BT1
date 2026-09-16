### Title
GetRequest timeout has no counterparty proof requirement, so it can be forced through while consensus-client challenge period/freeze blocks the corresponding GetResponse from ever being delivered - ([File: modules/ismp/core/src/handlers/timeout.rs])

### Summary
`ControllerPeggedAssetV2.triggerDepeg` and `triggerEndEpoch` present a race: a liveness dependency (the Arbitrum sequencer feed) can block the "correct" outcome (depeg) while an unrelated path with no such check (end-epoch) can still be executed, producing an unfair result. Hyperbridge's ISMP `Get` request/timeout pair has the same structural asymmetry: `handle_responses` (the "correct outcome" path, delivering the real query result) requires `validate_state_machine`, which enforces that the destination-chain consensus client is unfrozen and that its `challenge_period` has elapsed [1](#0-0) , while `handle_timeouts`'s `TimeoutMessage::Get` branch (the "fallback outcome" path) performs **no** consensus-client liveness or challenge-period check at all — it only compares the request's `timeout_timestamp` to the *local* `host.timestamp()` [2](#0-1) .

### Finding Description
`validate_state_machine`, used by the response handler, requires the consensus client not be frozen and the configured challenge/delay period to have elapsed before a state commitment can be used to verify a membership proof: [1](#0-0)  and the shared helper [3](#0-2) . This means a legitimate `GetResponse` — one that was in fact computed and finalized on the destination chain before the request's `timeout_timestamp` — can be temporarily undeliverable to the source chain whenever:
- the destination-chain consensus client's `challenge_period` has not yet elapsed for the relevant height, or
- the consensus client is frozen (e.g., pending a fraud-proof dispute or awaiting governance to unfreeze it, per the documented "frozen consensus clients cannot be unfrozen" model) [4](#0-3) .

Meanwhile, `TimeoutMessage::Get` has none of these guards. It only checks that (a) the request commitment still exists locally, (b) no `response_receipt` has been stored yet, and (c) `get.timed_out(host.timestamp())` is true, purely against the *source* chain's own clock: [5](#0-4) . Unlike `PostRequest` timeouts, which additionally require a **non-membership state proof** from the destination chain (also gated by `validate_state_machine`) to affirmatively prove the request was never processed [6](#0-5) , the `Get` timeout path requires no counterparty evidence whatsoever — it is documented as intentional ("There are no proofs for Get timeouts, we only need to ensure that the timeout timestamp has elapsed on the host") [7](#0-6) .

This reproduces the M-11 bug class exactly: an external liveness/consensus dependency (sequencer feed / consensus client challenge period or freeze) can block the path that would produce the "correct" cross-chain outcome (`getLatestPrice` / `handle_responses`), while a structurally weaker path with no such dependency (`triggerEndEpoch` / `Get` timeout) remains fully callable and permanently forecloses the correct outcome, because deleting the request commitment on timeout prevents any later, valid response from ever being accepted (`handle_responses` requires `host.request_commitment(commitment)` to still exist) [8](#0-7) .

### Impact Explanation
Any `IsmpModule` relying on `GetRequest`/`GetResponse` for cross-chain state reads (e.g., token bridges validating collateral/liquidity state, intent solvers verifying fills, or any app gating a state-changing action on a query result) can be forced into its timeout/fallback code path even though the query was legitimately answered on the destination chain before expiry. Because the request commitment is deleted upon timeout processing [9](#0-8) , a subsequently-available, valid `GetResponse` for the same request will be rejected as `UnknownRequest` by `handle_responses` — permanently losing the query result. Depending on the consuming application, this can lead to unauthorized fallback actions, incorrect settlement, or fund-affecting decisions being made on stale/absent data — directly analogous to collateral-vault users wrongfully claiming premium in the source bug.

### Likelihood Explanation
This requires the natural overlap of two independently plausible conditions: (1) a `GetRequest`'s `timeout_timestamp` elapsing on the source chain, and (2) the destination chain's consensus client on the source being within its `challenge_period` or frozen at that same moment (e.g., following a legitimate consensus update that hasn't cleared its delay window, or during dispute resolution). Both challenge periods and consensus client freezes are core, expected protocol states (not attacker-injected), and an adversarial or opportunistic relayer/user can simply submit the `Get` timeout the instant `host.timestamp()` crosses the deadline, without waiting to see if a response is imminent — this requires no special privilege, matching the "unprivileged message dispatcher/relayer" reachability bar.

### Recommendation
Introduce a "challenge"/grace window for `Get` timeouts analogous to the Sherlock recommendation: require that the destination state machine's consensus client (as seen from source) is not within an active challenge period or otherwise "pending" before allowing `TimeoutMessage::Get` to be processed, or require a proof (even non-membership over the response-receipt key, as already done for `Post`) that no response was ever produced/receipted by the destination as of a finalized, challenge-period-cleared height. At minimum, disallow submitting a `Get` timeout while the corresponding destination-chain consensus client is frozen or within its configured `challenge_period`, mirroring the `validate_state_machine` check already applied to `handle_responses`.

### Proof of Concept
1. App A on chain X dispatches a `GetRequest` to chain Y with `timeout_timestamp = T`.
2. Chain Y computes the answer and it becomes available/finalized at time `T-1` (before timeout), but the consensus client for chain Y on chain X has just received an update, and its `challenge_period` extends past `T` (a fully legitimate, non-adversarial protocol state), or the client is `Frozen`.
3. A relayer attempts `handle_responses` with the valid membership proof before `T + challenge_period` — this reverts via `validate_state_machine` (`Error::ChallengePeriodNotElapsed` / `Error::FrozenConsensusClient`) [10](#0-9) .
4. Once `host.timestamp() > T`, anyone calls `handle` with `TimeoutMessage::Get { requests: [get] }`. No consensus-client or proof check applies; only the local timestamp and `response_receipt` are checked [2](#0-1) , so the timeout succeeds and the request commitment is deleted [9](#0-8) .
5. When the challenge period later elapses (or the client unfreezes) and the legitimate response is finally relayable, `handle_responses` rejects it with `UnknownRequest` because the commitment no longer exists [8](#0-7) , permanently losing the correct on-chain answer and forcing App A's `on_timeout` fallback logic to run instead of `on_response`.

### Citations

**File:** modules/ismp/core/src/handlers/response.rs (L38-40)
```rust
	let proof = msg.proof();
	let state_machine = validate_state_machine(host, proof.height)?;
	let state = host.state_machine_commitment(proof.height)?;
```

**File:** modules/ismp/core/src/handlers/response.rs (L58-61)
```rust
		let commitment = hash_request::<H>(&req);
		if host.request_commitment(commitment).is_err() {
			Err(Error::UnknownRequest { meta: (&req).into() })?
		}
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L48-88)
```rust
	let results = match msg {
		TimeoutMessage::Post { requests, timeout_proof } => {
			let state_machine = validate_state_machine(host, timeout_proof.height)?;
			let state = host.state_machine_commitment(timeout_proof.height)?;

			let wrapped: Vec<Request> = requests.iter().cloned().map(Request::Post).collect();
			dedup_requests::<H>(&wrapped)?;

			for post in &requests {
				let dest_chain = post.dest;

				// in order to allow proxies, the host must configure the given state machine
				// as it's proxy and must not have a state machine client for the destination chain
				let allow_proxy = host.is_allowed_proxy(&timeout_proof.height.id.state_id) &&
					check_state_machine_client(dest_chain);

				// check if the timeout is allowed to be proxied
				if dest_chain != timeout_proof.height.id.state_id && !allow_proxy {
					Err(Error::RequestProxyProhibited { meta: post.into() })?
				}

				// Ensure a commitment exists for all requests in the batch
				let commitment = hash_request::<H>(&Request::Post(post.clone()));
				if host.request_commitment(commitment).is_err() {
					Err(Error::UnknownRequest { meta: post.into() })?
				}

				if !post.timed_out(state.timestamp()) {
					Err(Error::RequestTimeoutNotElapsed {
						meta: post.into(),
						timeout_timestamp: post.timeout(),
						state_machine_time: state.timestamp(),
					})?
				}
			}

			let commitments = requests
				.iter()
				.map(|post| hash_request::<H>(&Request::Post(post.clone())))
				.collect();
			state_machine.verify_non_membership(host, commitments, state, &timeout_proof)?;
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L139-164)
```rust
		TimeoutMessage::Get { requests } => {
			let wrapped: Vec<Request> = requests.iter().cloned().map(Request::Get).collect();
			dedup_requests::<H>(&wrapped)?;

			for get in &requests {
				let commitment = hash_request::<H>(&Request::Get(get.clone()));
				// if we have a commitment, it came from us
				if host.request_commitment(commitment).is_err() {
					Err(Error::UnknownRequest { meta: get.into() })?
				}

				// Reject the timeout if a response has already been received for this request
				let response = GetResponse { get: get.clone(), values: Default::default() };
				if host.response_receipt(&response).is_some() {
					Err(Error::GetResponseAlreadyReceived { meta: get.into() })?
				}

				// Ensure the get timeout has elapsed on the host
				if !get.timed_out(host.timestamp()) {
					Err(Error::RequestTimeoutNotElapsed {
						meta: get.into(),
						timeout_timestamp: get.timeout(),
						state_machine_time: host.timestamp(),
					})?
				}
			}
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L178-183)
```rust
					let commitment = hash_request::<H>(&request);
					if host.request_commitment(commitment).is_err() {
						Err(Error::UnknownRequest { meta: (&get).into() })?
					}
					// Delete commitment to prevent reentrancy
					let meta = host.delete_request_commitment(&request)?;
```

**File:** modules/ismp/core/src/handlers.rs (L121-147)
```rust
pub fn validate_state_machine<H>(
	host: &H,
	proof_height: StateMachineHeight,
) -> Result<Box<dyn StateMachineClient>, Error>
where
	H: IsmpHost,
{
	// Ensure consensus client is not frozen
	let consensus_client_id = host.consensus_client_id(proof_height.id.consensus_state_id).ok_or(
		Error::ConsensusStateIdNotRecognized {
			consensus_state_id: proof_height.id.consensus_state_id,
		},
	)?;
	let consensus_client = host.consensus_client(consensus_client_id)?;
	// Ensure client is not frozen
	host.is_consensus_client_frozen(proof_height.id.consensus_state_id)?;

	// Ensure delay period has elapsed
	if !verify_delay_passed(host, &proof_height)? {
		return Err(Error::ChallengePeriodNotElapsed {
			state_machine_id: proof_height.id,
			current_time: host.timestamp(),
			update_time: host.state_machine_update_time(proof_height)?,
		});
	}

	consensus_client.state_machine(proof_height.id.state_id)
```

**File:** docs/content/protocol/ismp/consensus.mdx (L200-200)
```text
The `freeze_client` method is used to prove the existence of a consensus fault to an onchain consensus client. This message will be sent by offchain parties, colloquially known as _fishermen_ when they detect the existence of two conflicting views of the network backed by consensus proofs. This may arise from double signing or eclipse attacks. The consensus client after successfully verifying the validity of the conflicting views of the network will go into a frozen state. In this state it can no longer process new consensus messages as well as new requests & responses. Frozen consensus clients cannot be unfrozen and a new consensus client must be initialized through the `create_client` method instead.
```

**File:** docs/content/protocol/ismp/timeouts.mdx (L30-35)
```text
    /// There are no proofs for Get timeouts, we only need to
    /// ensure that the timeout timestamp has elapsed on the host
    Get {
        /// Requests that have timed out
        requests: Vec<GetRequest>,
    },
```
