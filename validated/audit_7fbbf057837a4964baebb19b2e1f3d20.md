## Finding: Missing zero-amount check in `IntentGatewayV2.withdraw()` diverges from canonical implementation, risking a permanently stuck escrow release on Tron

### Title
Missing non-zero-amount guard in Tron `IntentGatewayV2.withdraw()` can permanently freeze escrowed order funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The canonical EVM intents implementation explicitly skips zero-amount token entries when releasing escrow, but the Tron port of the same contract omits this guard, causing the withdrawal loop to unconditionally revert on any zero-amount entry.

### Finding Description
The canonical `_withdraw` function in `evm/src/apps/intentsv2/IntentsBase.sol` skips a token entry when its `amount` is zero, before consulting the escrow balance: [1](#0-0) 

The Tron variant's `withdraw()` (the function reached via `onAccept` for `RedeemEscrow`/`RefundEscrow` requests, and via `onGetResponse` for source-chain cancellations) does **not** have this `if (amount == 0) continue;` guard: [2](#0-1) 

Instead it goes straight to `if (_orders[body.commitment][token] == 0) revert UnknownOrder();` for every entry in `body.tokens`, which for `RedeemEscrow`/`RefundEscrow` messages is populated directly from `order.inputs` at order-placement time (see `_body(RequestKind.RefundEscrow, commitment, order.inputs, order.user)` in the canonical `ExtrinsicIntents.sol`): [3](#0-2) 

`withdraw()` in the Tron contract is invoked from three separate entry points — `onAccept` for `RedeemEscrow`/`RefundEscrow`, and `onGetResponse` for the source-cancel GET-response path: [4](#0-3) [5](#0-4) 

Because these are all single-shot dispatches from a Hyperbridge-delivered `PostRequest`/`GetResponse` — reachable by any relayer delivering the message with an unprivileged proof — a zero-amount entry anywhere in `order.inputs`/`body.tokens` deterministically reverts the *entire* `withdraw()` call, including the release of every other, non-zero, legitimately escrowed token in the same order. I was not able to fully confirm within this investigation whether `placeOrder()` on the Tron contract rejects a zero-amount `TokenInfo` entry in `order.inputs` (the EVM `IntentGatewayV2.sol`/`IntentsBase.sol` order-validation path uses `InvalidInput()` for various zero checks elsewhere, but I did not locate and read the exact `placeOrder` body for the Tron file before the tool budget ran out).

### Impact Explanation
If a zero-amount input entry can reach `order.inputs` (e.g., a user places a multi-token order where one leg has amount `0`, which several other parts of the codebase treat as a valid "placeholder"/"declined" convention — see the same convention used elsewhere for `TokenInfo.amount == 0` in `IntrinsicIntents.sol` and the SDK's phantom-bid aggregation), then every `RedeemEscrow`/`RefundEscrow` delivery for that order will revert unconditionally in `withdraw()`. Because the destination side has typically already recorded `_filled[commitment]` and/or already delivered output tokens to the beneficiary before the settlement message is dispatched, the source-chain escrow release becomes permanently unreachable via the intended flow — the legitimately escrowed non-zero-amount tokens for that order are stuck in the contract with no code path to release them. This is a permanent freezing-of-funds condition scoped to affected orders, reachable by a single order placement plus a single relayed message delivery, with no privileged role required.

### Likelihood Explanation
Likelihood depends entirely on whether the Tron `placeOrder()` (or the canonical order-construction UX that feeds it) permits a zero-amount `TokenInfo` in `order.inputs`. I could not verify this constraint within the available tool budget. If such validation exists and rejects zero-amount inputs, this divergence is unreachable and the severity would be significantly lower (a hardening/defense-in-depth gap rather than an exploitable freeze). I flag this explicitly as the key open question a follow-up review must resolve before treating this as confirmed-exploitable.

### Recommendation
Add the same `if (amount == 0) continue;` guard to `evm/tron/contracts/apps/IntentGatewayV2.sol`'s `withdraw()` function that already exists in the canonical `IntentsBase._withdraw()`, so the Tron port stays behaviorally consistent with the audited reference implementation. Additionally, confirm (or add) an explicit `InvalidInput()` revert in `placeOrder()` for any `order.inputs[i].amount == 0`, closing the root cause at order-creation time as well.

### Proof of Concept
1. Attacker/user calls `placeOrder` with `order.inputs = [TokenInfo(USDC, 1000e6), TokenInfo(DAI, 0)]` (assuming this passes validation — unconfirmed).
2. Order is filled cross-chain; solver fills output, `_fillCrossChain`/equivalent dispatches a `RedeemEscrow` POST back to source.
3. On the source (Tron) chain, `onAccept` decodes the `WithdrawalRequest` with `tokens = order.inputs` (including the zero-amount DAI entry) and calls `withdraw(body, false)`.
4. Inside the loop, for the DAI entry, `_orders[commitment][DAI] == 0` (since nothing was ever escrowed for a zero-amount input) → `revert UnknownOrder()`, unwinding the whole transaction.
5. The USDC escrow (1000e6, legitimately owed to the solver/user) is never released; no other code path exists to re-trigger settlement for this commitment, so funds are permanently stuck on the source chain.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L455-464)
```text
        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L301-307)
```text

        _filled[commitment] = address(uint160(uint256(order.user)));

        _post(
            order, _body(RequestKind.RefundEscrow, commitment, order.inputs, order.user), options.relayerFee, msg.value
        );
    }
```
