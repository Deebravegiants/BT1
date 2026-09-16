## Analysis

The reported bug class is a *gas-limit / gas-griefing* attack: an unprivileged caller controls a gas-cost parameter for a downstream cross-domain call, and that parameter can be abused to force reverts/DoS on a shared code path that also processes other users' legitimate operations.

The closest analog in this codebase is in the **message delivery path**, not a caller-supplied gas parameter, but an *unbounded* gas forward to an attacker-controlled destination contract during batched relay of `PostRequest`s.

### Root cause

`EvmHost.dispatchIncoming(PostRequest, address relayer)` is called by `HandlerV2.handlePostRequests` for every leaf in a permissionlessly-submitted batch of proven requests: [1](#0-0) 

Inside `dispatchIncoming`, the destination module's `onAccept` is invoked via a raw low-level `.call` with **no gas cap** — Solidity forwards essentially all remaining gas (the 63/64 rule) to the callee: [2](#0-1) 

`request.to` is fully attacker-controlled: anyone can call `EvmHost.dispatch(DispatchPost)` on the source chain and set `to` to any address, including a contract the attacker deploys on the destination chain themselves: [3](#0-2) 

Because `handlePostRequests` iterates over **all** proven leaves in one transaction and dispatches each one in the same call frame, an attacker who plants a malicious `to` contract whose `onAccept` deliberately consumes a large, attacker-tunable amount of gas (a bounded loop, not necessarily reverting) can:
1. Cause the enclosing `handlePostRequests`/`batchCall` transaction to run out of gas partway through the loop, reverting the **entire batch** — including delivery of every other, legitimate co-batched request — even though the honest requests would otherwise have succeeded.
2. Force relayers to burn gas without being paid the corresponding relayer fee (the malicious request's `fee` is attacker-set, e.g. zero), since low-level `.call` failures inside `dispatchIncoming` are swallowed (`success == false` → early return) but full out-of-gas at the outer call is not.

This mirrors the reported class exactly: an unvalidated, attacker-influenced gas-consumption parameter reachable via a permissionless entry point (`dispatch`/`handlePostRequests`) that can DoS the shared batch-delivery path used by other unrelated users' messages — i.e., "a route unable to deliver messages," one of the explicitly accepted impact categories.

### Title
Unbounded gas forwarded to attacker-controlled `onAccept` in `EvmHost.dispatchIncoming` enables batch-wide gas-griefing DoS — (File: evm/src/core/EvmHost.sol, evm/src/core/HandlerV2.sol)

### Summary
`HandlerV2.handlePostRequests` processes an entire relayer-submitted batch of proven `PostRequest`s in a single transaction, calling `IHost.dispatchIncoming` for each one. `dispatchIncoming` forwards the destination module's `onAccept` call via a bare `.call(...)` with no gas limit, so nearly all remaining transaction gas is available to the callee. Because `PostRequest.to` is fully attacker-chosen and requests are dispatched permissionlessly, an attacker can plant a malicious contract as the destination and make its `onAccept` consume a large, tunable amount of gas without reverting, exhausting the gas available to the rest of the batch loop and causing the whole `handlePostRequests`/`batchCall` transaction to run out of gas.

### Finding Description
- `dispatch(DispatchPost)` on `EvmHost` lets any account create a `PostRequest` with an arbitrary `to` (any address on the destination chain) and an arbitrary/zero `fee`: [3](#0-2) 
- `HandlerV2.handlePostRequests` verifies the MMR proof once for the whole batch, then loops over every leaf, calling `host.dispatchIncoming(leaf.request, _msgSender())` sequentially inside the same transaction: [4](#0-3) 
- `dispatchIncoming` executes the callback with a plain `.call`, not `.call{gas: X}`, so the callee (an attacker-deployed contract) can consume essentially all forwarded gas: [2](#0-1) 
- The design only guards against a *reverting* `onAccept` (it deletes the receipt and continues); it has no defense against a *non-reverting* callback that simply burns gas until the outer transaction itself runs out of gas mid-loop.
- When the outer transaction runs out of gas, the EVM reverts the entire transaction atomically, undoing delivery of every other request batched alongside the malicious one — including `PostRequestHandled` events and any state changes for benign users' requests processed earlier in the same loop.

### Impact Explanation
This allows a single low-cost malicious request (fee can be set to 0) to repeatedly deny delivery of unrelated, legitimate requests batched by relayers, and to make relayers pay for failed (out-of-gas) transactions. Since relaying is otherwise permissionless and economically driven by fees, an attacker can grief relayers/route delivery cheaply and repeatedly by re-submitting the malicious request (or new ones) targeting freshly deployed griefing contracts, degrading the reliability of the messaging route — meeting the "route unable to deliver messages" impact bar. It does not directly steal funds but produces a reliable availability/DoS primitive on the shared batch-delivery path.

### Likelihood Explanation
Likelihood is medium: the attacker needs only to (1) deploy an ordinary contract on the destination EVM chain implementing a gas-burning `onAccept`, and (2) dispatch a `PostRequest` to it via the standard, permissionless `dispatch()` entrypoint with `fee = 0`. No privileged role, governance, or consensus manipulation is required — this is reachable by any unprivileged message dispatcher.

### Recommendation
Cap the gas forwarded to the destination module in `dispatchIncoming` (e.g., `.call{gas: gasLimit}(...)`) with a bounded, protocol-defined `gasLimit` (configurable via `HostParams`), and treat an out-of-gas callback the same as any other failed delivery (delete the receipt, allow retry) rather than letting it propagate to exhaust the enclosing batch transaction. This mirrors how most cross-chain messaging systems (including the original L1StandardBridge-style designs) explicitly bound the gas given to untrusted destination execution.

### Proof of Concept
1. Attacker deploys `EvilApp` on the destination chain implementing `onAccept` with a loop that consumes a large, tunable amount of gas without reverting (e.g., repeated storage writes until a gas threshold is met).
2. Attacker calls `EvmHost.dispatch(DispatchPost{ to: abi.encode(EvilApp), fee: 0, ... })` on the source chain, alongside (or ahead of) other users' honest requests being aggregated by a relayer.
3. A relayer batches the attacker's proven request together with several legitimate ones into `HandlerV2.handlePostRequests` (or `batchCall`).
4. During the loop in `handlePostRequests`, `dispatchIncoming` calls `EvilApp.onAccept` which consumes gas up to the point where the enclosing transaction cannot complete the remaining iterations, causing the entire transaction to revert with out-of-gas — no requests in that batch are delivered, and the relayer's gas is spent for nothing.

### Citations

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

**File:** evm/src/core/EvmHost.sol (L794-818)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** evm/src/core/EvmHost.sol (L921-948)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                post.fee, path, address(this), block.timestamp
            );
        } else if (post.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
        }

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

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
```
