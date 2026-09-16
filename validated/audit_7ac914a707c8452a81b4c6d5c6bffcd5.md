### Title
Governance `withdraw()` on `EvmHost` can drain the fee-token balance needed to pay already-escrowed relayer fees, permanently freezing those funds - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.withdraw()` transfers an arbitrary amount of the `feeToken` (or native token) out of the host contract to a beneficiary chosen by cross-chain governance, with no check against the fees the host has already escrowed on behalf of relayers for outstanding GET requests/responses and timed-out POST/GET requests. This mirrors the Illuminate `withdraw`/`withdrawFee` conflict: a privileged withdrawal path that ignores a separate, still-owed liability tracked elsewhere in the contract, so the liability becomes unpayable once the balance is pulled out from under it.

### Finding Description
`EvmHost` escrows relayer fees per request commitment in `_requestCommitments[commitment].fee` (`FeeMetadata`) at dispatch time. These escrowed fees are paid out later, directly from the contract's `feeToken` balance, in multiple code paths:

- `dispatchIncoming(GetResponse, address relayer)`: after a successful `onGetResponse` call, `IERC20(feeToken()).safeTransfer(relayer, fee)` pays the relayer the fee recorded in `_requestCommitments[commitment].fee`. [1](#0-0) 
- `dispatchTimeOut(GetRequestTimeout, meta, commitment)` and the POST-timeout overload refund `meta.fee` back to `meta.sender` from the same `feeToken` balance. [2](#0-1) 

None of these payout sites reserve or "lock" the fee-token balance against `withdraw()`. The governance-only `withdraw()` function transfers `params.amount` of `params.token` (native or `feeToken`) straight to `params.beneficiary` via `IERC20(params.token).safeTransfer` (or a raw native call), with the only guard being the ERC20's own balance check: [3](#0-2) 

`withdraw()` is reachable via `HostManager.onAccept`, which decodes a `Withdraw` governance action from a request that has already passed proof verification and the Hyperbridge-source / admin-relayer checks, then calls `IHostManager(_params.host).withdraw(withdrawParams)`: [4](#0-3) 

Because `withdraw()` has no visibility into (or check against) the sum of outstanding `_requestCommitments[...].fee` values still owed to relayers/payers for pending GET requests and un-timed-out requests, a governance withdrawal that pulls the `feeToken` balance down below that outstanding total will leave insufficient balance for future `dispatchIncoming(GetResponse,...)` fee payouts or `dispatchTimeOut(...)` refunds. Those `safeTransfer` calls will then revert, `dispatchIncoming`/`dispatchTimeOut` execution will fail (the calling handler transaction reverts, since these payouts are not wrapped in a try/catch the way `onAccept` calls are), and the escrowed relayer fee/refund becomes permanently stuck — exactly analogous to Illuminate's `fees[eToken]` becoming unpayable after `withdraw(eToken)` zeroed the contract's eToken balance.

### Impact Explanation
Relayers who already delivered a GET response, or applications/payers awaiting a timeout refund, can have their earned/escrowed `feeToken` funds become undeliverable once governance (or a compromised/careless governance-controlled `HostManager`) withdraws host revenue without accounting for outstanding commitments. This is a freezing-of-funds bug: legitimate relayer fee payouts and payer refunds revert indefinitely (or until new `feeToken` balance is deposited by other means), directly matching the "Medium" severity class of the referenced Illuminate finding (fee withdrawal path rendered non-functional due to a separate withdrawal draining the tracked balance).

### Likelihood Explanation
Requires a legitimate governance `Withdraw` action to be dispatched from Hyperbridge and delivered by the authorized admin relayer — this is a normal, expected operational flow (not a malicious-admin scenario per se, since governance is not assumed malicious, only unaware of outstanding commitments), making it a routine consequence of decoupled accounting rather than a privileged-attacker exploit. Given `withdraw()` reads only the raw `feeToken` balance with no accounting for `_requestCommitments`, any withdrawal sized close to the current on-chain `feeToken` balance can trigger this under normal operation whenever there are outstanding GET requests/responses in flight.

### Recommendation
Track a running total of currently-escrowed relayer fees (sum of `_requestCommitments[...].fee` for all non-finalized GET requests and pending POST/GET timeouts) and enforce in `withdraw()` that the withdrawable amount cannot reduce the `feeToken` balance below that reserved total. Alternatively, maintain a `reservedFees` accumulator incremented on dispatch and decremented on payout/refund/timeout, and have `withdraw()` compute `withdrawable = IERC20(feeToken()).balanceOf(address(this)) - reservedFees` as the cap for any `Withdraw` governance action targeting the fee token.

### Proof of Concept
1. A user dispatches a GET request via `EvmHost`, attaching a relayer fee `F` in `feeToken`; this fee is transferred into the host and recorded in `_requestCommitments[commitment].fee = F`.
2. Governance/admin observes the host's `feeToken` balance (which includes `F` plus any protocol revenue) and dispatches a `Withdraw` action for the full observed balance to a treasury address; `HostManager.onAccept` delivers it and `EvmHost.withdraw()` transfers the entire balance out, per [5](#0-4) .
3. The relayer later submits the proof of the GET response; `HandlerV2` calls `EvmHost.dispatchIncoming(GetResponse, relayer)`. After `onGetResponse` succeeds, the host attempts `IERC20(feeToken()).safeTransfer(relayer, F)` per [6](#0-5) , which reverts because the host's `feeToken` balance is now `0 < F`.
4. The relayer's earned fee `F` is permanently unrecoverable through the normal payout path (the `_requestCommitments` entry for the delivered request may even be cleared/stuck depending on retry semantics), reproducing the Illuminate-style "withdraw before withdrawFee" freeze.

### Citations

**File:** evm/src/core/EvmHost.sol (L647-660)
```text
    /**
     * @dev withdraws host revenue to the given address, can only be called by cross-chain governance
     * @param params, the parameters for withdrawal
     */
    function withdraw(WithdrawParams memory params) external restrict(_hostParams.hostManager) {
        if (params.token == address(0)) {
            // this is safe because re-entrancy is mitigated before dispatching requests
            (bool sent,) = params.beneficiary.call{value: params.amount}("");
            if (!sent) revert WithdrawalFailed();
        } else {
            IERC20(params.token).safeTransfer(params.beneficiary, params.amount);
        }
        emit HostWithdrawal({beneficiary: params.beneficiary, amount: params.amount, token: params.token});
    }
```

**File:** evm/src/core/EvmHost.sol (L824-846)
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
```

**File:** evm/src/core/EvmHost.sol (L856-900)
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

```

**File:** evm/src/core/HostManager.sol (L134-148)
```text
    function onAccept(IncomingPostRequest calldata incoming)
        external
        override
        restrict(msg.sender, _params.host)
        restrict(incoming.relayer, _params.admin)
    {
        PostRequest calldata request = incoming.request;
        // Only the Hyperbridge parachain can send requests to this module.
        if (!request.source.equals(IHost(_params.host).hyperbridge())) revert UnauthorizedAction();

        OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
        if (action == OnAcceptActions.Withdraw) {
            // This is where governance & relayers can withdraw their revenue.
            WithdrawParams memory withdrawParams = abi.decode(request.body[1:], (WithdrawParams));
            IHostManager(_params.host).withdraw(withdrawParams);
```
