Confirmed: this is a solid, reachable analog to the "gas siphoning" bug class in the report.

### Title
Unbounded gas forwarding to attacker-controlled `IApp` destinations in `EvmHost.dispatchIncoming` enables relayer gas-griefing / batch-DoS - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming(PostRequest, address)` forwards a relayer-submitted, permissionless `handlePostRequests` message to an arbitrary destination module chosen entirely by the *source-chain sender* (`request.to`), using a raw, gas-unbounded `.call(...)`. This is structurally identical to the UNCX "gas siphoning" pattern: a role that pays gas on behalf of others (`AUTO_COLLECT_ACCOUNT` in the report, the permissionless relayer in Hyperbridge) is forced to invoke a contract address and calldata combination fully controlled by an untrusted party, with no cap on the gas the callee may consume. [1](#0-0) 

### Finding Description
`dispatchIncoming` extracts `destination` from `request.to` (attacker-controlled bytes chosen by whoever dispatched the request on the source chain) and forwards the call with `.call(...)` — no gas stipend is specified, so effectively all remaining gas in the transaction is available to the callee: [2](#0-1) 

`HandlerV2.handlePostRequests` loops over a *batch* of independently-sourced requests and calls `host.dispatchIncoming` for each one in the same relayer transaction: [3](#0-2) 

The relayer's transaction gas limit is fixed *before* submission, based on a `debug_traceCall`/`eth_estimateGas` simulation with a small buffer: [4](#0-3) 

Because the actual on-chain call to `destination` is unmetered relative to that fixed outer gas limit, a malicious contract deployed as the destination `IApp` can:
1. Behave cheaply during the relayer's `debug_traceCall` simulation (so it passes profitability checks and gets a modest gas limit), then consume far more gas at actual inclusion time (e.g. by keying behavior off `block.number`/`block.timestamp`/state that differs between simulation and inclusion), forcing the callee to burn most/all of the forwarded gas.
2. Because no gas stipend is capped on the `.call`, this can leave too little gas left in `EvmHost`/`HandlerV2` to safely complete bookkeeping for the rest of the batch, causing the whole `handlePostRequests` transaction (containing other, unrelated legitimate requests) to run out of gas and revert — a classic 63/64-rule gas-griefing DoS.
3. Even short of an outright revert, the attacker forces the relayer to pay for gas usage that is unbounded and outside the relayer's control, while the relayer is only compensated via the fixed `fee` attached on the source chain — an exact analog of the "free gas" theft described in the report, since `request.to`/the destination module (analogous to UNCX's arbitrary token/position-manager) is chosen by an untrusted party and the relayer (analogous to `AUTO_COLLECT_ACCOUNT`) has no way to bound or vet it ahead of time.

The same unbounded-`.call` pattern exists for `GetResponse` delivery: [5](#0-4) 

### Impact Explanation
This allows an attacker to:
- Grief permissionless relayers by making delivery of a malicious request unprofitable or outright reverting (wasting real ETH gas costs with no compensation), discouraging relayer participation and degrading Hyperbridge's liveness/message-delivery guarantees for that route.
- In the batched-call path (`batchCall`/`handlePostRequests` covering multiple requests), a single malicious request can cause the entire batch — including other users' legitimate, fee-paying messages — to fail via out-of-gas, delaying or effectively censoring delivery for unrelated senders sharing the batch.
This qualifies as "a route unable to deliver messages" and imposes uncompensated financial loss (gas theft) on the permissionless relayer role, matching the accepted impact categories.

### Likelihood Explanation
Any account can deploy a malicious `IApp` contract and dispatch a `PostRequest` targeting it as `to` from any source chain the attacker controls (no privilege required — this is the "unprivileged message dispatcher" path). Relayers process requests permissionlessly and race to deliver for the fee, so a relayer will pick this request up during normal operation as long as it appears profitable at estimation time. The differential-gas trick (cheap during trace, expensive at inclusion) is a well-known technique and requires no special access.

### Recommendation
Cap the gas forwarded to the destination `IApp` in `EvmHost.dispatchIncoming`/`dispatchIncoming(GetResponse,...)` (e.g. `.call{gas: fixedCap}(...)`) so a malicious destination can never consume more than a bounded, predictable amount of gas, regardless of what the relayer simulated. Ensure the configured cap leaves enough gas in the caller's context after the call returns to always safely complete bookkeeping (receipt deletion/event emission) even if the callee fully exhausts its stipend, preventing the whole-batch DoS.

### Proof of Concept
1. Attacker deploys `EvilApp` implementing `IApp.onAccept` that reads `block.number` (or any oracle unavailable at simulation time) — during `debug_traceCall`/`eth_estimateGas` it takes a cheap branch (e.g. does nothing, ~5k gas), but at actual on-chain inclusion (a later block) it takes a gas-burning branch (e.g. large loop, ~30M gas).
2. Attacker dispatches a `PostRequest` on a source chain with `to = EvilApp`, attaching a small relayer fee (just enough to look profitable under the cheap simulated cost).
3. A relayer's tesseract node estimates gas via `debug_traceCall` (cheap path), sets a tight gas limit on `handlePostRequests`/`batchCall`, and submits, potentially batching several other legitimate requests together (`tesseract/messaging/evm/src/tx.rs` `generate_batched_contract_calls`).
4. On inclusion, `EvmHost.dispatchIncoming` forwards essentially all remaining gas to `EvilApp.onAccept` via the un-stipended `.call` (`evm/src/core/EvmHost.sol:809-810`), which now burns the expensive branch, exhausting the transaction's gas limit.
5. Depending on how much margin is left, either (a) the relayer's whole transaction (and any other batched, unrelated requests) reverts out-of-gas with the relayer paying full gas costs for nothing, or (b) the relayer's actual gas expenditure for this single message vastly exceeds the fee it was paid, realizing a direct, uncompensated loss to the relayer analogous to the reported gas-siphoning vector.

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

**File:** evm/src/core/HandlerV2.sol (L204-209)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
```

**File:** tesseract/messaging/evm/src/tx.rs (L427-435)
```rust
		let call = contract.batchCall(vec![prelude_calldata.clone(), msg_calldata]);
		let gas = call.estimate_gas().await.unwrap_or_else(|_| (chain_gas_limit * 8) / 10);
		txs.push(build_tx_request(
			from,
			handler_addr,
			call.calldata().clone(),
			gas_price,
			gas_with_buffer(gas),
		));
```
