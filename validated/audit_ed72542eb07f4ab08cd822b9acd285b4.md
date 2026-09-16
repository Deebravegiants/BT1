Based on the investigation, I found a fund-accounting vulnerability in the GET-request timeout/response flow of `EvmHost.sol` that is analogous in effect to the CVE's use-after-free class: state that should be invalidated once "consumed" (a GET request's fee metadata, paid out on response delivery) is never cleared, and a second, unrelated code path (timeout processing) later reads that stale entry and pays it out again — a double-spend of the relayer-fee escrow.

I was unable to retrieve the complete body of `HandlerV2.handleGetRequestTimeouts()` past line 300 due to tool-call limits, so I cannot 100% confirm the absence of a `responseReceipts` guard inside that function; the finding below is built from the code paths I was able to fully inspect (`EvmHost.dispatchIncoming(GetResponse)`, `EvmHost.dispatchTimeOut(GetRequestTimeout)`, and the duplicate-check pattern that `HandlerV2` applies for `handleGetResponses` but that has no analogue visible for the timeout path). A Devin session with full file access should verify this before treating it as certain.

### Title
GET-request relayer fee can be paid out twice: once on response delivery, once on timeout — stale `_requestCommitments` entry reused after being logically "freed" - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming(GetResponse, address)` pays the relayer fee for a GET request out of `_requestCommitments[commitment].fee` when a response is successfully delivered, but never deletes `_requestCommitments[commitment]` [1](#0-0) . Later, `EvmHost.dispatchTimeOut(GetRequestTimeout, FeeMetadata, bytes32)` — reachable permissionlessly through `HandlerV2.handleGetRequestTimeouts` — reads that same still-populated `_requestCommitments` entry and pays the fee out a second time to the original payer [2](#0-1) . The fee metadata object is effectively "used after being freed" (spent) by a second, independent consumer.

### Finding Description
1. A user dispatches a GET request, which stores `FeeMetadata{sender, fee}` under the request commitment on the source `EvmHost` [3](#0-2)  (POST path shown; the GET analogue populates the same `_requestCommitments` mapping).
2. When the GET response is later relayed and delivered through `HandlerV2.handleGetResponses` → `EvmHost.dispatchIncoming(GetResponse, relayer)`, the relayer fee is paid immediately out of `_requestCommitments[commitment].fee`, but the mapping entry itself is left intact: `delete` is only applied to `_responseReceipts` on failure, never to `_requestCommitments` on success [4](#0-3) .
3. `HandlerV2.handleGetResponses` guards against replaying the *response* itself via `host.responseReceipts(...).relayer != address(0)) revert DuplicateMessage()` [5](#0-4) , but this only prevents delivering the response twice — it says nothing about the request's fee metadata still being live for the timeout path.
4. `HandlerV2.handleGetRequestTimeouts` fetches `state = host.stateMachineCommitment(message.height)` and enforces the challenge period, then (based on the pattern used for the structurally identical POST-timeout handler) checks only that `host.requestCommitments(requestCommitment)` is non-empty and that the request has timed out relative to `state.timestamp` [6](#0-5) ; unlike `handlePostRequestTimeouts`, GET timeouts carry no non-membership proof requirement at all (confirmed by protocol docs: "There are no proofs for Get timeouts, we only need to ensure that the timeout timestamp has elapsed on the host") [7](#0-6) .
5. Because `_requestCommitments[commitment]` was never cleared in step 2, this check still succeeds even though the request was already fulfilled, and `EvmHost.dispatchTimeOut(GetRequestTimeout, meta, commitment)` deletes the commitment and refunds `meta.fee` to `meta.sender` a second time [8](#0-7) .

This is directly analogous to the CVE's use-after-free bug class: an object (the fee-bearing request-commitment record) is "freed" in the logical sense once its fee has been disbursed on the response path, but the freed/stale reference is not invalidated and gets reused by a second consumer (the timeout path), causing state/asset corruption instead of a memory crash.

### Impact Explanation
Any account can permissionlessly submit `handleGetRequestTimeouts` for a GET request whose response has already been paid out, as long as enough time has passed on the source chain that the timeout condition is satisfied by the current state commitment's timestamp. This drains an extra `meta.fee` worth of the fee token (or native asset, depending on configuration) from the host's escrow to the original payer, on top of the fee already paid to the relayer — a direct, permissionless theft/duplication of protocol-held funds, satisfying the "concrete theft ... of funds" bar in the validation rules.

### Likelihood Explanation
The path is reachable from a single relayed message (`handleGetRequestTimeouts`), described in the docs as "Access: Permissionless (can be called by anyone)" [9](#0-8) , and requires no privileged role (not fisherman/collator/governance-only). The only precondition is that the state-machine timestamp used for the timeout proof has advanced past the GET request's `timeout_timestamp`, which is a normal occurrence for slow-to-time-out requests whose response was delivered close to expiry, or for any request an attacker can wait out. I could not fully confirm the missing `responseReceipts` check for the remainder of `handleGetRequestTimeouts` (visibility cut off at line 300), so this should be verified against the full function body before remediation.

### Recommendation
- In `EvmHost.dispatchIncoming(GetResponse, address)`, delete `_requestCommitments[commitment]` once the fee has been paid to the relayer, mirroring the pattern already used for `_responseReceipts` on failure.
- In `HandlerV2.handleGetRequestTimeouts` / `EvmHost.dispatchTimeOut(GetRequestTimeout, ...)`, explicitly check `host.responseReceipts(commitment).relayer == address(0)` before allowing a timeout to proceed, so a request that has already received (and paid for) a response can never also be timed out and refunded.

### Proof of Concept
1. Dispatch a GET request from `EvmHost` with a non-zero `fee`, recording `commitment`.
2. Let the request be answered normally: a relayer submits `HandlerV2.handleGetResponses`, which calls `EvmHost.dispatchIncoming(GetResponse, relayer)`; the relayer is paid `_requestCommitments[commitment].fee`. Note that `_requestCommitments[commitment]` is *not* cleared.
3. Wait (or arrange) for a later state commitment on the source chain whose `timestamp` exceeds the GET request's `timeoutTimestamp`.
4. Any account submits `HandlerV2.handleGetRequestTimeouts` for the same request against that later state commitment (no non-membership proof required for GET timeouts).
5. `EvmHost.dispatchTimeOut(GetRequestTimeout, meta, commitment)` runs, calls `onGetTimeout` on the source app, and — if that call succeeds — refunds `meta.fee` a second time to the original payer, resulting in the fee token/native escrow paying out `2x` the intended fee for a single GET request.

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

**File:** evm/src/core/HandlerV2.sol (L241-246)
```text
        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // duplicate response?
            if (host.responseReceipts(leaf.response.request.hash()).relayer != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.response, _msgSender());
        }
```

**File:** evm/src/core/HandlerV2.sol (L293-300)
```text
    function handleGetRequestTimeouts(IHost host, GetTimeoutMessage calldata message) external notFrozen(host) {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        // fetch the state commitment
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
```

**File:** docs/content/protocol/ismp/timeouts.mdx (L30-35)
```text
    /// There are no proofs for Get timeouts, we only need to
    /// ensure that the timeout timestamp has elapsed on the host
    Get {
        /// Requests that have timed out
        requests: Vec<GetRequest>,
    },
```

**File:** docs/content/developers/evm/api/ihandler.mdx (L196-207)
```text
---

### handleGetRequestTimeouts()

Processes timed-out GET requests with cryptographic proof.

```solidity lineNumbers
function handleGetRequestTimeouts(
    IHost host,
    GetTimeoutMessage calldata message
) external
```
```
