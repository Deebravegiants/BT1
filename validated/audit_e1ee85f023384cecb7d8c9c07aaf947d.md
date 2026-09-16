This confirms the analog: line 209 shows `_fillCrossChain` dispatches `RedeemEscrow` with `order.inputs` — tokens **chosen by the order creator, not the solver** — and `body.beneficiary` set to the solver (`msg.sender`). The solver has no control over which tokens are in `order.inputs`; they only see them when filling. This lets a malicious order creator weaponize `_withdraw`'s all-or-nothing loop against the solver who fronts real assets on the destination chain.

### Title
Malicious order creator can permanently block a solver's escrow redemption via a non-transferable input token, freezing solver funds - ([File: evm/src/apps/intentsv2/ExtrinsicIntents.sol], [File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw` (and the Tron `IntentGatewayV2.withdraw`) iterates over `body.tokens` and reverts the entire call if any single token transfer fails. `body.tokens` for a `RedeemEscrow` message is `order.inputs`, a field entirely controlled by the order creator at `placeOrder` time, while the recipient (`beneficiary`) of the payout is the solver who fills the order on the destination chain. A malicious order creator can include one "poison" ERC-20 as one of several `order.inputs` — for example a token whose `transfer()` always reverts, or reverts specifically when the recipient is not the original creator — so that when an honest solver fills the order (paying out real value on the destination chain) and the `RedeemEscrow` message comes back to release the escrowed inputs to the solver, `_withdraw`'s loop reverts on the poisoned token and the whole redemption fails, permanently, for every token in that order's escrow, not just the poisoned one.

### Finding Description
`_withdraw` in `evm/src/apps/intentsv2/IntentsBase.sol` (lines 451-470, mirrored by `withdraw` in `evm/tron/contracts/apps/IntentGatewayV2.sol:691-730`) loops over `body.tokens` and does: [1](#0-0) 
For non-native tokens it uses `IERC20(token).safeTransfer` (reverting variant) so a single malicious/reverting token aborts the whole loop, undoing the release of all other legitimate tokens in the same call.

`RedeemEscrow`'s `WithdrawalRequest.tokens` is always `order.inputs` — set once by the order creator in `placeOrder` — while `WithdrawalRequest.beneficiary` is the solver: [2](#0-1) 
The solver has no ability to inspect or reject individual input tokens before committing capital; they only choose whether to fill the order based on the advertised inputs/outputs. Once they fill (transferring real output assets to `order.output.beneficiary` on the destination chain, see `_fillCrossChain`), the only way to receive their compensation is via this `RedeemEscrow` → `_withdraw` path, which the order creator can permanently sabotage with one poisoned input token.

The `onAccept` dispatch path that reaches `_withdraw` is: [3](#0-2) 

### Impact Explanation
This is a permanent freezing-of-funds / theft vulnerability reachable via a single `placeOrder` transaction from any unprivileged user (an intent creator). The solver, an unrelated third party who has no control over `order.inputs`, fronts real value on the destination chain and can never redeem the escrowed compensation on the source chain — the entire escrow (including any legitimate tokens bundled with the poison token) becomes permanently stuck, since every retry of `RedeemEscrow` hits the same reverting transfer. This matches the reachable-path requirement (single dispatched request/order) and the "concrete theft or permanent freezing of funds" bar in the intents escrow/bids domain explicitly listed as in-scope.

### Likelihood Explanation
Likelihood is high: creating an ERC-20 that reverts unconditionally (or reverts only for specific recipients, e.g. a blacklist-style token, or one that reverts once a fixed supply/allowance condition is hit) is trivial and requires no special privilege. The attacker only needs to get a solver to fill an order containing the poisoned token as one of several `order.inputs` — an economically attractive order (favorable outputs) is enough bait. No governance, admin, or race condition is required.

### Recommendation
Do not let a single failing token transfer abort settlement of the whole escrow. Options:
- Use a low-level, non-reverting `token.call(...)` per token (as already done for the fee-token transfer in `withdraw`/`_withdraw`'s tx-fee section and in `IntentGatewayV2.withdraw`'s per-token loop) and, on failure, credit the amount to a per-beneficiary/per-token pull-payment balance instead of reverting the whole batch, so other tokens still settle.
- Alternatively, validate/whitelist acceptable input tokens at `placeOrder` time (e.g., require they conform to a minimal ERC-20 transfer behavior, or restrict `order.inputs` to a curated token list) so a solver cannot be tricked into filling an order backed by an unredeemable token.
- At minimum, isolate each token transfer in its own try/catch so a failure on one token does not prevent release of the others.

### Proof of Concept
1. Attacker deploys `EvilToken`, an ERC-20 whose `transfer()` unconditionally `revert()`s (or reverts whenever `to != attacker`).
2. Attacker calls `placeOrder` with `order.inputs = [ {token: EvilToken, amount: X}, {token: USDC, amount: Y} ]` and attractive `order.output` assets, escrowing both tokens under the order's commitment.
3. An honest solver observes the order, calls `fillOrder` → `_fillCrossChain`, transferring the required output assets to `order.output.beneficiary` on the destination chain, and the contract dispatches `RedeemEscrow` back to source with `tokens = order.inputs`, `beneficiary = solver`.
4. On the source chain, `onAccept` → `_withdraw(body, false, true)` iterates `body.tokens`; when it reaches `EvilToken`, `IERC20(token).safeTransfer(beneficiary, amount)` reverts, reverting the entire `_withdraw` call.
5. The solver can never redeem the `USDC` portion either (the whole call reverts every retry), permanently losing the destination-chain assets they already paid out while the attacker's escrowed input tokens remain locked in the contract.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L207-212)
```text
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );
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
