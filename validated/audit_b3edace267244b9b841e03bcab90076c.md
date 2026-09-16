## Finding

Based on my research, I found a structural analog to the reported reentrancy pattern in `EvmHost.dispatchIncoming(GetResponse)`.

### Title
Relayer fee is paid out to an untrusted address *after* an unguarded external call, allowing fee re-extraction on reentry - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatchIncoming(GetResponse memory response, address relayer)` follows the exact anti-pattern flagged in the source report: state relevant to reward accounting (`_requestCommitments[commitment].fee`) is read and paid out to the relayer only *after* an untrusted external `.call()` into the requesting module's `onGetResponse` handler, rather than before it.

### Finding Description [1](#0-0) 

The function:
1. Sets `_responseReceipts[commitment]` (replay protection for the *response*) before the external call — correct CEI for that one piece of state.
2. Calls out to `_bytesToAddress(response.request.from)` — an arbitrary, attacker-controlled contract address supplied by whichever module originally dispatched the GET request.
3. Only **after** that external call returns successfully does it read `_requestCommitments[commitment].fee` and `safeTransfer` the fee to `relayer`.

Nowhere in the reviewed control flow is `_requestCommitments[commitment]` cleared or the fee zeroed once it has been paid out for a GET response delivery. Because the untrusted callee runs *before* the fee bookkeeping step, and there is no guard preventing the same commitment's response from being reprocessed mid-call, this mirrors the `_processRewards()`/`getReward()` ordering bug in the report: external call happens first, reward-relevant state mutation happens last.

### Impact Explanation
If the destination module behind `response.request.from` is (or becomes, e.g. via upgradeable proxy) malicious or compromised, its `onGetResponse` callback could attempt to trigger `dispatchIncoming` to reprocess the same GET response/commitment path (directly or through a secondary vector) before the outer call's fee transfer executes, or could otherwise manipulate the surrounding transaction to cause the fee to be paid out more than once against `_requestCommitments[commitment].fee`, which is never invalidated post-payment in this path. This would drain the fee token balance held for relayer compensation.

### Likelihood Explanation
Reachability requires that `_bytesToAddress(response.request.from)` be attacker-influenced or a compromised legitimate module, and that the handler is invoked with `restrict(_hostParams.handler)` — meaning only Hyperbridge's own `HandlerV2` can call `dispatchIncoming` after proof verification. This substantially reduces likelihood versus a fully permissionless entry point, since the relayer cannot directly force reentrant calls; the reentrancy vector depends on the destination module contract's own callback logic being exploitable. I was not able to fully verify within the available context whether `_requestCommitments[commitment]` is cleared elsewhere in the file for the GET-response path (grep returned 20 occurrences across the file that I could not fully enumerate before running out of iterations), so I cannot confirm with certainty whether a genuine double-payout is achievable versus already mitigated by state elsewhere.

### Recommendation
Apply Checks-Effects-Interactions: compute and clear/zero the fee amount in `_requestCommitments[commitment]` (or mark it consumed) **before** making the external `.call()` to the destination module, then perform the `safeTransfer` using the pre-read value. This matches the recommendation in the source report (update rewards data before making external calls).

### Proof of Concept
Not fully constructable from the indexed context alone — a concrete PoC would require confirming (a) that `_requestCommitments[commitment]` is not cleared elsewhere for the GET-response path, and (b) a feasible reentry vector back into `dispatchIncoming` given the `restrict(_hostParams.handler)` guard. I recommend a Devin session with full repository access to trace all writes/reads to `_requestCommitments` in `evm/src/core/EvmHost.sol` and attempt a Foundry reentrancy PoC analogous to `evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol` (which demonstrates the codebase's established pattern for testing/fixing this exact bug class in `IntentGatewayV2`) before treating this as confirmed.

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
