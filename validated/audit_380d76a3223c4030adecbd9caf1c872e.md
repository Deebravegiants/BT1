### Title
`IntentGatewayV2.withdraw()` performs unguarded zero-amount ERC20 transfers, permanently freezing escrow when a fee-on-zero-transfer token is used - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`placeOrder` allows creating an order with multiple input tokens whose amounts can become `0` after protocol-fee reduction (`reducedAmount = originalAmount - protocolFee`, e.g. a dust input where `protocolFee == originalAmount`, or a `0`-amount input entry that only fails the `order.inputs.length == 0` check but not a per-token `amount > 0` check). The internal `withdraw()` function that redeems/refunds this escrow on `RedeemEscrow`/`RefundEscrow` never skips zero-amount tokens before calling `token.call(transfer(...))`, unlike the sibling implementation `IntentsBase._withdraw()` which explicitly does `if (amount == 0) continue;`.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`: [1](#0-0) 

`withdraw()` iterates `body.tokens` and unconditionally executes an ERC20 `transfer` call for every entry, including entries with `amount == 0`:

```
for (uint256 i; i < len;) {
    ...
    if (token == address(0)) { ... }
    else {
        (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
        if (!success) revert TransferFailed();
    }
    ...
}
```

Compare this to `IntentsBase._withdraw()` in the same protocol family, which explicitly guards against this: [2](#0-1) 

`placeOrder()` only rejects an empty `inputs` array, not a zero-amount individual input, and after protocol-fee reduction a small/dust input can be reduced to exactly `0`: [3](#0-2) 

The reduced-amount `TokenInfo[]` (which can contain a `0` entry) is what gets committed to `_orders` and later encoded as the `WithdrawalRequest.tokens` that flows to `withdraw()` on `RedeemEscrow`/`RefundEscrow` delivery: [4](#0-3) 

If any of the escrowed input tokens is an ERC20 implementation that reverts on a zero-value `transfer` (a known class of non-standard tokens, matching the referenced Sherlock report's root cause), the whole `withdraw()` call reverts unconditionally.

### Impact Explanation
Because the set of tokens/amounts in `WithdrawalRequest.tokens` is fixed by the original order's commitment (order fields are part of the commitment hash), every retry of the same `RedeemEscrow`/`RefundEscrow` message will hit the exact same zero-amount transfer and revert identically. This makes the incoming request for that order permanently non-deliverable through `onAccept` — the escrowed input tokens for that order (including any non-zero-amount tokens bundled in the same withdrawal call) can never be released to the beneficiary. This is a permanent freezing of user escrowed funds and a route that is unable to deliver messages, not merely wasted gas as in the original low/medium-gas report.

### Likelihood Explanation
Triggering requires only that a user (or the order-filling flow) places an order containing a token whose protocol-fee-reduced amount lands on `0`, and that token happens to be a non-standard ERC20 that reverts on zero-value transfers. `placeOrder` has no validation preventing a per-input amount of `0` or a fee-reduction that drives an amount to `0`; this is fully reachable by any unprivileged order creator without cooperation from governance or Hyperbridge operators, satisfying the "unprivileged... intent solver" reachability bar.

### Recommendation
Mirror `IntentsBase._withdraw()`'s guard in `IntentGatewayV2.withdraw()`: skip the transfer (and corresponding escrow decrement) when `amount == 0`, i.e. add `if (amount == 0) { unchecked { ++i; } continue; }` before the token transfer branch. Additionally, consider rejecting orders whose input amount (or fee-reduced amount) is zero at `placeOrder` time to avoid creating unredeemable commitments.

### Proof of Concept
1. Attacker/user calls `placeOrder` with `order.inputs` containing two tokens: a normal ERC20 `T1` with amount `100e18`, and a token `T2` (a real-world non-standard ERC20 that reverts on `transfer(to, 0)`) with a small amount such that after protocol-fee deduction `reducedAmount` for `T2` becomes `0` (e.g. `amount = 1` wei with `protocolFeeBps` rounding the fee up to `1`, or simply supplying `amount = 0` for `T2` directly since only `inputs.length == 0` is checked, not per-token amounts).
2. Order escrows both tokens; commitment is computed with the reduced (zero for `T2`) amount and stored in `_orders`.
3. On fill/cancel, the counterpart chain dispatches a `RedeemEscrow` or `RefundEscrow` request back with `WithdrawalRequest.tokens = [{T1, 100e18}, {T2, 0}]`.
4. `onAccept` → `withdraw()` loops through tokens; when it reaches `T2` with `amount == 0`, it calls `T2.call(transfer(beneficiary, 0))`, which reverts inside `T2`'s `transfer` implementation.
5. Because `token.call(...)` returns `success = false`, `withdraw()` reverts with `TransferFailed()`, so the entire `onAccept` reverts — `T1`'s legitimate `100e18` is never released, and every retry of the same message hits the identical revert, permanently freezing both escrowed amounts.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-374)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
        // Validate that order has inputs
        if (order.inputs.length == 0) revert InvalidInput();

        address hostAddr = host();
        // fill out the order preludes
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        // Calculate reduced inputs (after protocol fees) for commitment and escrow
        uint256 inputsLen = order.inputs.length;
        // Use destination-specific protocol fee, fallback to source chain fee if zero
        bytes32 destinationHash = keccak256(order.destination);
        uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
        if (protocolFeeBps == 0) {
            protocolFeeBps = _params.protocolFeeBps;
        }
        TokenInfo[] memory reducedInputs;
        bytes32 commitment;

        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                // Emit DustCollected for protocol fee if non-zero
                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L456-469)
```text
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
```
