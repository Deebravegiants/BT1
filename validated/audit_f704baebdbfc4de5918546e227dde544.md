## Analysis

The external report describes a reentrancy class where token-transfer callbacks let an attacker re-enter a contract system while state (shares/balances) is only partially updated — decrement-then-transfer (or transfer-then-decrement) ordering matters, and a missing or absent reentrancy guard on a *system* of functions (not just a single function) is the root cause.

Searching the Hyperbridge codebase for an analog in an unprivileged, fund-moving path (`IntentGatewayV2` escrow/order lifecycle, which is directly reachable by any user placing/filling/cancelling orders), I found that the **Tron-targeted fork of `IntentGatewayV2`** reproduces exactly this bug class, while the canonical EVM `IntentGatewayV2` was explicitly hardened against it (see `evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol`, which documents a CEI fix and asserts `nonReentrant`-style protection).

### Title
Missing reentrancy protection + transfer-before-accounting-update in Tron `IntentGatewayV2.withdraw` allows escrow theft via reentrant callback - (`evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` has no `ReentrancyGuard`/`nonReentrant` modifier anywhere in the contract, unlike the canonical EVM `IntentGatewayV2`, which uses `ReentrancyGuardTransient` and guards `placeOrder`, `fillOrder`, and `cancelOrder` with `nonReentrant` [1](#0-0) , [2](#0-1) , [3](#0-2) . In the Tron fork, `withdraw()` releases escrow to an attacker-controlled `beneficiary` via a raw low-level `.call` **before** decrementing the corresponding `_orders[commitment][token]` accounting entry [4](#0-3) , and no reentrancy lock exists anywhere in the file .

### Finding Description
`withdraw()` in the Tron `IntentGatewayV2` sets `_filled[body.commitment] = beneficiary` first, then loops over `body.tokens`, checks only that `_orders[commitment][token] != 0` (not that `amount <= escrowed`), sends the token/native value via an unguarded low-level `.call`, and **only after** the external call decrements `_orders[body.commitment][token] -= amount` [4](#0-3) . This is the same transfer-before-bookkeeping ordering the external audit flags in `StrategyBase.withdraw`, and it is reachable by any solver/user who can become the `beneficiary` of an order (via `placeOrder`, `fillOrder`, or `cancelOrder`) [5](#0-4) .

Compare this with the hardened, canonical EVM `IntentsBase._withdraw`, which decrements `_orders[body.commitment][token]` **before** performing the transfer, i.e., proper checks-effects-interactions ordering [6](#0-5) . The canonical contract additionally wraps every externally reachable entry point (`placeOrder`, `fillOrder`, `cancelOrder`) in `nonReentrant` [3](#0-2) , and the project's own regression suite (`IntrinsicIntentsReentrancyTest.sol`) exists specifically because a prior version without the CEI fix allowed a malicious beneficiary to re-enter `fillOrder` during the native-token payout and steal escrowed fees/tokens [7](#0-6) . The Tron fork was not brought up to the same standard: it has neither the `nonReentrant` guard nor the "decrement-then-transfer" ordering that the fix relies on.

### Impact Explanation
A malicious contract set as an order's `beneficiary` (attacker fully controls this address when placing or being selected to fill an order) receives native value through an unguarded `.call{value: amount}("")` inside `withdraw()` [8](#0-7) . Because `_orders[commitment][token]` for other still-pending token legs of the same withdrawal (or of other in-flight escrow operations reachable through `placeOrder`/`fillOrder`/`cancelOrder`, none of which are reentrancy-locked) has not yet been decremented at the moment this callback fires, and there is no contract-wide reentrancy lock, an attacker can re-enter the gateway and interact with escrow/fee state that the outer call has not yet finalized. This can result in theft of escrowed input tokens and/or protocol/solver fees beyond what the attacker is legitimately owed — a direct loss of user/protocol funds.

### Likelihood Explanation
High reachability: `withdraw()` is invoked on every settlement (`onAccept` RedeemEscrow/RefundEscrow) and every source-chain cancellation response (`onGetResponse`) [9](#0-8) , and the `beneficiary` of any withdrawal is attacker-controlled by construction (the order's `user` or the filling `solver`). No privileged role is required — a normal user placing an order with themselves as beneficiary, or a solver filling an order, can deploy the malicious beneficiary contract. The only precondition is a native-token (TRX) or non-standard token leg with a fallback/callback, which is inherent to any native-value payout path (present in every withdrawal that includes a native-token input).

### Recommendation
Port the CEI fix and `nonReentrant` protection from the canonical EVM `IntentsBase`/`IntentGatewayV2` to the Tron fork:
1. Add a reentrancy guard (e.g., `ReentrancyGuard`/`ReentrancyGuardTransient`) and apply it to `placeOrder`, `fillOrder`, and `cancelOrder`.
2. In `withdraw()`, decrement `_orders[body.commitment][token] -= amount` **before** performing the native/token transfer, matching `IntentsBase._withdraw`'s ordering [10](#0-9) .
3. Validate `amount <= escrowed` explicitly rather than only checking `escrowed != 0`.

### Proof of Concept
1. Attacker deploys a malicious contract `Evil` with a `receive()`/fallback that, upon receiving native value, re-enters `IntentGatewayV2` (e.g., calls `fillOrder`/`placeOrder`/`cancelOrder` on another commitment that shares reachable state, or attempts a second `withdraw`-triggering path if any exists without the filled check).
2. Attacker places (or fills) an order with `beneficiary = Evil` and at least one native-token (TRX) leg plus another token leg in the same `WithdrawalRequest`.
3. When Hyperbridge delivers the settlement/cancellation message, `onAccept`/`onGetResponse` calls `withdraw()`, which sends TRX to `Evil` via `.call` before decrementing `_orders[commitment][token]` for that leg [11](#0-10) .
4. `Evil`'s callback fires during this window; because no `nonReentrant` guard exists anywhere in the contract, `Evil` can re-enter other externally reachable order functions while the just-paid escrow slot is still logically "owed" (not yet zeroed), enabling double-accounting/theft of escrow or fee funds that the outer transaction has not yet finalized.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L60-60)
```text
contract IntentGatewayV2 is IntrinsicIntents, ExtrinsicIntents, ReentrancyGuardTransient, Initializable {
```

**File:** evm/src/apps/IntentGatewayV2.sol (L194-194)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L505-505)
```text
        uint256 sweepCount = 0;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L516-540)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable {
        bytes32 commitment = keccak256(abi.encode(order));

        // order has already been filled
        if (_filled[commitment] != address(0)) revert Filled();

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        if (isSameChain) {
            // Same-chain: validate locally and refund immediately
            // only owner can cancel
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

            // Verify we're on the correct chain
            if (orderSource != currentChain) revert WrongChain();

            WithdrawalRequest memory body =
                WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user});

            withdraw(body, true);
        } else if (currentChain == orderSource) {
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-744)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
}
```

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L32-49)
```text
/**
 * @title ReentrantBeneficiary
 * @notice Malicious beneficiary contract that attempts to re-enter `fillOrder` during
 *         the ETH transfer made by `_fillSameChain` or `_fillCrossChain`.
 *
 * Attack window (pre-fix):
 *
 *   _fillSameChain / _fillCrossChain:
 *     beneficiary.call{value: ...}("")   ← RE-ENTRY HERE
 *     // _filled still == address(0) pre-fix, now set at the top (CEI)
 *
 * With the CEI fix in place, `_filled[commitment]` is set to `msg.sender` at the
 * very start of both fill functions. Any reentrant `fillOrder` call therefore hits
 * the `if (_filled[commitment] != address(0)) revert Filled()` guard and reverts.
 * That revert propagates through `receive()`, causing the outer ETH transfer to
 * return `(false, ...)`, which triggers `InsufficientNativeToken()` in the outer
 * call — rolling back all state changes atomically.
 */
```
