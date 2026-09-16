## Title
Double payout of GET-request query fee via stale non-membership proof — response delivery does not clear `_requestCommitments`, so a stale historical proof lets a relayer claim the timeout refund after the fee was already paid (`evm/src/core/EvmHost.sol`, `evm/src/core/HandlerV2.sol`)

## Summary
`EvmHost.dispatchIncoming(GetResponse, relayer)` pays the escrowed query fee to the relayer on successful delivery but never clears the corresponding entry in `_requestCommitments`. `HandlerV2.handleGetRequestTimeouts` authorizes a timeout purely via a Merkle **non‑membership** proof of a response receipt anchored at an arbitrary, possibly stale, historical state height, and `EvmHost.dispatchTimeOut` (GET variant) refunds the same fee to the original payer without checking whether a response was in fact later delivered. The result is that the same escrowed fee can be paid out twice for a single GET request: once to the relayer that delivered the response, and again as a "timeout refund" to the payer, using a non-membership proof that was true only in the past.

## Finding Description
On the source-chain host, a GET request's fee metadata lives in `_requestCommitments[commitment]` from the moment it is dispatched: [1](#0-0) 

When a `GetResponse` is delivered, `dispatchIncoming` writes a response receipt (replay protection for *responses*) and, on success, pays the relayer `_requestCommitments[commitment].fee` — but it does **not** delete or zero `_requestCommitments[commitment]`: [2](#0-1) 

Separately, `handleGetRequestTimeouts` authorizes a GET timeout by verifying a non-membership proof that no response receipt exists **at a chosen historical `message.height`**, then calls `dispatchTimeOut`: [3](#0-2) 

`dispatchTimeOut` for GET requests deletes `_requestCommitments[commitment]` (replay protection for the *request*, not the response) and unconditionally refunds `meta.fee` to `meta.sender` if the module callback succeeds — with no check of `_responseReceipts[commitment]`: [4](#0-3) 

Because the non-membership proof only proves the absence of a response receipt **as of a past finalized height** (any height still retained in `_stateCommitments`, see storage at `evm/src/core/EvmHost.sol:691-699`), and old heights are retained indefinitely unless explicitly vetoed by a fisherman, a proof generated shortly after the request's timeout (before any response existed) remains permanently valid for submission — even after a legitimate relayer later delivers the actual `GetResponse` and is paid.

By contrast, the Substrate/pallet-ismp implementation performs a **live** check instead of a stale proof: it rejects a GET timeout outright if a response receipt already exists in current storage. [5](#0-4) 

The EVM path has no equivalent live guard, so it is structurally exposed to this double-payout race that the Substrate host is not.

## Impact Explanation
This directly causes theft/loss of protocol funds: the same escrowed relayer fee is paid out twice for one GET request — once to whichever relayer delivers the `GetResponse`, and again to the original fee payer via a stale timeout proof. Any unprivileged relayer can trigger this by (a) obtaining/retaining an early non-membership proof right after a request's timeout window opens, (b) letting (or forcing, since delivery is permissionless) a legitimate response be delivered later, and (c) submitting the stale timeout proof afterward. It also delivers a spurious `onGetTimeout` callback to a module for a request that was already answered, an unsound protocol invariant violation that downstream `IApp` modules may not defend against. This satisfies the "concrete theft ... of funds" and "unsound state commitment" impact bar, reachable via a single relayed proof from an unprivileged actor, so it meets High severity.

## Likelihood Explanation
Reachable by any relayer with no special privileges — `handleGetResponses` and `handleGetRequestTimeouts` are both explicitly permissionless entry points, and old state commitments are retained by default (fishermen veto is the only eviction path, and is not routinely exercised for ordinary heights). The attacker only needs to capture a non-membership proof at any height between the request's timeout and the eventual response delivery, which is a normal, low-effort action for a relayer racing to relay both legs of a GET request.

## Recommendation
In `EvmHost.dispatchIncoming(GetResponse, address)`, delete `_requestCommitments[commitment]` once the fee has been paid out (mirroring the replay-protection pattern already used for POST/GET request timeouts), and/or in `EvmHost.dispatchTimeOut` (GET variant) check `_responseReceipts[commitment]` is unset before refunding, reverting (or skipping the refund) if a response was already delivered. Additionally, consider requiring `handleGetRequestTimeouts` to use a proof anchored no older than the height at which the request timeout elapsed, or bind timeout proofs to the *current* / latest verified state rather than an arbitrary historical height, to remove the staleness window entirely.

## Proof of Concept
1. User dispatches a `DispatchGet` on the source `EvmHost`; `_requestCommitments[commitment] = FeeMetadata{sender, fee}` is stored.
2. Once `request.timeout()` has elapsed, a relayer (attacker) captures a Merkle non-membership proof for `ResponseReceipts[commitment]` at some finalized height `H1` (no response has been recorded yet).
3. Later, a different (honest) relayer submits `handleGetResponses`, which calls `EvmHost.dispatchIncoming(response, honestRelayer)`; on success the fee is paid to `honestRelayer`, but `_requestCommitments[commitment]` is left intact (`evm/src/core/EvmHost.sol:824-847`).
4. The attacker now submits `handleGetRequestTimeouts` with the stale proof from `H1` (still verifiable against `_stateCommitments`, since no veto occurred). The check `entry.value.length != 0` passes because at height `H1` no receipt existed.
5. `EvmHost.dispatchTimeOut` deletes `_requestCommitments[commitment]` and refunds `meta.fee` to `meta.sender` — the same fee already paid out in step 3 is paid a second time, and the module also receives a spurious `onGetTimeout` for an already-answered request.

### Citations

**File:** evm/src/core/EvmHost.sol (L117-118)
```text
    // commitment of all outgoing requests and amount put up for relayers.
    mapping(bytes32 => FeeMetadata) private _requestCommitments;
```

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

**File:** modules/ismp/core/src/handlers/timeout.rs (L150-154)
```rust
				// Reject the timeout if a response has already been received for this request
				let response = GetResponse { get: get.clone(), values: Default::default() };
				if host.response_receipt(&response).is_some() {
					Err(Error::GetResponseAlreadyReceived { meta: get.into() })?
				}
```
