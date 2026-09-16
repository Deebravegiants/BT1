## Finding: Stale-height non-membership proof allows double payment of relayer fees for GET requests (already-answered GET timed out again)

### Title
Use of stale/already-verified state heights to force a `GetRequestTimeout` dispatch after the response was already delivered, causing the request's fee to be paid out twice - (`File: evm/src/core/HandlerV2.sol`, `evm/src/core/EvmHost.sol`)

### Summary
`HandlerV2.handleGetRequestTimeouts` accepts *any* previously-verified state-machine height for its non-membership proof, and `EvmHost` never invalidates a GET request's fee metadata once its response has been delivered locally. Combined with the fact that `EvmHost` stores state commitments for every height ever submitted (never pruned except by fisherman veto), a relayer can time out a GET request using an old, still-valid non-membership proof from *before* the response existed on Hyperbridge — even though the response was already delivered and its fee already paid — resulting in the host paying the same fee twice out of its own token reserves.

### Finding Description
For GET requests, `EvmHost.dispatchIncoming(GetResponse)` records a local response receipt and immediately pays the relayer the request's fee, but it does **not** delete the `_requestCommitments[commitment]` entry: [1](#0-0) 

Separately, `HandlerV2.handleGetRequestTimeouts` validates a GET timeout purely via a **non-membership proof against a historical, already-verified state height** on Hyperbridge (proving no response receipt existed *at that height*), then calls `dispatchTimeOut`, which refunds the fee to the original payer: [2](#0-1) [3](#0-2) 

Crucially, `handleGetRequestTimeouts` never checks `host.responseReceipts(commitment)` — the local receipt that `dispatchIncoming(GetResponse)` already set on the very same host — before allowing the timeout to proceed. The equivalent Substrate/pallet-ismp handler explicitly performs this local check before permitting a timeout: [4](#0-3) 

Because `EvmHost` keeps every historically verified `_stateCommitments[stateMachineId][height]` entry indefinitely (only removable via fisherman veto), a relayer can supply a proof anchored to an **older height H1** (from before the GetResponse was actually delivered) whose `state.timestamp` already exceeds the request's `timeoutTimestamp`, satisfying `request.timeout() > state.timestamp` == false in the loop check: [5](#0-4) 

Since the non-membership proof against H1 legitimately shows "no response receipt yet" (because the response only landed at a later height H2 on Hyperbridge), the proof verifies successfully even though the request was already answered and paid for on the source chain.

### Impact Explanation
`dispatchTimeOut(GetRequestTimeout, ...)` unconditionally refunds `meta.fee` to `meta.sender` from the host's ERC20 fee-token balance: [3](#0-2) 

Since the same commitment's `FeeMetadata` was never cleared by the earlier `dispatchIncoming(GetResponse)` reward payout, the same fee is paid out a second time — once to the relayer who delivered the response, once to the original payer via the stale timeout. This is a direct duplication of protocol-held funds (unbacked payout), and it additionally delivers a spurious `onGetTimeout` callback to an application that already received a valid `onGetResponse`, which can corrupt downstream application accounting (e.g., double refunds in apps relying on the ISMP callback as source of truth). This satisfies the "concrete theft ... of funds" and "forged message delivery" criteria for a reachable, single-relayer-triggerable High-severity bug.

### Likelihood Explanation
Any permissionless relayer can trigger this: they only need to (a) let a GET request pass its timeout window, (b) note that the response was already delivered using a newer verified height, and (c) submit `handleGetRequestTimeouts` referencing an older, still-stored, already-verified height/non-membership proof whose timestamp exceeds the request timeout. No special privileges, admin/governance actions, or off-chain mocked components are required — this is purely a message-handler/state-commitment design gap reachable from a normal relayer transaction.

### Recommendation
Add a local `host.responseReceipts(commitment).relayer != address(0)` check (mirroring the Substrate `response_receipt` check in `timeout.rs`) in `HandlerV2.handleGetRequestTimeouts` before calling `dispatchTimeOut`, and/or have `EvmHost.dispatchIncoming(GetResponse)` delete `_requestCommitments[commitment]` after paying the relayer, so a subsequent timeout attempt fails the `meta.sender == address(0)` check regardless of which historical height's proof is used.

### Proof of Concept
1. User dispatches a `DispatchGet` from `EvmHost`; `_requestCommitments[commitment]` stores `{sender, fee}` [6](#0-5) .
2. Relayer A submits a valid `GetResponseMessage`; `HandlerV2.handleGetResponses` verifies membership and calls `host.dispatchIncoming(response, relayerA)`, which pays `fee` to relayer A but leaves `_requestCommitments[commitment]` intact [1](#0-0) .
3. Relayer B (can be the same actor) waits, then submits `handleGetRequestTimeouts` referencing an older Hyperbridge state height H1 (verified/stored earlier, before the response existed at H2) whose `state.timestamp` already exceeds `request.timeout()`. The non-membership proof against H1 validly shows no response receipt at that historical point.
4. `host.dispatchTimeOut(GetRequestTimeout, meta, commitment)` executes, refunding `meta.fee` a second time to `meta.sender`, and invoking `onGetTimeout` on an application that already processed `onGetResponse` for the same request.

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

**File:** evm/src/core/EvmHost.sol (L974-1001)
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
```

**File:** evm/src/core/HandlerV2.sol (L293-321)
```text
    function handleGetRequestTimeouts(IHost host, GetTimeoutMessage calldata message) external notFrozen(host) {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        // fetch the state commitment
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
        uint256 timeoutsLength = message.timeouts.length;

        for (uint256 i = 0; i < timeoutsLength; ++i) {
            GetRequest memory request = message.timeouts[i];
            // timed-out?
            if (request.timeout() > state.timestamp) revert MessageNotTimedOut();

            bytes32 commitment = request.hash();
            FeeMetadata memory meta = host.requestCommitments(commitment);
            if (meta.sender == address(0)) revert UnknownMessage();

            bytes[] memory keys = new bytes[](1);
            keys[0] = bytes.concat(RESPONSE_RECEIPTS_STORAGE_PREFIX, commitment);

            // verify state trie non-membership proofs
            PolkadotTrie.StorageValue memory entry = PolkadotTrie.VerifyProof(state.stateRoot, message.proof, keys)[0];
            if (entry.value.length != 0) revert InvalidProof();

            host.dispatchTimeOut(GetRequestTimeout(request, _msgSender()), meta, commitment);
        }
    }
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L150-154)
```rust
				// Reject the timeout if a response has already been received for this request
				let response = GetResponse { get: get.clone(), values: Default::default() };
				if host.response_receipt(&response).is_some() {
					Err(Error::GetResponseAlreadyReceived { meta: get.into() })?
				}
```
