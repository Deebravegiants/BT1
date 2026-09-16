## Title
Missing zero-address validation on `DispatchPost.payer` permanently locks relayer-fee refunds - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)` accepts an application-supplied `payer` address with no validation and stores it as the fee-refund recipient. If `payer == address(0)` (whether from a buggy calling application or a malicious/careless integrator), the relayer-fee refund on timeout is sent to the zero address, permanently freezing (or reverting/relocking) protocol-held fee funds. This is the same bug class as the Connext report: unvalidated user-controlled addresses (`recovery`, `agent`) that cause funds to be sent to `address(0)` or permanently locked.

### Finding Description
`dispatch(DispatchPost)` stores the caller-supplied `post.payer` directly into `_requestCommitments[commitment]` as the `FeeMetadata.sender`, with no sanity check that it is non-zero: [1](#0-0) 

Compare this to `dispatch(DispatchGet)`, which safely uses `_msgSender()` (not a caller-supplied field) as the fee-refund address: [2](#0-1) 

When a POST request times out, `dispatchTimeOut()` first deletes the commitment (replay protection), invokes the source module's `onPostRequestTimeout` callback, and only then refunds the fee to `meta.sender` (i.e., the original `post.payer`): [3](#0-2) 

If `meta.sender == address(0)`:
- For fee tokens that follow OpenZeppelin's standard `_transfer` (which reverts on `to == address(0)`), the `safeTransfer` call reverts. Because the whole external call (originating from `HandlerV2.handlePostRequestTimeouts`) reverts atomically, the earlier `delete _requestCommitments[commitment]` is rolled back too — the request becomes permanently stuck: every future timeout-processing attempt repeats the same revert, and the escrowed relayer fee can never be recovered.
- For fee tokens that do not guard transfers to the zero address, the fee tokens are burned/sent to `address(0)`, an unrecoverable loss of funds.

This mirrors the reported class of bug precisely: the dispatch-time sanity checks omit validation of a user/application-supplied address (`payer`) that is later used as a fund-recipient in a completion/refund path, exactly like the missing `recovery != 0` check in Connext's `xcall()`.

### Impact Explanation
Any application built on top of `IDispatcher`/`EvmHost` that forwards a caller-controlled or default-uninitialized `payer` value (e.g., a struct field left at its zero value, or a bug in app-level input handling) can cause the associated relayer fee — potentially non-trivial amounts, since fees can be increased via `fundRequest()` — to be permanently frozen in the host contract or burned. This is reachable by any unprivileged application dispatching a POST request through the permissionless `dispatch()` entrypoint, satisfying the reachable "unprivileged message dispatcher" criterion.

### Likelihood Explanation
Likelihood is moderate: it does not require a malicious host/admin, only a caller (application contract) passing an incorrect/default `payer` value — an easy, plausible integration mistake, and exploitable by design by anyone building on the dispatcher who wants to lock/burn fee funds for a request. There is no on-chain check preventing it.

### Recommendation
Add a sanity check in `EvmHost.dispatch(DispatchPost)` (and any similar dispatch/fund paths) rejecting `post.payer == address(0)`, mirroring the pattern of validating `recovery != 0` / `agent != 0` recommended in the referenced report:
```solidity
if (post.payer == address(0)) revert InvalidPayer();
```
Additionally, consider validating this invariant is preserved in `fundRequest()` and any other codepath that reads `FeeMetadata.sender` as a refund target.

### Proof of Concept
1. An application contract calls `IDispatcher(host).dispatch(DispatchPost({..., payer: address(0), fee: X, ...}))`, paying fee `X` in fee tokens.
2. The request times out; a relayer submits `handlePostRequestTimeouts` on `HandlerV2`, which calls `EvmHost.dispatchTimeOut`.
3. `onPostRequestTimeout` succeeds on the source module.
4. `IERC20(feeToken()).safeTransfer(address(0), X)` executes:
   - If `feeToken` blocks transfers to `address(0)` (standard OZ ERC20), the whole transaction reverts, rolling back the `delete` of `_requestCommitments[commitment]`; the request/fee is stuck forever, un-timeoutable.
   - If `feeToken` allows it, `X` fee tokens are burned irrecoverably. [1](#0-0) [3](#0-2)

### Citations

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

**File:** evm/src/core/EvmHost.sol (L974-1013)
```text
    function dispatch(DispatchGet memory get) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                get.fee, path, address(this), block.timestamp
            );
        } else if (get.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), get.fee);
        }

        uint64 timeoutTimestamp = get.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(get.timeout);
        GetRequest memory request = GetRequest({
            source: host(),
            dest: get.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            timeoutTimestamp: timeoutTimestamp,
            keys: get.keys,
            height: get.height,
            context: get.context
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: _msgSender(), fee: get.fee});
        emit GetRequestEvent({
            source: string(request.source),
            dest: string(request.dest),
            from: request.from,
            keys: request.keys,
            nonce: request.nonce,
            height: request.height,
            context: request.context,
            timeoutTimestamp: request.timeoutTimestamp,
            fee: get.fee
        });
    }
```
