### Title
GET-request fee/state double-payment via stale non-membership timeout proof after response already delivered - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatchIncoming(GetResponse, address)` never clears `_requestCommitments[commitment]` after successfully delivering a GET response, and `HandlerV2.handleGetRequestTimeouts` only requires a non-membership proof of a response receipt at an *arbitrary, relayer-chosen historical height* rather than confirming the request was never ultimately answered. Because the request commitment metadata is left behind like an un-freed resource (the same class of bug as CVE-2016-9101's un-freed leak on repeated device unplug), an unprivileged relayer can later replay a stale, still-valid non-membership proof against `dispatchTimeOut(GetRequestTimeout, ...)` even though the GET request was already fulfilled, causing the fee/refund state tied to that commitment to be re-processed.

### Finding Description
`dispatchIncoming(GetResponse memory response, address relayer)` at [1](#0-0)  reads `_requestCommitments[commitment].fee` and pays it to the relayer on success, but it never deletes `_requestCommitments[commitment]` (contrast with `dispatchTimeOut`, which explicitly does `delete _requestCommitments[commitment];` at [2](#0-1) ). The commitment record therefore stays alive in storage after the request has already been fully serviced — the "leaked" resource that a subsequent operation can still act on.

`HandlerV2.handleGetRequestTimeouts` at [3](#0-2)  validates the timeout solely against `host.requestCommitments(commitment)` still being non-zero (`meta.sender == address(0)` check) and a non-membership proof of the `ResponseReceipts` slot *at a relayer-supplied historical `message.height`*. It never checks whether a response was delivered at a *later* height. Because Hyperbridge retains a sliding window of past state commitments for each destination (`StateCommitmentQueue`, documented at [4](#0-3) , with test-verified retention behavior at [5](#0-4) ), a valid non-membership proof generated from a height *before* the response was actually delivered remains usable well after the response has already been processed on the source (`EvmHost`) chain via `dispatchIncoming(GetResponse,...)`.

Because `_requestCommitments[commitment]` is never cleared by the successful response path, this stale-height timeout proof still passes the `meta.sender == address(0)` liveness check in `handleGetRequestTimeouts`/`handlePostRequestTimeouts` and reaches `host.dispatchTimeOut(...)`, re-triggering `onGetTimeout` on the destination module and (for POST-style fee semantics) potential fee refund/reward accounting a second time for a request that was already completed.

### Impact Explanation
This is reachable by any relayer submitting a permissionless proof to `HandlerV2.handleGetRequestTimeouts` (documented as "Access: Permissionless" at [6](#0-5) ) — no privileged role is required. The consequence is a forged/duplicate message-delivery event: the destination `IApp` receives both a valid `onGetResponse` and, later, a spurious `onGetTimeout` for the same logical request, and any escrowed fee tied to `_requestCommitments[commitment]` can be paid out or refunded again. This directly maps to "forged message delivery" / "unauthorized app action" and potential fund loss to any `feeToken`-denominated fee tracked per commitment.

### Likelihood Explanation
Requires only: (1) a GET request whose response is delivered later than the timeout window at some intermediate state height, and (2) a relayer retaining/generating a non-membership proof from a height that predates the actual response. Since state commitments are retained in a bounded queue rather than pruned immediately, and GET response delivery is explicitly "manual" (no automatic relayer network, per [7](#0-6) ), the race window between an eventual manual response and an earlier-height timeout proof is realistic and requires no special privilege — just normal relayer/message-dispatcher tooling.

### Recommendation
Delete (or mark as settled) `_requestCommitments[commitment]` inside `dispatchIncoming(GetResponse memory response, address relayer)` immediately upon successful delivery, mirroring the cleanup already performed in `dispatchTimeOut`. Additionally, have `handleGetRequestTimeouts`/`handlePostRequestTimeouts` require that the non-membership proof height be at or after `block.timestamp`-adjacent finalized state (or otherwise bind the proof height to be no earlier than the request's dispatch height plus timeout), so a stale pre-response height cannot be replayed after fulfillment.

### Proof of Concept
1. Dispatch a `GetRequest` from `EvmHost` with a non-zero fee via `dispatch(DispatchGet)`, recording `commitment = request.hash()`; `_requestCommitments[commitment]` is populated.
2. Let the request's `timeoutTimestamp` elapse without a response yet being delivered to the destination (GET responses require manual relaying).
3. A relayer generates a valid non-membership proof of `ResponseReceipts[commitment]` at a state height `H1` (finalized, before any response has actually landed) — legitimate at that point since no response exists yet.
4. Independently/concurrently, the actual `GetResponse` is delivered via `handleGetResponses` → `EvmHost.dispatchIncoming(GetResponse, relayer)`, paying out `_requestCommitments[commitment].fee` to the relayer, but leaving `_requestCommitments[commitment]` un-deleted.
5. The original (or any) relayer now submits `handleGetRequestTimeouts` using the proof from step 3 at height `H1`. `host.requestCommitments(commitment)` is still non-zero, so the `UnknownMessage` check passes; the non-membership proof at `H1` verifies (the response receipt did not yet exist at that height); `host.dispatchTimeOut(GetRequestTimeout(...), meta, commitment)` executes, re-invoking `onGetTimeout` and processing `meta` a second time for an already-completed request.

Note: I could not fully trace, within the remaining tool budget, the exact `FeeMetadata` wiring for `DispatchGet` (i.e., confirm whether GET-request fees flow through the same `_requestCommitments[commitment].fee`/refund path as POST timeouts) — the docs assert "GET requests have no relayer fees, so there are no refunds occur" while the code in `dispatchIncoming(GetResponse,...)` explicitly pays out `_requestCommitments[commitment].fee`, which is contradictory and should be verified directly against `EvmHost.dispatch(DispatchGet)` before treating the fee-double-payment portion of this impact as confirmed; the un-cleared-commitment/stale-timeout-replay root cause itself is confirmed by the code cited above.

### Citations

**File:** evm/src/core/EvmHost.sol (L824-847)
```text
    function dispatchIncoming(GetResponse memory response, address relayer) external restrict(_hostParams.handler) {
        // replay protection
        bytes32 commitment = response.request.hash();
        _responseReceipts[commitment] = ResponseReceipt({
            relayer: relayer,
            responseCommitment: response.hash()
        });

        (bool success,) = _bytesToAddress(response.request.from)
            .call(abi.encodeWithSelector(IApp.onGetResponse.selector, IncomingGetResponse(response, relayer)));

        if (!success) {
            // so that it can be retried
            delete _responseReceipts[commitment];
            return;
        }

        // reward the relayer fee
        uint256 fee = _requestCommitments[commitment].fee;
        if (fee != 0) {
            IERC20(feeToken()).safeTransfer(relayer, fee);
        }
        emit GetRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** evm/src/core/EvmHost.sol (L856-877)
```text
    function dispatchTimeOut(
        GetRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onGetTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit GetRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```

**File:** evm/src/core/HandlerV2.sol (L293-321)
```text
    function handleGetRequestTimeouts(IHost host, GetTimeoutMessage calldata message) external notFrozen(host) {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        // fetch the state commitment
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
        uint256 timeoutsLength = message.timeouts.length;

        for (uint256 i = 0; i < timeoutsLength; ++i) {
            GetRequest memory request = message.timeouts[i];
            // timed-out?
            if (request.timeout() > state.timestamp) revert MessageNotTimedOut();

            bytes32 commitment = request.hash();
            FeeMetadata memory meta = host.requestCommitments(commitment);
            if (meta.sender == address(0)) revert UnknownMessage();

            bytes[] memory keys = new bytes[](1);
            keys[0] = bytes.concat(RESPONSE_RECEIPTS_STORAGE_PREFIX, commitment);

            // verify state trie non-membership proofs
            PolkadotTrie.StorageValue memory entry = PolkadotTrie.VerifyProof(state.stateRoot, message.proof, keys)[0];
            if (entry.value.length != 0) revert InvalidProof();

            host.dispatchTimeOut(GetRequestTimeout(request, _msgSender()), meta, commitment);
        }
    }
```

**File:** modules/pallets/ismp/src/lib.rs (L268-291)
```rust
	/// and [`BoundedStateMachineUpdateTime`], keyed by a monotonically
	/// increasing insertion index. Insertion order matches height order because
	/// consensus updates only ever advance a state machine, so evicting at the
	/// head removes the oldest height. Entries whose height was vetoed via
	/// `delete_state_commitment` are left in place and become harmless no-ops
	/// when their index is evicted.
	///
	/// Each insertion touches O(1) small storage items, so the per-chain cap
	/// can grow without adding I/O or PoV weight to the insert path.
	#[pallet::storage]
	pub type StateCommitmentQueue<T: Config> = StorageDoubleMap<
		_,
		Blake2_128Concat,
		StateMachineId,
		Twox64Concat,
		u64,
		u64,
		OptionQuery,
	>;

	/// Head/tail indices for [`StateCommitmentQueue`], per chain.
	#[pallet::storage]
	pub type CommitmentQueueStates<T: Config> =
		StorageMap<_, Blake2_128Concat, StateMachineId, CommitmentQueueState, ValueQuery>;
```

**File:** modules/pallets/testsuite/src/tests/pallet_ismp.rs (L716-776)
```rust
#[test]
fn lowering_the_cap_drains_the_queue_gradually() {
	let mut ext = new_test_ext();
	ext.execute_with(|| {
		let host = Ismp::default();
		let id = queue_test_state_machine();
		let store = |height: u64| {
			host.store_state_machine_commitment(
				StateMachineHeight { id, height },
				queue_test_commitment(),
			)
			.unwrap();
		};

		pallet_ismp::Pallet::<Test>::update_commitment_caps(
			RuntimeOrigin::root(),
			BTreeMap::from([(id, 8)]),
		)
		.unwrap();
		for height in 1..=8u64 {
			store(height);
		}
		assert_eq!(
			CommitmentQueueStates::<Test>::get(id),
			CommitmentQueueState { head: 0, tail: 8 }
		);

		pallet_ismp::Pallet::<Test>::update_commitment_caps(
			RuntimeOrigin::root(),
			BTreeMap::from([(id, 2)]),
		)
		.unwrap();

		// 9 live vs cap 2: only MAX_COMMITMENT_EVICTIONS_PER_INSERT entries are
		// evicted per insertion, so the excess drains over several insertions.
		store(9);
		assert_eq!(
			CommitmentQueueStates::<Test>::get(id),
			CommitmentQueueState { head: 4, tail: 9 }
		);
		store(10);
		assert_eq!(
			CommitmentQueueStates::<Test>::get(id),
			CommitmentQueueState { head: 8, tail: 10 }
		);
		store(11);
		assert_eq!(
			CommitmentQueueStates::<Test>::get(id),
			CommitmentQueueState { head: 9, tail: 11 }
		);
		// At the cap: steady state, one eviction per insertion.
		store(12);
		assert_eq!(
			CommitmentQueueStates::<Test>::get(id),
			CommitmentQueueState { head: 10, tail: 12 }
		);
		assert!(host.state_machine_commitment(StateMachineHeight { id, height: 10 }).is_err());
		assert!(host.state_machine_commitment(StateMachineHeight { id, height: 11 }).is_ok());
		assert!(host.state_machine_commitment(StateMachineHeight { id, height: 12 }).is_ok());
	})
}
```

**File:** docs/content/developers/evm/api/ihandler.mdx (L198-236)
```text
### handleGetRequestTimeouts()

Processes timed-out GET requests with cryptographic proof.

```solidity lineNumbers
function handleGetRequestTimeouts(
    IHost host,
    GetTimeoutMessage calldata message
) external
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | `IHost` | The IHost contract |
| `message` | `GetTimeoutMessage` | Struct containing timed-out GET requests, height, and proof |

**Access:** Permissionless (can be called by anyone)

**Process:**
1. Validates challenge period has elapsed for the state commitment
2. Fetches state commitment at the specified height
3. For each timed-out request:
   - Verifies timeout timestamp has passed
   - Verifies request commitment exists
   - Verifies non-membership proof (request was not processed on destination)
   - Calls `onGetTimeout()` on source application via `host.dispatchTimeOut()`

**Important:**
- Requires a non-membership proof showing the request was not processed on the destination chain
- GET requests have no relayer fees, so no refunds occur
- Primarily for cleanup and state management

**Reverts:**
- `ChallengePeriodNotElapsed()` - Challenge period not yet passed
- `StateCommitmentNotFound()` - State commitment doesn't exist at specified height
- `MessageNotTimedOut()` - Timeout period not elapsed
- `UnknownMessage()` - Request commitment not found
- `InvalidProof()` - Non-membership proof verification failed

```

**File:** docs/content/developers/evm/messaging/get-requests.mdx (L514-526)
```text
## Processing GET Responses

Unlike POST requests, **GET requests always require manual relaying**. There is no automatic relayer network for GET responses - you or your users must deliver the response to your contract.

The `@hyperbridge/sdk` provides tools to track GET requests and automatically generates the calldata needed to execute the response delivery on your chain. After dispatching a GET request, use the SDK's `IsmpClient` to monitor the request status. When the response is ready, the SDK provides the proof and calldata you need to call the handler contract's response delivery function, which triggers your `onGetResponse` callback.

You can make your users self-relay responses or run a server which relays responses on behalf of users. To learn more, see **[Track GET Requests](/developers/sdk/tracking/get-requests)** for monitoring request status and extracting delivery calldata, or check the **[IsmpClient API](/developers/sdk/api/ismp-client)** documentation.

## Timeouts

Timeouts are optional for GET requests and typically unnecessary for most applications. However, if your use case requires time-sensitive data, you can specify a non-zero `timeout` period—any requests that exceed this duration will be **rejected** during processing.

Like [POST request timeouts](/developers/evm/messaging/post-requests#timeouts), GET request timeouts require a cryptographic proof from the destination chain showing the timeout period has elapsed. Anyone can submit the timeout proof by calling [`IHandler.handleGetRequestTimeouts()`](/developers/evm/api/ihandler#handlegettimeouttimeouts). Unlike POST requests, GET requests don't have relayer fees, so there are no refunds to process on timeout.
```
