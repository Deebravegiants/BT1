## Title
Malicious order input token can permanently freeze all escrowed funds in a multi-token intent order - (File: `evm/src/apps/intentsv2/IntentsBase.sol`, `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2`/`IntentsBase` allow orders to escrow an arbitrary array of ERC20 tokens with no whitelist. Both the same-chain and cross-chain withdrawal paths (`_withdraw` in `IntentsBase.sol`, `withdraw` in the Tron `IntentGatewayV2.sol`) release *all* of an order's escrowed tokens in a single loop that reverts atomically if any one token's transfer call fails. An order creator can deliberately include one blacklist-capable, pausable, or intentionally-reverting ERC20 alongside legitimate tokens; once that token's transfer to the beneficiary fails, the entire withdrawal reverts every time it is attempted (including every relayer retry of the cross-chain message), permanently locking the legitimate tokens as well as the solver's payout.

### Finding Description
`_withdraw` in `IntentsBase.sol` iterates over `body.tokens` and, for each non-zero amount, decrements escrow and performs `IERC20(token).safeTransfer(beneficiary, amount)` (or a native send) in the same loop, with no isolation between tokens: [1](#0-0) 

The equivalent Tron `withdraw` function does the same, using a raw `.call` whose `success` is checked and reverts with `TransferFailed` on any failure: [2](#0-1) 

Order inputs are never validated against a token whitelist — `placeOrder` only checks that amounts are non-zero, not that the tokens are "safe" (non-blacklisting, non-pausable, well-behaved): [3](#0-2) 

Both the redemption path (solver fills the order cross-chain, then the source chain releases escrow to the solver via `RedeemEscrow`) and the refund path (`RefundEscrow`/`_cancelSameChain`) funnel through this same all-or-nothing withdrawal loop: [4](#0-3) [5](#0-4) 

Because the solver on the destination chain already pays out `order.output.assets` to the beneficiary *before* the `RedeemEscrow` message is dispatched (`_fillCrossChain`), if the order's `order.inputs` array contains a malicious/blacklisting/reverting token, the `onAccept` call on the source chain that is supposed to release the solver's compensation will revert every time it is delivered — there is no fallback that releases the "good" tokens while skipping the bad one, and no per-token failure isolation (e.g. try/catch, or an "unclaimed" token bucket).

### Impact Explanation
An order creator (an unprivileged actor, not an admin) can mix a hostile ERC20 (self-deployed, or a real stablecoin whose transfer to the solver's address later gets blacklisted/paused) among the order's escrowed `inputs`. Once a solver fills the order — sending real value to the beneficiary on the destination chain — the `RedeemEscrow` withdrawal on the source chain will permanently revert, because it must transfer *every* input token atomically including the poisoned one. This:
- Permanently freezes the solver's rightful compensation (all escrowed input tokens, not just the bad one), even though the solver already delivered value.
- Similarly can permanently freeze the user's own refund on cancellation (`RefundEscrow`), since the same all-or-nothing loop is used.
- Cannot be worked around by relayers, since every delivery attempt of the same `onAccept` message hits the same revert — the funds are unrecoverable through the protocol's own logic.

This matches "permanent freezing of funds," qualifying as High severity per the same root cause identified in the referenced OpenQ report (an atomic loop over multiple tokens where one failing transfer blocks the whole payout).

### Likelihood Explanation
Likelihood is high: placing an order with an attacker-chosen/self-deployed ERC20 as one of several `inputs` is a normal, permissionless user action (`placeOrder`), requires no special privileges, and no token whitelist prevents it. A solver only needs to be tricked or race to fill such an order (solvers generally evaluate profitability, not token safety, and multi-input orders are a supported, expected order shape).

### Recommendation
- Isolate per-token transfer failures in `_withdraw`/`withdraw` (e.g., wrap each transfer in try/catch and credit failed transfers to a separate claimable/sweep balance) so one bad token cannot block release of the others.
- Alternatively, require a token allow-list for `order.inputs`/`order.output.assets`, or cap/limit which tokens can be escrowed, similar to deposit-token limits used elsewhere in Hyperbridge's app layer.
- Ensure `_fillCrossChain`/solver-selection flows validate that all input tokens are transferable to the solver (e.g., a `transfer(0)` no-op probe or an explicit allow-list) before the solver commits value on the destination chain.

### Proof of Concept
1. Attacker deploys `EvilToken`, an ERC20 whose `transfer` function unconditionally reverts when the recipient is not the attacker (or is blacklist-capable and gets blacklisted post-fill).
2. Attacker calls `placeOrder` with `order.inputs = [ {token: EvilToken, amount: X}, {token: USDC, amount: Y} ]`, offering an attractive `order.output` on the destination chain.
3. A solver calls `fillOrder`/`selectSolver` + `_fillCrossChain`, sending `order.output.assets` to the beneficiary on the destination chain, and dispatches `RedeemEscrow(order.inputs, solver)` back to the source chain.
4. On the source chain, `onAccept` → `_withdraw` iterates `body.tokens = [EvilToken, USDC]`; the `EvilToken.safeTransfer(solver, X)` call reverts, reverting the entire `_withdraw`, so `USDC` is never released to the solver either.
5. Every relayer retry of the same message hits the same revert. The solver's `X` EvilToken and `Y` USDC compensation is permanently stuck in escrow, despite already having paid out real value on the destination chain.

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-463)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-337)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L159-180)
```text
    function _cancelSameChain(Order calldata order, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        uint256 inputsLen = order.inputs.length;
        TokenInfo[] memory remainingTokens = new TokenInfo[](inputsLen);
        bool hasEscrow = false;
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            uint256 escrowed = _orders[commitment][token];
            if (escrowed > 0) hasEscrow = true;
            remainingTokens[i] = TokenInfo({token: order.inputs[i].token, amount: escrowed});
            unchecked {
                ++i;
            }
        }
        if (!hasEscrow) revert UnknownOrder();

        WithdrawalRequest memory body =
            WithdrawalRequest({commitment: commitment, tokens: remainingTokens, beneficiary: order.user});

        _withdraw(body, true, true);
    }
```
