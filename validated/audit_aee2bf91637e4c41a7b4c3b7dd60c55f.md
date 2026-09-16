### Title
No Guarantee a Delivered POST Request/Response Is Actually Processed by the Destination App — relayer fees paid and receipts finalized based solely on raw-call `success`, not actual execution - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatchIncoming` (for both `PostRequest` and `GetResponse`) and `dispatchTimeOut` (for both `GetRequestTimeout` and `PostRequestTimeout`) deliver messages to destination `IApp` contracts using a raw low-level `.call()` and treat the boolean `success` return value as proof that the delegated action (`onAccept`/`onGetResponse`/`onGetTimeout`/`onPostRequestTimeout`) was actually executed. This is the same failure mode described in the external report: a call can "succeed" (not revert) without the intended logic running, because the destination contract merely needs to not revert on the given calldata — e.g. via a permissive fallback function (common in smart-contract wallets, Gnosis-Safe-style fallback handlers, or proxies whose implementation lacks the expected selector). Because `EvmHost` only checks `success`, it (a) permanently finalizes the request/response receipt so it can never be retried, and (b) pays out the protocol/relayer fee, even though the destination app never processed the message.

### Finding Description
In `dispatchIncoming(PostRequest, address)`: [1](#0-0) 
the function stores the request receipt (`_requestReceipts[commitment] = relayer`) and then performs `destination.call(abi.encodeWithSelector(IApp.onAccept.selector, ...))`. If `success` is `true` the receipt is kept and `PostRequestHandled` is emitted — there is no verification that `onAccept` (the actual delegated action) executed any logic, only that the call did not revert.

In `dispatchIncoming(GetResponse, address)`: [2](#0-1) 
the same pattern occurs, but with a direct monetary consequence: on `success == true` the function immediately pays the relayer the fee held in `_requestCommitments[commitment].fee` via `IERC20(feeToken()).safeTransfer(relayer, fee)`. This payment is not conditioned on the app having actually acted on the response — only on the raw call not reverting.

The same unconditional-payment-on-`success` pattern repeats for both timeout paths: [3](#0-2) 
where `meta.fee` is refunded to the relayer purely based on the call's `success` bit.

This mirrors the report's root cause exactly: the delegation/dispatch layer (`DelegationManager` in the report, `EvmHost` here) has no way to distinguish "callee executed the intended action" from "callee's code path silently swallowed the call without reverting." The report calls for verifying the callee's codehash/implementation before trusting execution; `EvmHost` performs no equivalent verification beyond `extcodesize(destination) != 0`, which only confirms *some* code exists, not that the expected selector/logic exists or ran.

### Impact Explanation
- Destination applications receiving cross-chain messages/responses are commonly proxy or smart-account style contracts (e.g. Safe-style fallback handlers, ERC-4337 accounts, upgradeable proxies) which by design accept arbitrary calldata without reverting. If such a contract is (or is upgraded to be) the registered `IApp` at `request.to` / `response.request.from`, every message routed to it will report `success = true` while never running `onAccept`/`onGetResponse` logic.
- For `dispatchIncoming(PostRequest)`, this permanently records the request as delivered (`_requestReceipts` never cleared), so the source-chain message can never be replayed or legitimately timed out for real execution — a **route unable to deliver messages** even though the relayer is the only one billed for delivery.
- For `dispatchIncoming(GetResponse)` and both `dispatchTimeOut` variants, the relayer is paid the escrowed protocol fee (`feeToken()` transfer) for a delivery/timeout that produced no actual application-side effect — an **unbacked/unauthorized fee payout** drained from `_requestCommitments`, i.e. concrete loss of escrowed funds with no corresponding service rendered.
- Any stateful app logic gated on message delivery (analogous to the report's `ERC20AllowanceEnforcer`/`LimitedCallsEnforcer`) will silently diverge from the on-chain "delivered" state recorded by `EvmHost`.

### Likelihood Explanation
Medium-to-High. No privileged Hyperbridge role is required — only that the *destination app address* (controlled by whichever third party registers to receive Hyperbridge messages) is, or becomes, a contract whose fallback does not revert for the `onAccept`/`onGetResponse`/`onGetTimeout`/`onPostRequestTimeout` selectors. This is a very common real-world contract shape (Safe modules/fallback handlers, minimal proxies with permissive fallbacks, multisig wallets), so it can occur without any malicious intent from the app owner, and is fully reachable by any relayer simply delivering a normal, otherwise-valid proof/message.

### Recommendation
Do not rely on raw `.call()` success alone as proof of execution:
1. Require destination apps to return explicit success data (e.g., a magic-value return, similar to ERC-165/`onERC721Received` patterns) and check `returndata` matches the expected selector/value before treating the action as executed.
2. Alternatively, verify at dispatch time that the destination's codehash corresponds to an approved/whitelisted `IApp` implementation before crediting fee payment or finalizing the receipt, per the report's own recommendation for the delegation manager.
3. Decouple relayer fee payment from raw call success — e.g., only pay out after an explicit application acknowledgment, or require apps to opt into a stricter interface that reverts by default (no catch-all fallback) so that failures are observable and the existing "delete receipt / restore commitment for retry" path is exercised correctly instead of silently finalizing.

### Proof of Concept
1. Deploy a `VictimApp` contract as the registered destination (`request.to`) that implements `IApp` interface only nominally but has a catch-all `fallback() external payable {}` (a pattern used by many Safe-style/smart-account contracts for compatibility).
2. A relayer submits a valid `PostRequestMessage` for a POST request whose `to` field is `VictimApp`. `HandlerV2` verifies the state proof, and calls `EvmHost.dispatchIncoming(request, relayer)`.
3. Inside `dispatchIncoming`, `destination.call(abi.encodeWithSelector(IApp.onAccept.selector, ...))` hits `VictimApp`'s fallback, which does nothing and returns successfully, `success == true`. [4](#0-3) 
4. `_requestReceipts[commitment]` remains set and `PostRequestHandled` is emitted — the protocol considers the message permanently delivered even though `VictimApp` never processed it, and (for the `GetResponse`/timeout variants) the relayer is paid the escrowed fee for a no-op delivery. [5](#0-4)

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

**File:** evm/src/core/EvmHost.sol (L856-906)
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
