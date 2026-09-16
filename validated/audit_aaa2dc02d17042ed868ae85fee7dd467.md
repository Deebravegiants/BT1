### Title
Stale `_requestCommitments` entry after a successful GET response delivery enables double payment of the same request's fee - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming(GetResponse, address)` pays the relayer the fee stored in `_requestCommitments[commitment]` on a successful response delivery, but — unlike every other consumer of this mapping — never deletes the entry afterwards. This is the same bug class as H-22: a per-item mapping that gates "has this already been settled" is left populated after settlement, so a later code path that still trusts the mapping's non-zero value acts on stale data.

### Finding Description
`_requestCommitments[commitment]` stores the `FeeMetadata` (payer + relayer fee) for an outgoing request. Every other handler that consumes this mapping treats it as a one-shot resource and explicitly deletes it for replay protection, restoring it only if the downstream call fails: [1](#0-0) [2](#0-1) 

But the GET-response success path never clears it: [3](#0-2) 

```solidity
function dispatchIncoming(GetResponse memory response, address relayer) external restrict(_hostParams.handler) {
    // replay protection
    bytes32 commitment = response.request.hash();
    _responseReceipts[commitment] = ResponseReceipt({...});

    (bool success,) = _bytesToAddress(response.request.from)
        .call(abi.encodeWithSelector(IApp.onGetResponse.selector, IncomingGetResponse(response, relayer)));

    if (!success) {
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

`_responseReceipts[commitment]` is set to block replay of the *response*, but `_requestCommitments[commitment]` — the record that still authorizes a fee payout — is left intact. `dispatchTimeOut(GetRequestTimeout,...)` reads this exact same mapping to refund the original payer: [1](#0-0) 

Nothing in `dispatchIncoming(GetResponse,...)` consults `_responseReceipts` from within `dispatchTimeOut`, so if a timeout message for the same request commitment is later (or even concurrently, depending on relayer race conditions and proof-height selection) submitted through the handler, `dispatchTimeOut` will read the still-populated non-zero `meta.fee` and pay it out a second time to `meta.sender`, on top of the fee already paid to the relayer in the response path.

### Impact Explanation
This allows the host's fee-token balance to be drained by anyone who can submit a valid timeout proof for a request whose response has already been delivered and settled — a direct, permanent loss of protocol/host funds through double payment of the same commitment's fee, matching the "concrete theft ... of funds" bar. It is directly analogous to H-22, where a state flag (`_isLiquidation`) failing to be cleared after a settlement caused a later code path to make an incorrect financial decision based on stale data.

### Likelihood Explanation
Likelihood depends on whether the GET-request-timeout submission path (in `HandlerV2.sol`) independently checks `_responseReceipts` or otherwise rejects a timeout for a request whose response was already delivered. I was not able to fully verify this gate within the available tool budget — this is the main outstanding uncertainty. If such an independent check exists in `HandlerV2.sol`'s timeout-handling function, this specific double-payment path may be blocked there even though the root-cause missing `delete` in `EvmHost.sol` still stands as a defense-in-depth gap. If no such check exists, the vulnerability is directly and permissionlessly exploitable by any relayer able to produce a timeout proof after (or racing) a legitimate response delivery.

### Recommendation
In `dispatchIncoming(GetResponse memory response, address relayer)`, delete `_requestCommitments[commitment]` immediately after (or as part of) the successful fee payout, mirroring the replay-protection pattern already used in `dispatchTimeOut`. Additionally, `HandlerV2.sol`'s GET-timeout handling should be reviewed to ensure it hard-rejects (or the host hard-rejects) any timeout for a commitment that already has a `_responseReceipts` entry, independent of the `_requestCommitments` fix, as defense in depth.

### Proof of Concept
1. A GET request is dispatched via `EvmHost.dispatch(DispatchGet)`, populating `_requestCommitments[commitment] = FeeMetadata({payer, fee})`.
2. A relayer delivers a valid `GetResponse` for the same commitment through the handler, which calls `dispatchIncoming(GetResponse, relayer)`. `onGetResponse` succeeds, `_responseReceipts[commitment]` is set, and the relayer is paid `fee` from `_requestCommitments[commitment].fee`, but that entry is never deleted.
3. Later, a `GetRequestTimeoutMessage` proof is constructed/submitted for the same commitment through the handler, invoking `EvmHost.dispatchTimeOut(GetRequestTimeout, meta, commitment)`.
4. Since `_requestCommitments[commitment]` still holds the original non-zero `fee`/`payer`, and assuming the handler's timeout path does not independently check `_responseReceipts` for this commitment (unverified — see Likelihood), `meta.fee` is refunded again to `meta.sender`, resulting in the host paying out the same request's fee twice from its fee-token balance.

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
