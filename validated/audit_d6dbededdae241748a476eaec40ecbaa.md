Confirmed: `dispatchTimeOut(PostRequestTimeout)` in `EvmHost.sol` refunds the entire relayer fee back to `meta.sender` (the payer) and pays nothing to the relayer that submits the timeout proof, even though `PostRequestTimeoutMessage` handling in `HandlerV2.handlePostRequestTimeouts()` is a permissionless, gas-costing operation. This mirrors the reported analog precisely: like the liquidator who is not rewarded when `availableBalance` is insufficient, the relayer who processes a timed-out request earns zero for the work, so profit-seeking relayers have no incentive to submit timeout proofs, leaving payer funds and app state stuck in escrow.

### Title
Timeout-processing relayers are never rewarded, so timed-out requests can remain permanently unprocessed and payer funds frozen in escrow - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatchTimeOut(PostRequestTimeout, FeeMetadata, bytes32)` always refunds the entire escrowed relayer fee to the original `payer` and pays nothing to the relayer that supplied the timeout proof, in contrast to normal delivery paths (`dispatchIncoming`) where the delivering relayer is the one compensated. Since submitting a timeout proof via the permissionless `HandlerV2.handlePostRequestTimeouts()` costs real gas, no rational relayer will do it for zero reward.

### Finding Description
`EvmHost.dispatch(DispatchPost)` escrows `post.fee` and records `_requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee})` [1](#0-0) . When the request times out, anyone can call `HandlerV2.handlePostRequestTimeouts()`, which verifies a non-membership proof and calls `host.dispatchTimeOut(PostRequestTimeout(request, _msgSender()), meta, requestCommitment)` [2](#0-1) .

Inside `dispatchTimeOut(PostRequestTimeout, ...)`, if the `onPostRequestTimeout` callback succeeds, the entire fee is transferred to `meta.sender` (the payer) — never to the relayer (`timeout.relayer`, i.e. `_msgSender()` from the handler) who actually supplied the timeout proof and paid the gas: [3](#0-2) 

This is structurally asymmetric with the normal, non-timeout delivery flow, where the relayer who performs the on-chain work is the one compensated (e.g. `dispatchIncoming(GetResponse, relayer)` pays `fee` directly to `relayer`): [4](#0-3) 

The same design is documented and intentional-looking but has the same economic flaw as the audited liquidation bug: work that must be permissionlessly performed to keep protocol state correct (unlocking escrowed funds / notifying the source app) carries zero reward for the executor: [5](#0-4) 

### Impact Explanation
When a POST request times out, the relayer fee that was meant to compensate delivery work is fully refunded to the payer, leaving nothing for whoever submits the timeout proof. Because "Relayers are profit-driven mediators" per the protocol's own documentation, and timeout processing yields strictly negative expected profit (gas cost, zero reward), the permissionless relayer network has no incentive to ever call `handlePostRequestTimeouts()`. If the payer (a smart contract or a user without direct chain access/proof-generation tooling) cannot self-relay the timeout proof, the timed-out request commitment remains stuck in `_requestCommitments`, the app-level `onPostRequestTimeout` cleanup never fires, and any escrowed fee/funds tied to that request's resolution are frozen indefinitely — a permanent freezing-of-funds condition analogous to unliquidated unhealthy positions in the original report.

### Likelihood Explanation
Any application that relies on the permissionless relayer network (rather than self-relaying) for timeout handling is exposed. Timeouts are a routine, expected occurrence (e.g. destination congestion, chain outages, or intentional timeout-based designs), so this is not an edge case — every POST request with a non-zero fee that reaches its timeout window depends on someone submitting the timeout proof for no reward.

### Recommendation
Split the escrowed fee between the relayer that submits the valid timeout proof and the payer (or pay the full fee to the timeout-submitting relayer, since they performed the equivalent proof-verification/gas work as a normal delivery), mirroring how `dispatchIncoming` rewards the delivering relayer. `PostRequestTimeout` already carries `timeout.relayer` (`_msgSender()` from `handlePostRequestTimeouts`), so the reward path can reuse this recorded submitter.

### Proof of Concept
1. Application `App` calls `IDispatcher(host).dispatch(post)` with `post.fee = F`, `post.payer = App`; `F` is escrowed into `EvmHost` via `IERC20(feeToken()).safeTransferFrom(...)` [6](#0-5) .
2. Request goes unhandled past `timeoutTimestamp` (e.g. destination congestion).
3. Any relayer `R` could call `HandlerV2.handlePostRequestTimeouts(host, message)`, paying gas to build and submit the non-membership proof [2](#0-1) .
4. `EvmHost.dispatchTimeOut(PostRequestTimeout, meta, commitment)` runs `onPostRequestTimeout` and, on success, transfers `meta.fee` entirely to `meta.sender` (`App`) — `R` receives `0` [3](#0-2) .
5. Because `R`'s expected payoff is `0 - gas_cost < 0`, no relayer submits the timeout proof; if `App` cannot self-relay, the request/commitment and any dependent escrowed state remain frozen indefinitely.

### Citations

**File:** evm/src/core/EvmHost.sol (L841-846)
```text
        // reward the relayer fee
        uint256 fee = _requestCommitments[commitment].fee;
        if (fee != 0) {
            IERC20(feeToken()).safeTransfer(relayer, fee);
        }
        emit GetRequestHandled({commitment: commitment, relayer: relayer});
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

**File:** evm/src/core/HandlerV2.sol (L254-286)
```text
    function handlePostRequestTimeouts(IHost host, PostRequestTimeoutMessage calldata message)
        external
        notFrozen(host)
    {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        // fetch the state commitment
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
        uint256 timeoutsLength = message.timeouts.length;

        for (uint256 i = 0; i < timeoutsLength; ++i) {
            PostRequest memory request = message.timeouts[i];
            // timed-out?
            if (request.timeout() > state.timestamp) revert MessageNotTimedOut();

            // known request? also serves as source check
            bytes32 requestCommitment = request.hash();
            FeeMetadata memory meta = host.requestCommitments(requestCommitment);
            if (meta.sender == address(0)) revert UnknownMessage();

            bytes[] memory keys = new bytes[](1);
            keys[0] = bytes.concat(REQUEST_RECEIPTS_STORAGE_PREFIX, requestCommitment);

            // verify state trie non-membership proofs
            PolkadotTrie.StorageValue memory entry = PolkadotTrie.VerifyProof(state.stateRoot, message.proof, keys)[0];
            if (entry.value.length != 0) revert InvalidProof();

            host.dispatchTimeOut(PostRequestTimeout(request, _msgSender()), meta, requestCommitment);
        }
    }
```

**File:** docs/content/developers/evm/api/ihost.mdx (L396-417)
```text
### dispatchTimeOut(PostRequestTimeout)

Dispatches a timed-out POST request to the source application's `onPostRequestTimeout()` callback. If the callback succeeds, refunds the relayer fee to the payer.

```solidity lineNumbers
function dispatchTimeOut(
    PostRequestTimeout memory timeout, 
    FeeMetadata memory meta, 
    bytes32 commitment
) external
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `timeout` | `PostRequestTimeout` | The timed-out POST request bundled with the relayer that submitted the timeout proof |
| `meta` | `FeeMetadata` | Fee metadata (contains payer and relayer fee) |
| `commitment` | `bytes32` | Request commitment hash |

**Access:** Restricted to handler

**Important:** Fee refund only happens if the application's timeout callback succeeds.

```
