## Title
`EvmHost.dispatchIncoming(GetResponse)` never clears `_requestCommitments`, letting the same GET request's fee be paid to a relayer and later refunded again via a timeout - (File: `evm/src/core/EvmHost.sol`)

## Summary
This mirrors the C4 finding: a state entry that should be deleted once a resource is "spent" (burned tokens / paid fee) is instead left intact, letting the same value be consumed a second time through a sibling code path. In `FlashGovernanceArbiter.burnFlashGovernanceAsset()`, the user's pending-decision entry was overwritten with config data instead of deleted, letting the user reuse/withdraw the state early. In `EvmHost.sol`, `_requestCommitments[commitment]` — the struct holding the `fee` escrowed for a dispatched GET request — is read and paid out to the relayer in `dispatchIncoming(GetResponse)` but is **never deleted**, unlike every other terminal path for the same mapping (`dispatchTimeOut` for both GET and POST requests explicitly `delete _requestCommitments[commitment]` for replay protection).

## Finding Description
`_requestCommitments[commitment]` is populated when a GET request is dispatched from this host, storing `{sender, fee}`: [1](#0-0) 

When the corresponding `GetResponse` is delivered back to this same (source) host, `dispatchIncoming(GetResponse, ...)` reads `_requestCommitments[commitment].fee` and pays it out to the relayer, but the mapping entry is left untouched: [2](#0-1) 

Compare this to the timeout paths for the very same mapping, which correctly `delete` the entry first as replay protection, and only restore it if the downstream module callback fails (so the timeout can be retried): [3](#0-2) 

Because `dispatchIncoming(GetResponse)` skips this deletion, the `FeeMetadata` (`sender`, `fee`) for an already-settled GET request remains fully populated in storage after the relayer has already been paid. `fundRequest` also treats "sender != address(0)" as the sole liveness check for a commitment, further confirming that the codebase relies on `_requestCommitments` deletion as the sole indicator that a request has been fully settled: [4](#0-3) 

If a `GetRequestTimeout` message for the same commitment is later (or concurrently) processed by the handler — using a state proof taken from a height before the response was recorded, or if the destination-side non-membership window still validates for any reason — `dispatchTimeOut` will delete the (still-populated) commitment and pay `meta.fee` to `meta.sender` as a "refund", on top of the fee that was already paid to the relayer in `dispatchIncoming(GetResponse)`. The same escrowed fee is thus paid out twice from two independent, non-mutually-exclusive code paths, because the first path fails to clear the record that marks the fee as already claimed.

## Impact Explanation
This allows unbacked double payment of the protocol's escrowed fee token: once to the relayer for delivering the response, and again to the original sender via a timeout refund, for the same GET request. This is a direct loss of protocol/fee-token funds (accounted for once but paid out twice), matching the "concrete theft ... of funds" bar for a valid analog. It is reachable by any relayer/message submitter driving both the response-delivery and timeout-message paths through the standard dispatch/handler flow — no privileged or admin role is required.

## Likelihood Explanation
Exploitation requires an attacker (or opportunistic relayer) to get a valid timeout proof accepted for a GET request whose response has already been delivered on the source host — feasible in edge cases around timing (a response landing just before/after the configured `timeoutTimestamp`, or a stale-but-still-valid non-membership proof window), since the source host itself performs no cross-check against `_responseReceipts`/prior settlement before honoring the handler-supplied timeout dispatch. This is a realistic race rather than a purely theoretical one, given the explicit `delete` pattern present in every sibling handler except this one.

## Recommendation
In `dispatchIncoming(GetResponse, address relayer)`, delete `_requestCommitments[commitment]` (mirroring the `delete` used in the timeout handlers) immediately after reading the fee and before/while paying the relayer, so that a subsequent timeout dispatch for the same commitment sees a cleared entry (`meta.sender == address(0)`, `meta.fee == 0`) and cannot pay out a second time.

## Proof of Concept
Conceptual sequence (concrete PoC would require constructing dual proofs against the handler, which was out of scope to fabricate here):
1. Dispatch a `GET` request from `EvmHost` with `fee = F`; `_requestCommitments[commitment] = {sender, F}` is stored (`evm/src/core/EvmHost.sol:999-1001`).
2. Relayer delivers the `GetResponse`; `dispatchIncoming(GetResponse, relayer)` pays `F` to `relayer` from `_requestCommitments[commitment].fee`, but leaves `_requestCommitments[commitment]` populated (`evm/src/core/EvmHost.sol:824-846`).
3. A `GetRequestTimeout` message for the same `commitment` is subsequently accepted by the handler (e.g., using a proof taken before/around the response's delivery window) and routed to `dispatchTimeOut(GetRequestTimeout, meta, commitment)`.
4. Since `_requestCommitments[commitment]` was never cleared in step 2, `meta.fee == F` is still valid, so `dispatchTimeOut` refunds `F` a second time to `meta.sender` (`evm/src/core/EvmHost.sol:856-877`), doubling the payout for a single escrowed fee.

### Citations

**File:** evm/src/core/EvmHost.sol (L820-847)
```text
    /**
     * @dev Dispatch an incoming GET response to source module
     * @param response - get response
     */
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

**File:** evm/src/core/EvmHost.sol (L849-906)
```text
    /**
     * @dev Dispatch an incoming GET timeout to the source module.
     * @notice Does not refund any protocol fees.
     * @param timeout - timed-out get request bundled with the relayer that submitted the timeout proof
     * @param meta - fee metadata for the original request
     * @param commitment - request commitment
     */
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

    /**
     * @dev Dispatch an incoming POST timeout to the source module
     * @param timeout - timed-out post request bundled with the relayer that submitted the timeout proof
     * @param meta - fee metadata for the original request
     * @param commitment - request commitment
     */
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

**File:** evm/src/core/EvmHost.sol (L999-1001)
```text
        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: _msgSender(), fee: get.fee});
```

**File:** evm/src/core/EvmHost.sol (L1031-1050)
```text
    function fundRequest(bytes32 commitment, uint256 amount) external payable notFrozen {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                amount, path, address(this), block.timestamp
            );
        } else {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), amount);
        }

        FeeMetadata memory metadata = _requestCommitments[commitment];
        if (metadata.sender == address(0)) revert UnknownRequest();

        metadata.fee += amount;
        _requestCommitments[commitment] = metadata;

        emit RequestFunded({commitment: commitment, newFee: metadata.fee});
```
