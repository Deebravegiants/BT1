Confirmed: the ISMP GET-request `dispatch` (`EvmHost.sol` L974-1013) sets `request.from = abi.encodePacked(_msgSender())` — i.e., anyone can dispatch a `DispatchGet` directly against the host with `from = <attacker address>` and any `keys`/`context` they like. The response is later delivered by `EvmHost.dispatchIncoming(GetResponse, relayer)` (`EvmHost.sol` L824-833), which routes strictly by `response.request.from`, calling `onGetResponse` on whatever address the *original dispatcher* put in `from`. This means the "which contract handles this response" decision is entirely attacker-controlled at dispatch time, unlike POST requests where `to` is chosen and validated by the counterpart's registered gateway.

`ExtrinsicIntents.onGetResponse` (`evm/src/apps/intentsv2/ExtrinsicIntents.sol` L360-366) only checks `onlyHost` + `_checkRelayer` and that the queried storage value is empty, then blindly trusts `incoming.response.request.context` as a `WithdrawalRequest` and calls `_withdraw(body, true, true)`. It never verifies that the underlying `GetRequest.keys` actually correspond to `_calculateCommitmentSlotHash(body.commitment)` on the real destination gateway address (`_instance(order.destination)`), nor that the request commitment was one this contract itself dispatched via `_cancelFromSource`. This is the exact bug-class from the report: a callback trusts attacker-suppliable "userData"/context without confirming the flow was self-initiated.

### Title
Unvalidated GET-response context lets attackers forge order cancellations and drain arbitrary escrow in ExtrinsicIntents - (File: evm/src/apps/intentsv2/ExtrinsicIntents.sol)

### Summary
`ExtrinsicIntents.onGetResponse` accepts any `GetResponse` whose `request.from` field points at this contract, then decodes the attacker-controlled `request.context` as a `WithdrawalRequest` and immediately releases escrowed tokens for the encoded `commitment`/`tokens`/`beneficiary` — with no check that the queried storage key actually corresponds to that commitment's `_filled` slot on the correct destination gateway, and no check that the original GET request was dispatched by `_cancelFromSource` itself.

### Finding Description
`EvmHost.dispatch(DispatchGet)` (`evm/src/core/EvmHost.sol` L974-1013) lets any caller dispatch a GET request with an arbitrary `from` value taken from `_msgSender()`, arbitrary `keys`, and arbitrary `context`. `EvmHost.dispatchIncoming(GetResponse, relayer)` (`evm/src/core/EvmHost.sol` L824-833) later routes the verified response purely by `response.request.from`, invoking `onGetResponse` on that address with no further correlation to who actually "owns" the semantics of the query.

`ExtrinsicIntents.onGetResponse`:
```solidity
function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
    _checkRelayer(incoming.relayer);
    if (incoming.response.values[0].value.length != 0) revert Filled();

    WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
    _withdraw(body, true, true);
}
```
only validates `msg.sender == host` and (if a relayer is configured) that the relayer matches. It performs no check that:
1. `incoming.response.request.keys[0]` equals `bytes.concat(_instance(order.destination), _calculateCommitmentSlotHash(body.commitment))` for the `commitment` encoded in `body` — i.e. that the storage slot actually queried is the `_filled` mapping slot of the *legitimate* destination gateway for that order.
2. The GET request commitment corresponds to one this contract dispatched via `_cancelFromSource` in the first place.

An attacker can call `IDispatcher(host).dispatch(DispatchGet)` directly (bypassing `_cancelFromSource` entirely) with:
- `from = <this ExtrinsicIntents gateway address>` (so the response routes back here),
- `keys[0]` = some storage location known/guaranteed to be empty (e.g. a slot on any arbitrary contract/address that has never been written, trivially satisfying `values[0].value.length == 0`),
- `context` = an arbitrary ABI-encoded `WithdrawalRequest{commitment, tokens, beneficiary}` naming a real, currently-escrowed `commitment` that belongs to a legitimate, unexpired, unfilled order placed by another user, with `tokens` set to that order's escrowed amounts and `beneficiary` set to the attacker's own address.

Because `_withdraw` (`evm/src/apps/intentsv2/IntentsBase.sol` L451-485) only checks `_orders[commitment][token] != 0` (i.e., that escrow exists) and does not re-derive/authenticate the commitment against the caller's actual order ownership, this lets the attacker finalize (`_filled[commitment] = beneficiary`) and drain any legitimate user's escrowed input tokens for a manufactured "empty-storage" proof, permanently locking out the real solver/refund path (since `_filled` is now set to the attacker) and stealing the escrow.

### Impact Explanation
This is a direct, unauthenticated theft-of-funds primitive: any address can drain another user's escrowed `_orders[commitment][token]` balances for any commitment that is otherwise legitimately awaiting cancellation/refund, by fabricating a GET response context and pointing its storage-proof key at any address/slot guaranteed to be empty. It also permanently marks the order `_filled`, freezing the legitimate refund/fill path for that order. This matches "concrete theft ... of funds" and "unauthorized app action" criteria.

