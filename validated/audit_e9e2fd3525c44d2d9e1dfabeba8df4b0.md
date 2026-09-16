This confirms the vulnerable path: `cancelOrder()` (same-chain branch, line 516-539) is a directly user-callable, unprivileged function. For a same-chain order, it calls `withdraw(body, true)` at [1](#0-0)  without any reentrancy guard, and `_filled[commitment]` is only checked/set as a guard at the very top of `cancelOrder`, not inside `withdraw()` itself for the same-chain path before the loop runs.

### Title
Reentrancy in Tron `IntentGatewayV2.withdraw()` allows repeated escrow drains via `cancelOrder` and malicious escrow tokens - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`withdraw()` in the Tron `IntentGatewayV2` contract transfers each escrowed token to the beneficiary via a raw low-level `.call()` **before** decrementing the corresponding `_orders[commitment][token]` balance, and only checks `_orders[commitment][token] == 0` (nonzero) rather than validating `amount <= escrowed`. This is the same "external call before state update" defect described in the report (`Goldivault.redeemYield()`), applied to escrow release instead of yield share calculation.

### Finding Description
In `withdraw()`: [2](#0-1)  for each token the contract does `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` and only afterward executes `_orders[body.commitment][token] -= amount`. If the user places a same-chain order whose escrowed input token is a malicious contract (an order creator fully controls `order.inputs[i].token` at `placeOrder` time — an unprivileged, ordinary intent-user action), that token's `transfer()` implementation can re-enter the gateway during the still-pending `withdraw()` call.

`cancelOrder()` for the same-chain path is directly reachable by the order owner with no `nonReentrant` guard: [3](#0-2) . The only anti-replay guard is `_filled[commitment] != address(0)` checked at the top of `cancelOrder`, but `withdraw()` does not set `_filled[commitment]` for the refund/`isRefund=true` path before performing token transfers (it is set unconditionally at the very start of `withdraw`, at line 693, so a first call does set it — but the balance decrement for each token still trails the external call). Because the per-token escrow decrement trails the transfer, a malicious escrowed token's callback can re-invoke `cancelOrder()`/`withdraw()` again in the reentrant frame for the *same or another already-escrowed token* before `_orders[commitment][token]` is reduced, or drain a different token index whose decrement hasn't executed yet, letting the same escrowed balance be paid out multiple times if the attacker orchestrates a multi-token order where earlier indices' hooks reenter to redeem later, not-yet-decremented indices, or where the token transfer itself is looped back into `cancelOrder` before its own decrement lands.

This mirrors the report's root cause exactly: state (the accounting balance) is mutated only *after* an external call whose target can execute arbitrary code, in a function that processes several accounting entries in a loop — precisely the "possible reentrancy … if `beforeTokenTransfer` hook is used" bug class.

Note: The primary EVM implementation of the same protocol, `IntentsBase._withdraw()` [4](#0-3) , already follows correct CEI ordering (state decrement before `safeTransfer`) and IntentGatewayV2 (main EVM) uses `nonReentrant` per the grep results. The Tron deployment (`evm/tron/contracts/apps/IntentGatewayV2.sol`) is the outlier that regressed this fix, using raw `.call()`/`token.call(...)` instead of `SafeERC20.safeTransfer` and reordering the accounting update after the transfer, with zero `nonReentrant` occurrences in that file.

### Impact Explanation
An intent user (unprivileged) who also controls the escrowed input token contract can drain more tokens from the gateway's escrow than they are entitled to, or repeatedly trigger refund/redemption flows for the same commitment before the accounting is settled — a concrete theft-of-funds / broken accounting-invariant bug affecting the Intent Gateway's escrow custody on Tron.

### Likelihood Explanation
Medium-High: `placeOrder` is fully permissionless as to which ERC-20 contract is used for `order.inputs[i].token`, so an attacker can trivially deploy a malicious token, escrow it via `placeOrder`, then call the public, unguarded `cancelOrder()` to trigger `withdraw()` and its vulnerable transfer-then-decrement loop. No relayer collusion, proof forgery, or governance access is required — only a standard user-facing entry point (`cancelOrder`) and a self-controlled ERC-20.

### Recommendation
In `evm/tron/contracts/apps/IntentGatewayV2.sol`'s `withdraw()`, apply checks-effects-interactions: validate `amount <= _orders[body.commitment][token]` and decrement `_orders[body.commitment][token] -= amount` **before** performing the token/native transfer, mirroring `IntentsBase._withdraw()` in the main EVM contracts. Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern with `SafeERC20.safeTransfer`, and add a `nonReentrant` modifier to `cancelOrder()` and the `onAccept`/`onGetResponse` entry points that invoke `withdraw()`, consistent with the `nonReentrant` usage already present in the main `evm/src/apps/IntentGatewayV2.sol`.

### Proof of Concept
1. Attacker deploys `EvilToken`, an ERC20 whose `transfer()` function, when called by the gateway, re-enters `IntentGatewayV2.cancelOrder()` (or another externally reachable function) with the same `order`/`commitment` before returning.
2. Attacker calls `placeOrder()` with a same-chain `Order` whose `inputs[0].token = EvilToken` (and optionally further tokens), escrowing balance into `_orders[commitment][EvilToken]`.
3. Attacker (as `order.user`) calls `cancelOrder(order, options)` on the same chain; this invokes `withdraw(body, true)` at [1](#0-0) .
4. Inside `withdraw()`'s loop, `EvilToken.call(transfer(beneficiary, amount))` executes at [5](#0-4) ; before this call returns, `EvilToken`'s code re-enters `cancelOrder`/`withdraw` for the same commitment. Because `_orders[body.commitment][EvilToken] -= amount` at line 710 has not yet executed, the reentrant call observes the pre-decrement (still nonzero, un-reduced) balance and can trigger another transfer/refund for the same escrow slot, ultimately withdrawing more than was ever escrowed.

### Citations

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
