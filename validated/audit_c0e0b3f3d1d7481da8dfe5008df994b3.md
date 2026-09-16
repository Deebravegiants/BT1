### Title
Lack of enforced message ordering in `HandlerV2`/`EvmHost` lets a permissionless relayer deliver ISMP requests out of order, breaking order-dependent app flows and stalling delivery - (File: evm/src/core/HandlerV2.sol)

### Summary
`HandlerV2.handlePostRequests` and pallet-ismp's `handlers::request::handle` verify a batch of ISMP requests against a membership proof and then dispatch them to destination modules **in whatever order the relayer places them in the batch/proof**, with no protocol-level enforcement that requests from the same `(source, from)` pair to the same `(dest, to)` module are delivered in `nonce` order. Any dApp built on ISMP whose destination logic assumes causal/sequential ordering between two separately-dispatched messages (e.g., "register peer" before "use peer", or two dependent state transitions) can have its second message delivered and reverted before the first is delivered, exactly mirroring the ZetaChain finding.

### Finding Description
`EvmHost.dispatch(DispatchPost)` assigns each outgoing request a strictly increasing `nonce` via `_nextNonce()` [1](#0-0) , but this nonce is purely for commitment uniqueness — it is never checked at the destination.

On the delivery side, `HandlerV2.handlePostRequests` iterates over `request.requests[]` (a relayer-supplied array), checks destination/timeout/duplicate-receipt per leaf, verifies the MMR multiproof for the whole batch, and then dispatches each leaf to `host.dispatchIncoming` strictly in array order — an order chosen entirely by the calling relayer: [2](#0-1) 

Because requests are finalized on Hyperbridge/consensus independently and relayers submit them via separate, permissionless transactions (or self-relay via `handlePostRequests`/`batchCall`), two logically sequential messages dispatched from the same source contract are not guaranteed to be verified, finalized, or delivered in the order they were sent — the same root cause described in the ZetaChain report ("cross-chain messages are not guaranteed to be finalized in the order they were sent from the external chain"). This is confirmed by the pallet-ismp side, which processes `msg.requests` in the order supplied in the `RequestMessage`, with no cross-batch/cross-message ordering constraint either [3](#0-2) .

Notably, the protocol authors are aware that ordering matters for some applications: `HyperbridgeLzEndpoint.sol` — built specifically to bridge LayerZero's ordered-messaging semantics over ISMP — implements an explicit per-`(receiver, srcEid, sender)` nonce check (`_inboundNonce`) precisely to compensate for ISMP's lack of built-in ordering: [4](#0-3) 

This demonstrates that ISMP core (dispatch/`HandlerV2`) provides **no ordering guarantee by default**, and every app that needs it must implement its own per-channel nonce gate. Apps that do not implement such a gate — e.g. `HyperFungibleToken`/`BridgeToken`'s `onAccept` (mint) and calldata-execution path [5](#0-4) , and `IntentGatewayV2`/`IntentsBase`'s cross-chain governance/registration flow (`Execute`, `NewDeployment`, `UpdateParams`) that gate later user-triggered dispatches on an earlier registration message — are exposed to the same failure mode as ZetaChain's stake/unstake example: a later, dependent message can be verified and delivered before the earlier message it depends on, causing a permanent revert of that delivery attempt (until manually retried) or, worse, silent divergence of application state if the app does not use idempotent/commutative semantics.

### Impact Explanation
For state machines/relayers, the practical effect is a **route unable to reliably deliver messages** for any ISMP application whose logic implicitly assumes ordered delivery between two dispatches from the same sender. Because `HandlerV2.dispatchIncoming` on host-level failure only reverts the delivery of that single request without reverting the receipt/permanently discarding it (retryable), the primary risk is DoS/stuck funds until manual reordering/retry rather than an instant fund loss — but for applications lacking `HyperbridgeLzEndpoint`'s idempotent retry/nilify machinery, an out-of-order delivery that reverts inside `onAccept` (e.g., a calldata-execution branch in `HyperFungibleToken.onAccept` that depends on prior state, or a governance/registration action expected to precede subsequent app messages) can strand escrowed/locked funds on the source chain until the dependent message is redelivered in the correct order, and in adversarial-relayer scenarios a malicious/careless relayer can deliberately reorder deliveries to force such reverts or to grief specific users/dApps. This satisfies the "route unable to deliver messages" / "permanent freezing (until manual recovery)" impact bar.

### Likelihood Explanation
Likelihood is Medium: any relayer (fully permissionless, per `handlePostRequests`'s `notFrozen` modifier only [6](#0-5) ) can choose which finalized requests to include and in what order across separate transactions/batches, and Hyperbridge's own finalization pipeline (consensus proofs verified independently per height/epoch) does not guarantee FIFO delivery even for honest relayers under normal network conditions, exactly as described in the referenced report. The condition is naturally triggered whenever a dApp emits two or more causally dependent `PostRequest`s to the same destination module without embedding its own sequencing/nonce check, as demonstrated by the fact that `HyperbridgeLzEndpoint` had to add this exact mitigation itself.

### Recommendation
- Add an optional/first-class ordering primitive at the `IHost`/`HandlerV2` level (per `(source, from, dest, to)` channel), analogous to what `HyperbridgeLzEndpoint._inboundNonce` already does, so applications can opt into "ordered delivery" without re-implementing nonce bookkeeping themselves.
- Document explicitly (as ISMP already partially does via the "Danger" callout in `docs/content/protocol/ismp/requests.mdx`) that `PostRequest.nonce` is *not* an ordering guarantee and that dependent cross-chain flows (registration-before-use patterns in `IntentGatewayV2`, `HyperFungibleToken` calldata execution, etc.) must implement their own sequencing checks, following the pattern already proven safe in `HyperbridgeLzEndpoint.onAccept`/`retryPayload`.
- Audit in-repo apps (`IntentGatewayV2`, `HyperFungibleToken`/`BridgeToken`, `ExtrinsicIntents`) for any two-message causal dependencies dispatched to the same destination and add per-channel nonce checks or explicit idempotency where such dependencies exist.

### Proof of Concept
1. Application `A` on chain `X` dispatches `PostRequest #1` ("RegisterPeer"/"NewDeployment") to module `M` on chain `Y`, then immediately dispatches `PostRequest #2` ("UseFeature") to the same module `M`, both via `EvmHost.dispatch` in the same or a later block; each gets a strictly increasing `nonce` via `_nextNonce()` [1](#0-0) .
2. Both requests are independently included in Hyperbridge's overlay tree and finalized. Because finalization/inclusion timing can vary per request (challenge periods, differing MMR leaf positions, relayer batching choices), request #2's inclusion proof can become available and be relayed to `handlePostRequests` on chain `Y` before request #1's.
3. `HandlerV2.handlePostRequests` has no cross-message ordering check — it merely validates the multiproof for whatever leaves are supplied and dispatches them in the given array order [7](#0-6) .
4. Module `M.onAccept` receives `PostRequest #2` first; since it depends on state set up by `#1` (e.g., peer/instance registration), it reverts. `EvmHost.dispatchIncoming` swallows this per-request failure (per the documented "receipt deleted on failure, delivery remains retryable" behavior) rather than the whole batch failing, so the message becomes stuck until a relayer resubmits it after `#1` lands — mirroring the ZetaChain stake/unstake PoC's outcome of a reverted, order-dependent transaction.
5. Contrast with `HyperbridgeLzEndpoint.onAccept`, which was specifically hardened against this scenario with an explicit nonce check (`_inboundNonce[receiverAddr][srcEid][sender] + 1`) [4](#0-3)  — confirming that this ordering gap exists at the core ISMP layer and must be independently mitigated by each application, most of which (in this repo) do not do so.

### Citations

**File:** evm/src/core/EvmHost.sol (L934-944)
```text
        // adjust the timeout
        uint64 timeoutTimestamp = post.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(post.timeout);
        PostRequest memory request = PostRequest({
            source: host(),
            dest: post.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            to: post.to,
            timeoutTimestamp: timeoutTimestamp,
            body: post.body
        });
```

**File:** evm/src/core/HandlerV2.sol (L181-210)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 requestsLen = request.requests.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](requestsLen);

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // check destination
            if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
            // check time-out
            if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
        }

        bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, request.proof.multiproof, leaves, request.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
    }
```

**File:** modules/ismp/core/src/handlers/request.rs (L86-133)
```rust
	// Verify membership proof
	let state = host.state_machine_commitment(msg.proof.height)?;
	let commitments = msg
		.requests
		.iter()
		.map(|post| hash_request::<H>(&Request::Post(post.clone())))
		.collect();
	state_machine.verify_membership(host, commitments, state, &msg.proof)?;

	let mut total_weights = Weight::zero();
	let result = msg
		.requests
		.into_iter()
		.map(|request| {
			let wrapped_req = Request::Post(request.clone());
			let mut lambda = || {
				let cb = router.module_for_id(request.to.clone())?;
				// Re-check the receipt right before dispatch. The up-front pass above
				// runs before any callback executes; a prior request's on_accept in
				// this same batch could have stored a receipt for this request
				// (directly or by re-entering the handler), and we must not invoke
				// on_accept a second time.
				if host.request_receipt(&wrapped_req).is_some() {
					Err(Error::DuplicateRequest { meta: wrapped_req.clone().into() })?
				}
				// Store request receipt to prevent reentrancy attack
				let signer = host.store_request_receipt(&wrapped_req, &msg.signer)?;
				let res = cb.on_accept(request.clone()).map(|weight| {
					total_weights.saturating_accrue(weight);

					let commitment = hash_request::<H>(&wrapped_req);
					Event::PostRequestHandled(RequestResponseHandled {
						commitment,
						relayer: signer,
					})
				});
				// Delete receipt if module callback failed so it can be timed out
				if res.is_err() {
					host.delete_request_receipt(&wrapped_req)?;
				}
				Ok(res)
			};

			let res = lambda().and_then(|res| res);
			res
		})
		.collect::<Vec<_>>();

```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L375-396)
```text
        // Validate and advance the nonce. The nonce is committed BEFORE (and independently of)
        // OApp execution: a reverting `lzReceive` must not roll back this write. Otherwise the
        // message would be retried forever at the same nonce and every later nonce would be
        // permanently rejected, bricking the (receiver, srcEid, sender) channel.
        address receiverAddr = address(uint160(uint256(receiver)));
        uint64 expectedNonce = _inboundNonce[receiverAddr][srcEid][sender] + 1;
        if (nonce != expectedNonce) revert InvalidNonce(expectedNonce, nonce);
        _inboundNonce[receiverAddr][srcEid][sender] = nonce;

        // Deliver to the OApp. Isolate the external call so a deterministic revert (zero
        // recipient, over-cap mint, blocklisted recipient, malformed payload, paused OApp, etc.)
        // does not revert `onAccept`. On failure the payload is retained for later retry/recovery
        // via retryPayload/clear/skip/nilify/burn.
        Origin memory origin = Origin({srcEid: srcEid, sender: sender, nonce: nonce});
        try ILayerZeroReceiver(receiverAddr).lzReceive(origin, guid, message, address(0), "") {
            // delivered successfully
        } catch {
            bytes32 payloadHash = keccak256(abi.encode(guid, message));
            _inboundPayloadHashes[receiverAddr][srcEid][sender][nonce] = payloadHash;
            emit InboundPayloadStored(receiverAddr, srcEid, sender, nonce, payloadHash);
        }
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-313)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({
            from: message.from,
            to: beneficiary,
            source: string(request.source),
            amount: message.amount
        });
    }
```
