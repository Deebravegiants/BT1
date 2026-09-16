### Title
Unbounded external call in `EvmHost.dispatchIncoming` allows a griefing DoS on batched message delivery - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatchIncoming(PostRequest, address)` forwards a POST request to an attacker-controlled `to` address via a raw, gas-unbounded `.call()`. `HandlerV2.handlePostRequests` invokes this once per request inside a single loop that processes an entire relayer-submitted batch (and, via `batchCall`, can be combined with `handleConsensus` and other message types in one transaction). Because the callee receives essentially all remaining gas (EVM's 63/64 forwarding rule) and there is no per-call gas cap, an attacker can dispatch a POST request whose destination is a contract engineered to consume (or waste, e.g. via a return-data "gas bomb") all forwarded gas, causing the enclosing transaction to run out of gas and revert — denying delivery of every other, unrelated request bundled in that same relayer transaction.

### Finding Description
`dispatchIncoming` resolves the destination purely from attacker-supplied `request.to` and low-level `.call()`s it with no gas stipend: [1](#0-0) 

This is called from the request-processing loop in `HandlerV2.handlePostRequests`, which iterates over the entire batch of requests supplied by the relayer in one transaction, verifying the merkle multiproof once and then dispatching every leaf in sequence: [2](#0-1) 

`request.to` is fully attacker-controlled at dispatch time on the source chain — any unprivileged sender can dispatch a `PostRequest` addressed to a contract they deploy themselves. Because Solidity's `.call()` without an explicit `gas:` value forwards essentially all available gas to the callee, a malicious destination contract can:
- loop until it exhausts virtually all forwarded gas, or
- return an excessively large `returndata` buffer that costs a large amount of gas to copy back (a "return bomb"),

either of which will make `dispatchIncoming`'s external call consume nearly the entire gas budget available to the surrounding transaction. Since `dispatchIncoming` treats a failed callee call the same as any other failure (it just deletes the receipt and returns without reverting), the *intended* design assumes callee failures are cheap and isolated — but an out-of-gas condition induced by the callee is not cheap: it burns almost all of the caller's remaining gas by design of the EVM gas-forwarding rule, leaving insufficient gas for the rest of `handlePostRequests`'s loop (or for `batchCall`'s subsequent `handleConsensus`/other message deliveries) to complete, causing the whole enclosing transaction to revert with an out-of-gas error.

This is structurally the same bug class as the Jetty HTTP/2 report: a single invalid/malicious item, submitted by an unprivileged party, is processed synchronously inside a shared resource (Jetty's selector thread / here, the relayer's single batch transaction) in a way that can be made to consume unbounded resources and block/deny processing of everything else sharing that resource.

### Impact Explanation
Any unprivileged actor can deploy a griefing contract and dispatch a POST request to it. Once that request is included by a relayer in the same batch/transaction as legitimate, unrelated in-flight messages (which is exactly what `batchCall`/`handlePostRequests`'s batching is designed to optimize for), delivery of all of those other requests can be denied via transaction-wide gas exhaustion. This is a concrete "route unable to deliver messages" denial-of-service: relayers attempting normal batch delivery will have their transactions revert, and the presence of even one such malicious pending request can repeatedly disrupt delivery until relayers manually identify and isolate it (if they even can, since detection requires simulation).

### Likelihood Explanation
The attack requires only: (1) deploying a simple contract with a gas-burning `onAccept`/fallback, and (2) dispatching an ordinary POST request to it from any source chain — both permissionless, single-transaction actions available to any user. No governance, consensus forgery, or privileged role is needed, and relayers batching requests for gas efficiency are a normal, expected mode of operation, making the trigger conditions realistic and low-cost for an attacker.

### Recommendation
Cap the gas forwarded to application callbacks in `EvmHost.dispatchIncoming` (and the analogous `dispatchIncoming(GetResponse,...)`/`dispatchTimeOut` functions) using an explicit `call{gas: STIPEND}(...)`, and/or bound the copied return data size (e.g., only copy the first few bytes of `returndata`, or ignore it) to eliminate the return-bomb vector. Consider also isolating each dispatch's gas budget (e.g., via a fixed per-message gas allowance derived from the batch size) so that one hostile destination cannot consume gas earmarked for the rest of the batch.

### Proof of Concept
1. Deploy `EvilApp` implementing `onAccept(IncomingPostRequest)` that runs a gas-burning loop (e.g., `while(true){}` bounded only by gas, or writes many storage slots) or returns a very large `bytes` payload from a fallback used as `onAccept`.
2. From any account, dispatch a `PostRequest` on the source chain with `to = address(EvilApp)` on the destination chain, alongside/interleaved with normal application traffic that a relayer would naturally batch.
3. Relayer builds a `PostRequestMessage` (or `batchCall`) containing this request together with several legitimate, unrelated requests, and submits `HandlerV2.handlePostRequests`.
4. During the loop's call to `host.dispatchIncoming(leaf.request, _msgSender())` for the malicious leaf, the low-level `.call()` forwards ~63/64 of remaining gas into `EvilApp`, which burns nearly all of it; the transaction runs out of gas before finishing the loop, reverting delivery of all requests in the batch, including the legitimate ones.

### Citations

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

**File:** evm/src/core/HandlerV2.sol (L204-210)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
    }
```
