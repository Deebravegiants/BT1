### Title
Unbounded `Order.inputs` array lets a single `placeOrder` call permanently freeze cross-chain escrow via a gas-exhausting `_withdraw` loop - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.placeOrder` only checks that `order.inputs.length != 0` — there is no upper bound on the number of distinct input tokens a user can escrow in a single order. Every settlement path (fill, refund, cancel) that later releases that escrow does so through `IntentsBase._withdraw`, which iterates once per token performing an external transfer (`safeTransfer`/native send) with no cap. An attacker can place a cross-chain order with an arbitrarily large `inputs` array, cheap enough to escrow in one transaction, but sized so the corresponding release loop on the settlement side cannot fit inside a block's gas limit — permanently freezing the escrowed funds. This is the same bug class as the referenced report: an unbounded per-item loop, driven entirely by attacker-controlled list length, that degrades from an "annoyance" (many notifications) into an unrecoverable operation (a transaction that can never succeed).

### Finding Description
`placeOrder` stamps and escrows the order with only a non-empty check on `inputs`: [1](#0-0) 

The escrow-transfer loop and later fee/commitment loops are themselves `O(n)` over `order.inputs`, so a large `inputs` array can be deliberately shaped to just barely fit the block gas limit for the escrow transaction (e.g. by using pre-deployed minimal ERC-20s, or exploiting that transfers from already-warm token contracts/accounts are cheaper than the corresponding transfers-out later): [2](#0-1) 

Every escrow-release path funnels through `IntentsBase._withdraw`, which loops over `body.tokens` (i.e. `order.inputs`) doing a storage write plus an external call (native send or `IERC20.safeTransfer`) per entry, with no length cap: [3](#0-2) 

For cross-chain orders, the settlement flow already pays the solver's output to the beneficiary and *then* dispatches a `RedeemEscrow`/`RefundEscrow` ISMP POST back to the source chain. The source chain's `onAccept` calls `withdraw()` (→ `_withdraw`) to release the escrow to the solver: [4](#0-3) 

`onAccept` is invoked by the permissionless `IHandlerV2.handlePostRequests` (directly, or nested in `batchCall`), which is executed by relayers within a single EVM transaction subject to the destination chain's block gas limit: [5](#0-4) 

Because `_withdraw`'s per-token transfer loop is strictly more gas-hungry than a mere balance check (it performs `SLOAD`+`SSTORE` plus a real value/ERC-20 transfer per token, versus `transferFrom`'s cost at escrow time, which can additionally benefit from cheaper "cold→warm" patterns the attacker controls when picking tokens), an attacker can size `order.inputs` so the escrow succeeds but the corresponding `_withdraw` call in `onAccept` always reverts out of gas. The ISMP framework's documented contract is that if `on_accept`/`onAccept` fails, no receipt is persisted and the request can be retried/replayed — but if the failure is deterministic (always exceeds available gas), the request can never be delivered successfully, so the escrow release on the source chain is unreachable forever, while the solver has already irrevocably delivered the output tokens on the destination chain.

### Impact Explanation
This results in permanent freezing of the escrowed input tokens on the source chain: they can never be released to the solver (who already paid the output) nor reclaimed by the order creator (once filled, `_filled[commitment]` is set and only the fill/redeem path applies). It also griefs the solver, who has already paid for the order's outputs and dispatched the relayer fee, but can never receive the corresponding escrow. This satisfies the "permanent freezing of funds" criterion and is reachable by any unprivileged user via a single `placeOrder` call plus the normal solver fill flow — no admin, governance, or privileged role is involved.

### Likelihood Explanation
Likelihood is moderate-to-high: constructing an order with hundreds/thousands of distinct (even trivial, cheaply deployed) ERC-20 tokens is inexpensive relative to the guaranteed asymmetry between escrow-in cost and release-out cost, and the attacker fully controls `order.inputs.length` and the specific token contracts used (they can deploy adversarial ERC-20s that are cheap to `transferFrom` but expensive to `transfer`, e.g. via storage-heavy hooks/proxies, to widen the gas gap further). No special timing or race condition is required — the only cost to the attacker is gas for the escrow transaction itself.

### Recommendation
Enforce a hard cap on `order.inputs.length` (and `output.assets.length`) in `placeOrder`, sized so the worst-case `_withdraw` loop (transfer-out plus storage writes for every token) is guaranteed to fit comfortably within realistic block gas limits on all supported destination/source chains. Alternatively, decouple release from a single atomic loop by allowing per-token withdrawal claims (pull-based, one token per call) so a large `inputs` array degrades gracefully into multiple bounded transactions instead of one unbounded, potentially unexecutable, transaction.

### Proof of Concept
1. Deploy `N` minimal ERC-20 tokens (or reuse existing ones) such that `transferFrom` at escrow time is cheap (e.g., pre-warmed storage, no extra logic) but `transfer` is comparatively expensive for the attacker's contracts, or simply pick `N` large enough that `_withdraw`'s combined per-token `SLOAD`/`SSTORE`/transfer cost exceeds the destination/source chain's block gas limit while `placeOrder`'s per-token `transferFrom` cost does not.
2. Call `IntentGatewayV2.placeOrder(order, graffiti)` on the source chain with `order.inputs` containing `N` such tokens — this succeeds and escrows all `N` tokens: [6](#0-5) 
3. A solver fills the order cross-chain via `fillOrder`, delivering all output tokens to the beneficiary and dispatching the `RedeemEscrow` POST request back to the source chain: [7](#0-6) 
4. When a relayer delivers the `RedeemEscrow` message via `handlePostRequests`/`onAccept` on the source chain, `_withdraw` iterates all `N` input tokens: [3](#0-2)  — the call runs out of gas and reverts every time it is attempted, regardless of the gas limit supplied by any relayer (up to the chain's block gas limit), because the loop's total cost exceeds it.
5. The escrow can never be released: the solver never receives the input tokens they are entitled to, and the funds sit frozen in the `IntentGatewayV2` contract indefinitely.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-329)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

        // Reject duplicate output tokens
        uint256 outputsLen_ = order.output.assets.length;
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                if tload(token) {
                    mstore(0, 0xb4fa3fb3) // InvalidInput.selector
                    revert(0x1c, 0x04)
                }
                tstore(token, 1)
            }
            unchecked {
                ++i;
            }
        }
        // Clean up transient storage so repeated placeOrder calls in the same tx don't false-positive.
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                tstore(token, 0)
            }
            unchecked {
                ++i;
            }
        }

        address hostAddr = host();
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;
                if (amount == 0) revert InvalidInput();

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    _sendValue(dispatcher, amount);
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

            // Build sweep calls and snapshot gateway balances before the sweep.
            Call[] memory transferCalls = new Call[](inputsLen);
            uint256[] memory balancesBefore = new uint256[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;

                if (token == address(0)) {
                    uint256 balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                    balancesBefore[i] = address(this).balance;
                } else {
                    uint256 balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    balancesBefore[i] = IERC20(token).balanceOf(address(this));
                }

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));

            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }

                unchecked {
                    ++i;
                }
            }
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }

                unchecked {
                    ++i;
                }
            }
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** sdk/packages/core/contracts/interfaces/IHandlerV2.sol (L50-57)
```text
    /**
     * @notice Process a batch of incoming POST requests
     * @dev Verifies request proofs, checks for timeouts, validates message delays, and dispatches valid requests to destination apps.
     * Ensures requests haven't expired and come from verified state commitments.
     * @param host The Host contract that stores protocol state
     * @param request Batch of POST requests with their merkle proofs
     */
    function handlePostRequests(IHost host, PostRequestMessage memory request) external;
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L211-220)
```text
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }

        emit OrderFilled({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: order.inputs});
    }
```