### Likelihood Explanation
The attack requires only: (1) a single arbitrary `dispatch(DispatchGet)` call on the public `EvmHost`/dispatcher (open to any address, paying only the relayer fee), (2) a normal relayer to submit the resulting proof through `HandlerV2.handleGetResponses` (this is the standard permissionless relaying flow — `handleGetResponses` only validates the state proof and that the request commitment is known, not who dispatched it or what `context`/`keys` were used), and (3) knowledge of any existing escrowed commitment (all `OrderPlaced`/`OrderFilled`/`OrderCancelled` events and commitments are public on-chain). No privileged role, admin, or governance action is required — this is reachable by any unprivileged relayer/attacker submitting a single dispatched GET request and its proof.

### Recommendation
`onGetResponse` must cryptographically bind the response to the originating action:
1. Re-derive the expected storage key from `body.commitment` and the *registered* `_instance(order.destination)` address, and revert unless `incoming.response.request.keys[0]` matches that derived key exactly (as `_cancelFromSource` constructs it).
2. Track a pending-cancellation record (e.g. `mapping(bytes32 requestCommitment => bool)` set when `_cancelFromSource` dispatches, keyed by the exact hash of the `GetRequest`/commitment) and require `onGetResponse` to check that the incoming `response.request` hash matches a request this contract actually dispatched, clearing the flag once consumed — analogous to the `performingFlashLoan` reentrancy-style guard recommended in the referenced report, but generalized to "this GET request was initiated by me."
3. Alternatively/additionally, verify `incoming.response.request.dest` equals the expected destination chain for the order encoded in `body`, and that the destination address embedded in `keys[0]`'s first 20 bytes equals `_instance(order.destination)`.

### Proof of Concept
1. User A places a cross-chain order on chain S with commitment `C`, escrowing `TokenA` for gateway `ExtrinsicIntents` at address `G`.
2. Attacker calls `IDispatcher(hostOnChainS).dispatch(DispatchGet)` directly with:
   - `dest` = some arbitrary/irrelevant chain,
   - `from` = `G` (this ExtrinsicIntents contract's own address, so the response routes back to it),
   - `keys[0]` = a 52-byte key pointing at a guaranteed-empty storage slot (e.g., an unused contract address + random slot),
   - `context` = `abi.encode(WithdrawalRequest({commitment: C, tokens: order.inputs, beneficiary: attacker}))`.
3. A relayer submits the storage proof (trivially valid, since the slot is genuinely empty) via `HandlerV2.handleGetResponses`.
4. `EvmHost.dispatchIncoming` verifies the (correct, but semantically irrelevant) proof and calls `G.onGetResponse(...)`.
5. `ExtrinsicIntents.onGetResponse` sees `values[0].value.length == 0`, decodes attacker's forged `context`, and calls `_withdraw(body, true, true)`, transferring User A's escrowed `TokenA` to the attacker and marking `_filled[C] = attacker`, freezing the order. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L240-270)
```text
    function _cancelFromSource(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        if (options.height <= order.deadline) revert NotExpired();

        uint256 inputsLen = order.inputs.length;
        for (uint256 i; i < inputsLen;) {
            if (_orders[commitment][address(uint160(uint256(order.inputs[i].token)))] == 0) revert UnknownOrder();

            unchecked {
                ++i;
            }
        }

        bytes memory context =
            abi.encode(WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user}));

        bytes[] memory keys = new bytes[](1);
        keys[0] = bytes.concat(abi.encodePacked(_instance(order.destination)), _calculateCommitmentSlotHash(commitment));
        DispatchGet memory request = DispatchGet({
            dest: order.destination,
            keys: keys,
            timeout: 0,
            height: options.height,
            fee: options.relayerFee,
            context: context,
            payer: msg.sender
        });

        address hostAddr = host();
        if (msg.value > 0) {
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L360-366)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
```

**File:** evm/src/core/EvmHost.sol (L824-833)
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-485)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }

        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }

            if (isRefund) {
                emit EscrowRefunded({commitment: body.commitment, tokens: body.tokens});
            } else {
                emit EscrowReleased({commitment: body.commitment, tokens: body.tokens});
            }
        }
    }
```

**File:** evm/src/core/HandlerV2.sol (L217-247)
```text
    function handleGetResponses(IHost host, GetResponseMessage calldata message) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(message.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 responsesLength = message.responses.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](responsesLength);

        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // don't check for timeouts because it's checked on Hyperbridge

            // known request? also serves as source check
            FeeMetadata memory meta = host.requestCommitments(leaf.response.request.hash());
            if (meta.sender == address(0)) revert UnknownMessage();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.response.hash());
        }

        bytes32 root = host.stateMachineCommitment(message.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, message.proof.multiproof, leaves, message.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // duplicate response?
            if (host.responseReceipts(leaf.response.request.hash()).relayer != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.response, _msgSender());
        }
    }
```
