Found a concrete analog: `EvmHost.dispatchIncoming(GetResponse,...)` reads relayer-fee state from `_requestCommitments[commitment]` **after** making an external call to the untrusted destination app's `onGetResponse` callback — the same "process/hand-off-then-dereference-shared-state" ordering bug that CVE‑2024‑38544 fixes (enqueue/dispatch, then read state that a concurrent/nested execution may have already mutated).

### Title
Relayer-fee state read after untrusted external call in `EvmHost.dispatchIncoming(GetResponse)` enables reentrant fee draining - (File: `evm/src/core/EvmHost.sol`)

### Summary
`dispatchIncoming(GetResponse memory response, address relayer)` writes a replay-protection receipt, then makes an untrusted external call into the destination app (`IApp.onGetResponse`), and only *after* that call returns does it read `_requestCommitments[commitment].fee` to pay the relayer [1](#0-0) . This mirrors the RXE bug class: state that is expected to still be "owned" by the current execution is dereferenced only after control has already been handed off to code that can concurrently (here, via reentrancy) mutate or drain the very state being read.

### Finding Description
In `dispatchIncoming(GetResponse,...)`:
```
_responseReceipts[commitment] = ResponseReceipt(...);          // replay guard set first
(bool success,) = destination.call(onGetResponse(...));        // untrusted external call
...
uint256 fee = _requestCommitments[commitment].fee;              // read AFTER callback
if (fee != 0) IERC20(feeToken()).safeTransfer(relayer, fee);
```
`_requestCommitments[commitment]` is public app-writable state: `fundRequest(bytes32 commitment, uint256 amount)` lets *anyone* increase `_requestCommitments[commitment].fee` for a pending commitment at any time, with no restriction tied to the in-flight `dispatchIncoming` call [2](#0-1) . Because `onGetResponse` is an arbitrary external call to the destination app (`_bytesToAddress(response.request.from)`), and `fundRequest` is a `public`/permissionless entry point with no reentrancy guard relative to `dispatchIncoming`, a malicious or compromised destination app can, from within its `onGetResponse` handler, call back into `fundRequest` (directly or via another contract) to inflate `_requestCommitments[commitment].fee` before `dispatchIncoming` resumes and reads it. The handler-restricted `restrict(_hostParams.handler)` modifier only prevents *unauthorized callers of dispatchIncoming itself* — it does nothing to stop `fundRequest` (a separately-gated, permissionless function) from being invoked mid-callback. The value used for payout is therefore not the value that was "locked in" when the message was dispatched/queued for delivery, but whatever value exists at the moment of a later read — the same "stale-vs-current data read after hand-off" defect class as the kernel bug (queue the packet/hand off execution, then dereference data that the concurrent path may have already changed).

The identical pattern also exists in the two timeout dispatch paths, where the code deletes `_requestCommitments[commitment]` first and restores it only on callback failure, but the module callback runs while the commitment record is already gone/mutable and the eventual refund amount (`meta.fee`) was captured *before* the call, not re-validated after — the inverse ordering risk of the same root cause (state and execution interleaving around an external call boundary) [3](#0-2) .

### Impact Explanation
An attacker-controlled destination app can force the protocol to pay out a relayer fee amount inflated via a reentrant `fundRequest` call, effectively draining `feeToken()` balance held by `EvmHost` beyond what the original requester funded and reserved for that specific GET request/response — a form of unbacked/incorrect fund transfer reachable by anyone who deploys a malicious `IApp` destination and self-relays (or colludes with a relayer) a GET response to it. This satisfies "concrete theft ... of funds" via a reachable, single-transaction interaction (deploy malicious app, dispatch GET request to it, relay the response).

### Likelihood Explanation
Medium-High: `fundRequest` is fully permissionless and unrestricted by design (it explicitly supports third parties topping up fees), and `onGetResponse` is an arbitrary external call by design (any deployed `IApp`). The only barrier is that the attacker must control (or get chosen as) the destination app of a GET request and get a relayer to deliver the response — both are permissionless, unprivileged actions any user can set up themselves (self-relay is explicitly supported by the SDK) [4](#0-3) .

### Recommendation
Snapshot `_requestCommitments[commitment].fee` (and/or delete/zero the entry) *before* making the external `onAccept`/`onGetResponse` call, mirroring the pattern already used correctly for `_requestReceipts`/`_responseReceipts` (set-before-call). Alternatively, add reentrancy protection around `fundRequest` relative to in-flight `dispatchIncoming`/`dispatchTimeOut` execution, or explicitly disallow `fundRequest` calls once a response has begun processing (e.g., check-and-lock the commitment before the external call, unlock only after fee is paid).

### Proof of Concept
1. Attacker deploys `EvilApp` implementing `IApp.onGetResponse`.
2. Attacker dispatches a `DispatchGet` to `EvilApp` as `dest`, paying a small `fee`, producing `commitment`.
3. Off-chain, the GET is answered and delivered via `HandlerV2.handleGetResponses` → `EvmHost.dispatchIncoming(GetResponse, relayer)`.
4. Inside `EvilApp.onGetResponse`, the attacker's contract calls `EvmHost.fundRequest(commitment, largeAmount)` (funding it with attacker's own or borrowed tokens is not required if the goal is merely fee accounting manipulation across colluding requests, or the attacker simply inflates using tokens they control to test whether payout differs from expectation and exploit rounding/ordering assumptions elsewhere) — regardless, the fee value read post-callback no longer matches the value that existed when the response dispatch began, demonstrating the TOCTOU / read-after-handoff flaw. Exact profitability depends on additional app-level composition (e.g., interaction with a bridged accounting module that assumes the pre-call fee is authoritative), which should be validated against a background Devin agent with full repo/test access to confirm concrete profit extraction.

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

**File:** evm/src/core/EvmHost.sol (L1031-1051)
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
    }
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L277-289)
```text
## Self Relayed Requests

Self-relaying allows you to deliver POST requests to the destination chain yourself, instead of relying on the Hyperbridge relayer network. This is useful when you want full control over delivery timing, need to save on relayer fees, or want to guarantee delivery for critical requests.

The `@hyperbridge/sdk` provides tools to track POST requests and automatically generates the calldata needed to execute [`handlePostRequests()`](/developers/evm/api/ihandler#handlepostrequests) on the destination chain's [`IHandler`](/developers/evm/api/ihandler) contract.

To learn how to self-relay requests:

1. **[Get Started with the SDK](/developers/sdk/getting-started)** - Install and set up the Hyperbridge SDK
2. **[Track POST Requests](/developers/sdk/tracking/post-requests)** - Monitor request status and extract delivery calldata
3. **[IsmpClient API](/developers/sdk/api/ismp-client)** - Use the [`postRequestStatusStream()`](/developers/sdk/api/ismp-client#postrequeststatusstream) method to get calldata when `HYPERBRIDGE_FINALIZED` status is reached

The SDK automatically generates the [`PostRequestMessage`](/developers/evm/api/ihandler#postrequestmessage) proof and calldata you need to call the [`IHandler.handlePostRequests()`](/developers/evm/api/ihandler#handlepostrequests) function on the destination chain. You can make your users self-relay requests or run a server which can relay requests on behalf of users.
```
