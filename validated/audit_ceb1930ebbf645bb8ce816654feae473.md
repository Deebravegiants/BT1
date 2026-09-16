## Title
Unchecked ERC20 `transfer` return value in `IntentGatewayV2.placeOrder` predispatch sweep desyncs escrow accounting from actual token custody - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
In the Tron deployment of `IntentGatewayV2`, the predispatch branch of `placeOrder` sweeps tokens from the `CallDispatcher` back to the gateway using a raw, unchecked `IERC20.transfer` call, then unconditionally credits the order's escrow balance with the *expected* amount regardless of whether that transfer actually moved value. This is the exact bug class described in the referenced report (unchecked `transfer`/`transferFrom` return values), but here it is reachable and reachable-critical: any order creator fully controls the input token contract used in the predispatch flow, and desynced accounting lets fabricated escrow credit be created against the gateway's shared token pool.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `placeOrder`'s predispatch branch builds a sweep call using the raw selector instead of `safeTransfer`: [1](#0-0) 

```solidity
transferCalls[i] = Call({
    to: token,
    value: 0,
    data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
});
...
_orders[commitment][token] += reducedInputs[i].amount;
```

The transfer call is later executed through `CallDispatcher.dispatch`, which only checks whether the low-level `.call` itself reverted — it never decodes or validates the ABI-encoded `bool` return value of `transfer`: [2](#0-1) 

Because `_orders[commitment][token] += reducedInputs[i].amount` is executed in the same loop *before* the sweep call is dispatched, and is based purely on `reducedInputs[i].amount` (the order's declared/expected amount) rather than any post-transfer balance check, escrow accounting is credited unconditionally — independent of whether the gateway actually received the tokens.

This is a clear regression from the equivalent function in the primary EVM deployment, `evm/src/apps/IntentGatewayV2.sol`, which snapshots balances before the sweep and computes the *actually received* amount afterward before crediting/using it: [3](#0-2) 

The Tron variant lacks this balance-diffing safeguard entirely for the predispatch sweep path.

Since `order.inputs[i].token` is fully attacker-controlled (any address supplied by the order creator), an attacker can supply a malicious ERC20 contract whose `transfer` function returns `false` without reverting (a standard non-reverting-failure pattern that many real and adversarial tokens implement) as the input token. The attacker can arrange for the `CallDispatcher` to appear to hold `balance >= requiredAmount` (e.g. by having the malicious token freely mint balance to `dispatcher` inside `order.predispatch.call`, which the attacker also fully controls), satisfying the `balance < requiredAmount` check trivially at no cost. The subsequent sweep `transfer` call can then return `false` (transferring nothing, or transferring to a different destination), yet `CallDispatcher.dispatch` still reports success since the outer call did not revert.

### Impact Explanation
`_orders[commitment][token]` is incremented by the declared amount even though the gateway's real token balance for that token never increased. This escrow accounting entry is later redeemable via the gateway's normal withdrawal/refund/fill-and-redeem paths (`_withdraw`, `EscrowRefunded`, cross-chain `RedeemEscrow`), which pay out against the gateway's actual pooled token balance shared across all users' orders. An attacker can therefore mint fabricated escrow credit for a token backed by nothing, and later withdraw/redeem it, draining real tokens belonging to other legitimate users of the shared pool for that same token address — i.e., unbacked-credit theft leading to permanent loss of funds for other users of the `IntentGatewayV2` on the Tron deployment. This satisfies the "unbacked mint"/"concrete theft of funds" criteria.

### Likelihood Explanation
The attack requires only a single `placeOrder` transaction with attacker-supplied `predispatch.call`/`predispatch.assets`/`order.inputs` referencing a token contract the attacker deploys and fully controls — no privileged role, governance, or off-chain compromise is needed. This is directly reachable by any unprivileged intent submitter through the public `placeOrder` entry point, matching the required "single submitted transaction" threat model.

### Recommendation
Use `SafeERC20.safeTransfer`/`safeTransferFrom` (as already done in the non-predispatch branch and in the primary EVM `IntentGatewayV2.sol`) for the sweep call, or — matching the safer pattern already used elsewhere in this codebase — snapshot the gateway's token balance before dispatching the sweep call and after, then credit `_orders[commitment][token]` with the *actually received* delta rather than the pre-computed `reducedInputs[i].amount`. This closes the accounting gap regardless of whether the underlying token reverts, returns `false`, or applies a transfer fee.

### Proof of Concept
1. Attacker deploys `EvilToken`, an ERC20 whose `transfer(to, amount)` always returns `false` (or moves funds elsewhere) without reverting, and whose `mint`/predispatch call lets the attacker credit `balanceOf(dispatcher)` arbitrarily for free (e.g., via a custom `mint` function invoked in `order.predispatch.call`).
2. Attacker calls `placeOrder` with:
   - `order.predispatch.call` = calldata that mints `X` `EvilToken` to `dispatcher` (the shared `CallDispatcher`, `_params.dispatcher`).
   - `order.predispatch.assets` = empty/negligible, satisfying the loop at lines 393-411.
   - `order.inputs[0] = {token: EvilToken, amount: X}`.
3. In the predispatch branch (lines 416-449): `balance = IERC20(EvilToken).balanceOf(dispatcher) == X >= requiredAmount` passes; `transferCalls[0]` is built with the raw `transfer` selector; `_orders[commitment][EvilToken] += reducedInputs[0].amount` (≈X) is credited.
4. `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` executes `EvilToken.transfer(gateway, X)`, which returns `false` and moves 0 tokens — `CallDispatcher` sees `success = true` at the low-level-call layer and does not revert.
5. The IntentGateway's real `EvilToken` balance remains 0, but `_orders[commitment][EvilToken] == X`.
6. Attacker (or any actor referencing this commitment) later triggers cancellation/refund/withdrawal flows that pay out `_orders[commitment][EvilToken]` from the gateway's shared token custody — draining real `EvilToken`/other-users' balances held by the gateway, since the escrow ledger is inflated relative to actual holdings.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L427-441)
```text
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;
```

**File:** evm/src/utils/CallDispatcher.sol (L44-61)
```text
    function dispatch(bytes memory encoded) external {
        Call[] memory calls = abi.decode(encoded, (Call[]));
        uint256 callsLen = calls.length;
        for (uint256 i = 0; i < callsLen; ++i) {
            Call memory call = calls[i];
            uint32 size;
            address to = call.to;
            assembly {
                size := extcodesize(to)
            }

            if (size == 0) {
                revert NotContract(to);
            }

            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L260-306)
```text
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
```
