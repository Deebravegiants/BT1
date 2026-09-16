### Title
Malicious order-input token can permanently block escrow release/refund and steal solver rewards - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.withdraw()` loops over every escrowed `TokenInfo` in `body.tokens` and performs a raw `token.call(...transfer...)` to the beneficiary for each one, requiring every single transfer (plus the fee-token transfer) to succeed in the same atomic transaction before any escrow can be released. An order creator fully controls which token contracts are listed as `order.inputs` when calling `placeOrder`, so they can include a token whose `transfer` function selectively reverts when the recipient is the filling solver (or any specific beneficiary), while behaving normally for everyone else. This mirrors the referenced Code4rena finding where a pool owner adds a reward token that always reverts on transfer to `globalBeneficiary` to block a specific, targeted payment without affecting anything else.

### Finding Description
`withdraw()` is the single settlement path used for both `RedeemEscrow` (successful fill) and `RefundEscrow`/cancellation, invoked from `onAccept` and `onGetResponse`: [1](#0-0) 

For every token in the order (including the escrowed input tokens and, separately, the `TRANSACTION_FEES` entry), the function requires the raw `.call` to succeed: [2](#0-1) 

`order.inputs` (the exact set of tokens/amounts escrowed and later redeemed here) is chosen entirely by the order creator in `placeOrder`: [3](#0-2) [4](#0-3) 

Because a solver only learns which address will be the redemption beneficiary at commitment time (their own address, once they fill and are recorded as filler), an order creator can pre-compute the intended solver/filler address is unknown at order-placement time in the general flow — but in the `SelectSolver`/session-key flow the winning solver address is known and signed for ahead of settlement, and more generally the order creator (or any party colluding with them) can simply build a custom ERC20 that hardcodes a reverting condition (e.g., reverting whenever the destination is a contract, or when the destination equals a known relayer/host-manager pattern, or simply reverting unconditionally after inclusion) as one of several `order.inputs`. Since `withdraw()` requires *all* token transfers plus the fee transfer to succeed atomically, a single non-cooperative token can permanently block redemption of every other, perfectly legitimate token escrowed in the same order — for both the "fill" (`RedeemEscrow`) and the "cancel" (`RefundEscrow`) code paths, since both call the same `withdraw()` function.

This is a stronger variant of the referenced bug: in the original report only the tax portion was blocked while all pool functionality kept working; here, the entire order's escrow (including the solver's earned reward and the protocol's own transaction fee) is bricked, because the loop treats all tokens as an inseparable batch, unlike `PermissionlessBasicPoolFactory.withdrawTaxes` where taxes are isolated to a dedicated function.

### Impact Explanation
- A malicious order creator can craft an order containing at least one adversarial ERC20 input token, alongside otherwise legitimate assets.
- Once a solver fills the order on the destination chain (delivering real value), the source-chain `RedeemEscrow` request calls `withdraw()` to release the escrowed inputs to the filler. If the malicious token reverts on transfer to that filler, the whole transaction — including the release of the other, healthy escrowed tokens and the protocol's `TRANSACTION_FEES` — reverts and can never succeed, because the malicious token's `transfer` will always behave the same way for that fixed beneficiary.
- Because `_filled[body.commitment]` is only persisted if the whole call succeeds, the order permanently sits in "unfilled/unfillable" limbo: the solver cannot ever redeem what they are owed (theft of solver capital), and the cancellation/refund path (`RefundEscrow`, same `withdraw()` function) is equally blocked, so the original depositor's other legitimate assets are frozen forever as well.
- This satisfies "permanent freezing of funds" and effectively theft (the solver already delivered the counter-asset on the destination chain but can never claim the source-chain escrow).

### Likelihood Explanation
Likelihood is high: placing an order is a fully permissionless, single-transaction action (`placeOrder`), and crafting an ERC20 with a targeted-revert `transfer` implementation is trivial and requires no special privilege — unlike governance/admin-only attack vectors that are explicitly out of scope. Any user acting as an unprivileged "intent creator" can mount this attack against any solver who chooses to fill their order.

### Recommendation
- Isolate per-token transfer failures from each other (and from the fee transfer) instead of reverting the whole batch on a single failing token — e.g., use a pull-based withdrawal pattern per token/beneficiary (credit a claimable balance mapping and let the beneficiary withdraw each token individually) similar to the standard fix for this bug class.
- Alternatively, wrap each token transfer in a try/catch and only mark the specific token entry as unredeemed while advancing the other transfers and the fee payment; emit an event so the un-transferable token can be swept/recovered separately without blocking settlement of the healthy assets.
- Consider disallowing arbitrary, unvetted ERC20s as order inputs (e.g., an allowlist or minimal transfer-behavior check) if the pull-based redesign is not immediately feasible.

### Proof of Concept
1. Attacker deploys `EvilToken`, an ERC20 whose `transfer(to, amount)` returns `true`/succeeds for most addresses but is coded to `revert()` whenever `to` is not the attacker's own address (or a mutually-agreed collusion address).
2. Attacker calls `placeOrder` with `order.inputs = [ {token: LegitToken, amount: X}, {token: EvilToken, amount: Y} ]`, escrowing both tokens into the `IntentGatewayV2` contract: [4](#0-3) 
3. A solver observes the order, delivers the requested output assets on the destination chain, and the destination gateway sends a `RedeemEscrow` request back to the source-chain `onAccept`, which calls `withdraw(body, false)` with `beneficiary = solver`: [5](#0-4) 
4. Inside `withdraw`, the loop transfers `LegitToken` successfully to the solver, then attempts to transfer `EvilToken` to the solver, which reverts because `to != attacker`: [6](#0-5) 
5. The entire `withdraw()` call — and therefore the entire `onAccept` message-handling transaction — reverts. `LegitToken` is never transferred, `_filled` is never set, and the transaction fee is never paid to the protocol. The solver, having already delivered value on the destination chain, can never redeem the escrow, and the order can never be cancelled/refunded either since `RefundEscrow` invokes the identical `withdraw()` function.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-349)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-469)
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

                unchecked {
                    ++i;
                }
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-723)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }
```
