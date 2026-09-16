### Title
Malicious solver can permanently freeze a cross-chain intent order's escrowed input tokens by filling with a receiving address the escrowed token's `transfer` will always revert for — ([File: evm/src/apps/intentsv2/ExtrinsicIntents.sol])

### Summary
`_fillCrossChain()` in `ExtrinsicIntents.sol` lets a solver pay the order's beneficiary and, in the same call, permanently mark the order `_filled` on the destination chain and dispatch a `RedeemEscrow` message naming `msg.sender` (the solver itself) as the sole beneficiary of the escrowed input tokens on the source chain. Because the escrow release is a single unconditional `safeTransfer` to that fixed beneficiary with no fallback or re-beneficiary path, a solver who fills using an address that a specific escrowed ERC-20 will always revert on (e.g., a USDC-blocklisted address, or a non-payable/reverting contract) can complete the user-facing swap while making the input-token release permanently undeliverable — and every cancellation path is also blocked because both chains gate on `_filled`.

### Finding Description
On the destination chain, `_fillCrossChain()` sets `_filled[commitment] = msg.sender` immediately, transfers output tokens to the order's beneficiary, then dispatches a `RedeemEscrow` message whose beneficiary is `bytes32(uint256(uint160(msg.sender)))` — the solver's own address, fully solver-controlled: [1](#0-0) 

On the source chain, this message is processed by `onAccept()` → `_withdraw()`, which releases every escrowed token to that fixed `beneficiary` via `safeTransfer`/`safeValue` calls with no alternate recipient or retry logic: [2](#0-1) 

If the solver's chosen address cannot receive one of the escrowed tokens (blocklisted on a centrally-administered stablecoin, or a contract that unconditionally reverts on `transfer`), `onAccept()` reverts every time it is attempted — the message can never be successfully delivered, and `_orders[commitment][token]` is never decremented.

Crucially, cancellation is also foreclosed:
- `cancelOrder()` on the destination chain reverts immediately because `_filled[commitment]` is already non-zero there (set at fill time): [3](#0-2) 
- `cancelOrder()` on the source chain (still `_filled == 0` there, since the RedeemEscrow delivery never succeeds) routes to `_cancelFromSource()`, which dispatches a Hyperbridge GET to check the destination's `_filled` slot. Since that slot is non-empty (set to the solver), `onGetResponse()` reverts with `Filled()`: [4](#0-3) 

This is the same root cause as the referenced Sablier report: a single function bundles a fund release to a party who fully controls (and can pre-select to fail) their own receiving address, and that guaranteed-revert blocks the entire settlement/cancellation flow rather than just that party's own leg — except here the blocked leg is the user's escrowed principal, and there is no split-transaction fallback anywhere in the protocol to recover it.

### Impact Explanation
The user's escrowed input tokens become permanently frozen in the source-chain `IntentGatewayV2`/`ExtrinsicIntents` contract: they cannot be released to the solver (transfer always reverts) and cannot be refunded to the user (both cancellation routes are gated on `_filled`, which is already poisoned on the destination chain). This is a direct, permanent loss of user funds triggered by a single unprivileged solver action, with no recovery path in the current code (no admin sweep, no re-targetable beneficiary, no timeout-based refund for this state).

### Likelihood Explanation
Any address can call `fillOrder()` as a solver; no special privilege is required. USDC-style blocklists are a well-known primitive, and a solver could equally deploy a trivial contract that always reverts on `transferFrom`/`transfer`. The solver pays the required output tokens to the user (so the swap appears to "complete"), making the attack low-cost and not obviously detectable before the freeze occurs, since the RedeemEscrow dispatch/finalization happens automatically after the fill.

### Recommendation
Do not let a single external transfer failure to the solver-chosen beneficiary permanently block the whole message and the whole order's escrow. Options: (1) decouple redemption from `onAccept` finalization — mark the order settled by-token and let any address later "pull" via a separate `claim()`/`redeem()` step so a failing transfer to one address doesn't block release of other tokens or state transitions; (2) wrap the transfer to the beneficiary in a try/catch and, on failure, escrow the funds to a rescue/claimable balance keyed by the intended beneficiary instead of reverting the whole `onAccept`; (3) allow a beneficiary-address update mechanism (e.g., signed re-designation) so an initially-bad address doesn't permanently lock funds.

### Proof of Concept
1. User places a cross-chain order on chain A escrowing `1000 USDC`, expecting `1000 DAI` on chain B, per `Order`/`PaymentInfo` as encoded in `placeOrder` (see `evm/src/apps/IntentGatewayV2.sol`).
2. Attacker deploys `EvilSolver`, a contract with no payable fallback and whose `onERC20Received`-independent balance is irrelevant — simplest PoC: attacker uses an address already on USDC's blocklist, or deploys a contract whose bytecode always `revert()`s regardless of calldata (so any `IERC20(usdc).transfer(evilSolver, amount)` reverts).
3. Attacker calls `fillOrder(order, options)` from `EvilSolver` on chain B, providing the required `1000 DAI` to the user's beneficiary — `_fillCrossChain()` (`evm/src/apps/intentsv2/ExtrinsicIntents.sol:164-220`) executes normally: user receives DAI, `_filled[commitment] = evilSolver` is set on chain B, and a `RedeemEscrow` message naming `evilSolver` as beneficiary is dispatched to chain A.
4. A relayer submits the proof to chain A; `onAccept()` → `_withdraw()` attempts `IERC20(usdc).safeTransfer(evilSolver, 1000e6)`, which reverts every time (`evm/src/apps/intentsv2/IntentsBase.sol:451-470`). The message can never be finalized; `1000 USDC` stays escrowed under `_orders[commitment][usdc]`.
5. User (or anyone) calls `cancelOrder(order, options)` on chain A: since chain A's `_filled[commitment]` is still `0`, it routes to `_cancelFromSource`, dispatching a GET to chain B. Chain B's `_filled[commitment]` is non-zero (`evilSolver`), so `onGetResponse` on chain A reverts with `Filled()` (`evm/src/apps/intentsv2/ExtrinsicIntents.sol:360-366`). Calling `cancelOrder` directly on chain B also reverts immediately at the top-level `_filled` check (`evm/src/apps/IntentGatewayV2.sol:505-522`).
6. Result: the `1000 USDC` escrow on chain A is permanently unredeemable and unrefundable.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-212)
```text
    function _fillCrossChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            if (solverAmount < totalRequired) revert InvalidInput();

            (uint256 protocolShare, uint256 beneficiaryShare) =
                _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);

            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
            if (protocolShare > 0) emit DustCollected(token, protocolShare);
            outputFills[i] = TokenInfo({token: outputToken, amount: totalRequired});
        }

        _execute(order, outputsLen);

        // Native dispatch fee only if the solver sent enough to cover it; else the fee token.
        uint256 nativeFee = options.nativeDispatchFee;
        if (nativeFee > msgValue) nativeFee = 0;
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );
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

**File:** evm/src/apps/IntentGatewayV2.sol (L505-522)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable nonReentrant {
        bytes32 commitment = keccak256(abi.encode(order));

        if (_filled[commitment] != address(0)) revert Filled();

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        // Emitted here, once, rather than from each of the three routes below. Every check those
        // routes make — Unauthorized, NotExpired, UnknownOrder — reverts, and a revert discards
        // logs, so an early emit can never announce a cancellation that did not happen. Emitting
        // before the branch also keeps `EscrowRefunded` the last log on the same-chain route, where
        // the refund is processed in this same transaction. Three emit sites cost bytecode this
        // contract does not have: it sits within ~100 bytes of the EIP-170 limit.
        emit OrderCancelled({commitment: commitment, canceller: msg.sender});
```
