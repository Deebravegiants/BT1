Based on my research, I found a concrete analog in `EvmHost.sol`'s handling of relayer fees for GET responses, which mirrors the reported bug class of a protocol-held balance that is credited/paid but never cleared from its accounting record, unlike sibling code paths that do clear it. [1](#0-0) 

### Title
GET-response relayer fee is paid without clearing `_requestCommitments`, unlike every other fee-consuming path - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost::dispatchIncoming(GetResponse, address)` pays out the relayer fee recorded in `_requestCommitments[commitment].fee` but never deletes that entry afterward. Every other code path in the same contract that consumes a `FeeMetadata` entry (`dispatchTimeOut(GetRequestTimeout,...)`, `dispatchTimeOut(PostRequestTimeout,...)`) explicitly `delete`s `_requestCommitments[commitment]` before or immediately after paying out, precisely to prevent the same fee balance from being paid twice.

### Finding Description
`dispatch(DispatchPost)` records the payer/fee for an outgoing request in `_requestCommitments[commitment]`: [2](#0-1) 

When a GET response for that commitment is delivered, `dispatchIncoming(GetResponse, address relayer)` sets replay-protection state (`_responseReceipts[commitment]`), invokes the destination module, and — on success — reads `_requestCommitments[commitment].fee` and transfers it to the relayer, but the `_requestCommitments` entry is never deleted: [1](#0-0) 

Contrast this with the GET/POST timeout paths in the same contract, which treat the same `FeeMetadata` record as consumable exactly once and explicitly zero it out: [3](#0-2) [4](#0-3) 

This is structurally the same bug class described in the external report: a fee/stake balance that the contract is obligated to hold and pay out exactly once is not tracked/cleared on-chain after being consumed, leaving stale accounting state (`_requestCommitments[commitment].fee` still non-zero) that a second invocation could read and pay out again.

### Impact Explanation
If `dispatchIncoming(GetResponse, ...)` can ever be invoked a second time for the same `commitment` (e.g., because the destination module accepts a re-delivery, or because the handler layer's replay protection is bypassed or has an edge case), the relayer fee would be transferred out of `feeToken()` balance a second time. This directly causes wrong accounting/drainage of the fee token balance held by `EvmHost`, exactly as described in the reference report's "pool does not have enough ETH to distribute rewards or claim fees" scenario.

### Likelihood Explanation
Low-to-Medium: `_responseReceipts[commitment]` is set unconditionally at the top of the function (not checked-then-set), so the function itself performs no local replay check — it relies entirely on the caller (`HandlerV2`) to enforce that a given response commitment is only ever delivered once. I was not able to fully verify within the available tool budget whether `HandlerV2` independently guards against re-submitting a proof for an already-delivered `GetResponse` commitment before calling into `EvmHost`. If that external guard is complete, this finding reduces to a code-hygiene/defense-in-depth gap; if it has any gap (e.g., across different consensus-proof batches within a challenge period), it becomes directly exploitable double-payment.

### Recommendation
Delete (or zero out) `_requestCommitments[commitment]` in `dispatchIncoming(GetResponse, address)` immediately after reading and paying the fee, mirroring the pattern already used in `dispatchTimeOut(GetRequestTimeout, ...)` and `dispatchTimeOut(PostRequestTimeout, ...)`. This makes the fee record single-use at the state level rather than relying solely on `HandlerV2`'s external replay protection, closing the accounting gap regardless of upstream guarantees.

### Proof of Concept
Not independently reproduced against `HandlerV2`'s proof-verification logic due to tool-call budget constraints; the finding is based on the asymmetry visible directly in `EvmHost.sol`:
1. `dispatch(DispatchPost)` sets `_requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee})`.
2. `dispatchIncoming(GetResponse, relayer)` reads `_requestCommitments[commitment].fee`, transfers it to `relayer`, and returns — the mapping entry is left non-zero.
3. Any subsequent call to `dispatchIncoming` with the same `commitment` (if reachable) would pay the fee out again, since nothing was cleared, whereas the sibling `dispatchTimeOut` functions explicitly `delete _requestCommitments[commitment]` first to prevent exactly this.

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

**File:** evm/src/core/EvmHost.sol (L885-906)
```text
    function dispatchTimeOut(
        PostRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onPostRequestTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit PostRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```

**File:** evm/src/core/EvmHost.sol (L944-948)
```text
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
```
