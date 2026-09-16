### Title
Missing response-already-received check lets a stale `_requestCommitments` reference be reused to double-pay the GET request fee - ([File: evm/src/core/HandlerV2.sol])

### Summary
`EvmHost.dispatchIncoming(GetResponse)` pays the relayer fee out of `_requestCommitments[commitment]` on successful response delivery but never deletes that record. `HandlerV2.handleGetRequestTimeouts` / `EvmHost.dispatchTimeOut(GetRequestTimeout)` later consume the same still-present `_requestCommitments[commitment]` entry to refund the fee again, without ever checking whether a `GetResponse` was already delivered for that commitment. This is the same bug class as CVE-2016-7978 (a reference that should have been invalidated after being consumed is instead retained and reused), except here the "use-after-free" is of accounting state rather than memory, and its impact is a double payout that drains the host's feeToken reserve.

### Finding Description
On the EVM `IsmpDispatcher` side, dispatching a GET request stores fee metadata keyed by commitment: [1](#0-0) 

When a `GetResponse` is delivered, `dispatchIncoming` sets a response receipt (replay guard for redelivery of the *response*) and, on success, pays the relayer fee straight out of `_requestCommitments[commitment].fee` — but never deletes `_requestCommitments[commitment]`: [2](#0-1) 

Compare this to `dispatchTimeOut` for both POST and GET timeouts, which correctly treats `_requestCommitments` as a single-use resource, deleting it up front for replay protection: [3](#0-2) 

`HandlerV2.handleGetRequestTimeouts` gates the timeout only on: (1) the request being past its timeout height, (2) `_requestCommitments[commitment].sender != 0` ("known request"), and (3) a non-membership proof of the *destination-chain* response-receipt key at the supplied (relayer-chosen, potentially old) proof height. It never queries `host.responseReceipts(commitment)` — the EVM host's own record of whether the GET request has already been answered: [4](#0-3) 

This is exactly the check that the Rust pallet-ismp equivalent performs and that Hyperbridge's own docs call out as required: reject a timeout if a response has already been received for the request, checked immediately before consuming/deleting the request's stored metadata: [5](#0-4) [6](#0-5) 

Because `_requestCommitments[commitment]` is a stale reference that is never invalidated after being "consumed" by a successful `dispatchIncoming(GetResponse)`, and because `handleGetRequestTimeouts`'s non-membership proof is checked against an arbitrary state height chosen by the caller (which can predate the point at which Hyperbridge recorded the response), an attacker can present a valid non-membership proof for a height before the response was recorded, pass the `meta.sender != 0` check using the still-present record, and cause `dispatchTimeOut` to refund the fee a second time to `meta.sender`.

### Impact Explanation
This produces a real double payout of the relayer/user fee for the same GET request commitment: once via `dispatchIncoming(GetResponse)`'s relayer reward, once via `dispatchTimeOut(GetRequestTimeout)`'s sender refund. The funds paid out come from the shared feeToken balance held by `EvmHost` for all outstanding requests, so this is a drain of protocol/user funds backing unrelated pending requests — a concrete theft/permanent loss of funds scenario, reachable by any unprivileged relayer submitting an ordinary `GetTimeoutMessage` through the permissionless `HandlerV2`.

### Likelihood Explanation
`handlePostRequests`/`handleGetResponses`/`handleGetRequestTimeouts` are all explicitly permissionless entry points intended to be called by any relayer. The attacker only needs: (a) a legitimately delivered `GetResponse` for a commitment (which they can even deliver themselves as the relayer to also collect the first payout), and (b) a valid state (non-membership) proof at a height on the destination chain that predates when the response was recorded there — something a relayer naturally possesses/can select since they choose `message.height` and `message.proof`. No admin, governance, or privileged role is required.

### Recommendation
Before deleting `_requestCommitments[commitment]`/refunding in `dispatchTimeOut(GetRequestTimeout,...)`, add a check equivalent to pallet-ismp's `GetResponseAlreadyReceived` guard — i.e. revert if `_responseReceipts[commitment].relayer != address(0)` (a response was already delivered on this host). Additionally, delete `_requestCommitments[commitment]` as part of a successful `dispatchIncoming(GetResponse)` (mirroring how `dispatchTimeOut` treats the same map as single-use) so the fee-metadata reference cannot be reused by any later flow.

### Proof of Concept
1. User calls `EvmHost.dispatch(DispatchGet)`; `_requestCommitments[commitment] = {sender, fee}` is stored (`evm/src/core/EvmHost.sol:1001`).
2. A relayer submits `HandlerV2.handleGetResponses` with a valid `GetResponseMessage`; `dispatchIncoming(GetResponse)` succeeds, `_responseReceipts[commitment]` is set, and the relayer is paid `fee` from `_requestCommitments[commitment].fee` — but this map entry is left intact (`evm/src/core/EvmHost.sol:824-847`).
3. The same (or a colluding) relayer later submits `HandlerV2.handleGetRequestTimeouts` with the original `GetRequest` and a non-membership proof of the response-receipt key at a Hyperbridge state height that predates step 2's response being recorded there.
4. `meta.sender != address(0)` still holds (never cleared in step 2), the non-membership proof verifies against the chosen earlier height, so `dispatchTimeOut(GetRequestTimeout, meta, commitment)` runs, deletes `_requestCommitments[commitment]`, and — assuming `onGetTimeout` on the module succeeds — refunds `meta.fee` to `meta.sender` a second time (`evm/src/core/EvmHost.sol:856-877`).
5. Net effect: the same fee amount is paid out twice from the host's shared feeToken balance for a single GET request.

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

**File:** evm/src/core/EvmHost.sol (L1000-1001)
```text
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: _msgSender(), fee: get.fee});
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

**File:** modules/ismp/testsuite/src/lib.rs (L354-375)
```rust
/// Reject a GET timeout when the request has already received a response. The request's timeout
/// hasn't elapsed either, so without the response-receipt guard the handler would have failed
/// with `RequestTimeoutNotElapsed` — proving the response check runs first.
pub fn get_response_already_received_check<H>(host: &H) -> Result<(), &'static str>
where
	H: IsmpHost + IsmpDispatcher,
	H::Account: From<[u8; 32]>,
	H::Balance: From<u32> + Default,
{
	let intermediate_state = setup_mock_client(host);
	let get =
		dispatch_get_request(host, &intermediate_state, host.timestamp().as_secs() + 1_000_000);

	let response = GetResponse { get: get.clone(), values: Default::default() };
	host.store_response_receipt(&response, &vec![0u8; 32]).unwrap();

	let timeout_message = Message::Timeout(TimeoutMessage::Get { requests: vec![get] });

	let res = handle_incoming_message(host, timeout_message).map_err(|e| e.downcast().unwrap());
	assert!(matches!(res, Err(Error::GetResponseAlreadyReceived { .. })));
	Ok(())
}
```
