### Title
Reentrancy in `IntentGatewayV2.withdraw` (Tron deployment) — external token transfer executed before escrow accounting is updated - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron-targeted copy of the Intent Gateway (`evm/tron/contracts/apps/IntentGatewayV2.sol`) contains an internal `withdraw()` function that releases escrowed order funds to a beneficiary using a low-level `.call` (for native value and for ERC20 `transfer`) **before** decrementing the corresponding `_orders[commitment][token]` escrow accounting. This is the exact Checks-Effects-Interactions violation described in the referenced Ajna `PositionManager` report — an unprotected external call that hands control to an attacker-controlled address prior to finalizing internal state.

### Finding Description
In the canonical EVM Intent Gateway (`evm/src/apps/intentsv2/IntentsBase.sol::_withdraw`), the escrow decrement happens before the external transfer: [1](#0-0) 

and `cancelOrder`/`fillOrder` on that contract are guarded with `nonReentrant`: [2](#0-1) 

However, the Tron variant's `withdraw()` performs the external call (native ETH/TRX `.call{value: amount}("")` or ERC-20 `token.call(...transfer...)`) to the attacker-controllable `beneficiary` **before** the `_orders[body.commitment][token] -= amount;` line executes: [3](#0-2) 

`withdraw()` is reached from `onAccept` (RedeemEscrow/RefundEscrow) and `onGetResponse`, and also directly from the same-chain path of `cancelOrder`: [4](#0-3) [5](#0-4) 

Unlike the patched EVM `IntentGatewayV2.sol`, the Tron file's `cancelOrder` is declared **without** the `nonReentrant` modifier: [6](#0-5) 

Although `_filled[body.commitment]` is set to the beneficiary at the top of `withdraw()` (before the token loop) which blocks a second `withdraw()`/`fillOrder()` call for the *same* commitment, the missing `nonReentrant` guard combined with the stale (not-yet-decremented) `_orders` mapping opens a reentrancy window across the token loop and across other state-mutating entry points that read `_orders` for a different token of the same commitment, or that are otherwise reachable while `withdraw`'s external call is in flight (e.g., a malicious beneficiary contract receiving native value can re-enter `cancelOrder`, `placeOrder`, or any other unprotected public function in the same transaction context before this call's escrow bookkeeping settles). Because `withdraw` loops over multiple `body.tokens` entries and calls out to an attacker-controlled `beneficiary` per iteration while `_orders[commitment][token]` for *later* tokens in the array is still unmodified, and because the whole function is not wrapped in `nonReentrant`, the classic pattern flagged in the source report — external call before internal accounting update, with no reentrancy guard — is reproduced here nearly verbatim.

### Impact Explanation
A malicious `beneficiary` address (attacker controls it since `beneficiary` is derived from `body.beneficiary`, which for the `RedeemEscrow`/`fillOrder` path is the solver/filler address the attacker chooses) can implement a `receive()`/fallback hook that re-enters the gateway during the native-token `.call{value: amount}("")`. Since `cancelOrder` lacks `nonReentrant` and the escrow decrement for other tokens in the same withdrawal has not yet occurred, this creates a path to double-spend/drain escrowed funds or corrupt accounting for the order — a concrete theft-of-funds vector on the Tron deployment of the Intent Gateway, which handles user-escrowed input tokens and solver settlement payouts.

### Likelihood Explanation
This is directly reachable by any solver/filler that constructs a malicious beneficiary contract and calls `fillOrder`/triggers the cross-chain settlement path so that `onAccept`/`onGetResponse` invoke `withdraw()`, or by any user calling `cancelOrder()` for a same-chain order routed to a malicious contract address as `order.user`/beneficiary. No privileged role or special network conditions are required — a single submitted order/fill/cancel transaction is sufficient to trigger the vulnerable call ordering.

### Recommendation
Apply the same Checks-Effects-Interactions fix already present in the canonical EVM contract: decrement `_orders[body.commitment][token]` **before** performing the native/ERC20 transfer in `withdraw()`, and add the `nonReentrant` modifier to `cancelOrder` (and any other externally reachable function that can trigger `withdraw()`) in `evm/tron/contracts/apps/IntentGatewayV2.sol`, mirroring `evm/src/apps/intentsv2/IntentsBase.sol` and `evm/src/apps/IntentGatewayV2.sol`.

### Proof of Concept
1. Attacker places (or arranges to be beneficiary of) a same-chain order on the Tron gateway with escrowed input tokens, including a native-value component.
2. Attacker's beneficiary contract calls `cancelOrder()` (unprotected by `nonReentrant`), which calls `withdraw()`.
3. In `withdraw()`'s token loop, the native `.call{value: amount}("")` to the attacker's contract triggers its `receive()` before `_orders[commitment][token] -= amount` executes.
4. Inside `receive()`, the attacker re-enters another state-mutating gateway function that reads the still-stale `_orders[commitment][...]` entries for other tokens in the same order, allowing a double release of escrow before the original call finishes decrementing the balance — analogous to the reentrancy path fixed by the CEI change and `nonReentrant` modifier already applied to the parallel EVM contract.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-469)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L505-505)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable nonReentrant {
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L516-539)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-634)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
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
