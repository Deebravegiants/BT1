Based on my analysis, I found a valid analog in the Tron variant of the IntentGateway contract.

### Title
`IntentGatewayV2.withdraw` on Tron reverts on zero-amount escrow entries, permanently freezing cross-chain escrow settlement - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The GoodEntry report describes a code path where a downstream external call (`collect`) is fed parameters (`amount0Min`/`amount1Min` == 0/0) that are legitimate in the caller's own accounting but trigger an unconditional revert in the callee, freezing user funds until the code is patched. The Tron port of Hyperbridge's Intent Gateway (`evm/tron/contracts/apps/IntentGatewayV2.sol`) has the analogous defect: its `withdraw()` function, reachable from `onAccept` for `RedeemEscrow`/`RefundEscrow` cross-chain settlement messages, lacks the zero-amount skip guard that the parallel EVM implementation (`IntentsBase._withdraw`) explicitly added, causing legitimate zero-value `WithdrawalRequest` entries to revert the whole settlement delivery.

### Finding Description
On the canonical EVM Intent Gateway, `_fillSameChain` in `IntrinsicIntents.sol` builds `escrowedInputs[i]` only inside the branch that executes when `remaining > 0 && solverAmount > 0`; when an output leg is already fully filled or the solver quotes zero for it, the loop `continue`s and `escrowedInputs[i]` stays at its default value — `TokenInfo{token: bytes32(0), amount: 0}`: [1](#0-0) 

This zero-valued `TokenInfo` is included in the `WithdrawalRequest.tokens` array that either gets settled locally or dispatched cross-chain as a `RedeemEscrow`/`RefundEscrow` message body.

The main EVM `_withdraw` in `IntentsBase.sol` explicitly guards against this: it skips any token entry whose `amount == 0` before touching escrow accounting or making an external transfer: [2](#0-1) 

The Tron implementation's `withdraw()` — the equivalent handler invoked from `onAccept` for `RedeemEscrow`/`RefundEscrow` — has no such guard. It unconditionally checks `_orders[body.commitment][token] == 0` for every entry, including the zero-value placeholder whose `token` decodes to `address(0)` (native token): [3](#0-2) 

If the order's escrowed inputs never include the native token (i.e., all inputs are ERC-20, which is the common case), `_orders[commitment][address(0)]` is 0, and the placeholder zero entry causes `revert UnknownOrder()`. Since `_filled[body.commitment] = beneficiary` is set before the loop runs (line 693) but the transaction reverts before any state change is persisted, the entire `onAccept` call reverts — this is precisely the GoodEntry shape: a value that is well-formed to the caller (0) triggers an unconditional revert deeper in the call, and there is no bypass. Unlike the GoodEntry case (where borrowing everything to zero `aBal` offered an escape hatch), this path has no equivalent workaround, because the zero-entry is a structural artifact of the cross-chain message itself (`WithdrawalRequest.tokens` mirrors `order.inputs`/`escrowedInputs` 1:1 by index) and cannot be altered by the relayer or beneficiary once dispatched.

### Impact Explanation
Cross-chain settlement (`RedeemEscrow`/`RefundEscrow`) messages delivered through Hyperbridge's `onAccept` are supposed to be one-shot and final: a relayer submits a proof, the host calls `onAccept`, and escrow is released. If `withdraw()` reverts due to a zero-amount entry, the message delivery fails. Because the underlying ISMP request has already been committed/consumed on the source side of the flow (the order was marked filled or cancellation was already emitted on the triggering chain), there is no clean retry path that changes the array contents — the same `WithdrawalRequest` will be resubmitted and revert identically. This permanently freezes the escrowed input tokens for that order on the Tron gateway, a direct "permanent freezing of funds" impact matching the required severity bar.

### Likelihood Explanation
Likelihood is moderate-to-high in practice: the triggering condition is simply an order whose native-token (address `0x0`) is not among its escrowed inputs (the common case, since escrow is almost always ERC-20) combined with any output leg that a solver declines to fill or that is already fully filled in a prior partial fill — both are normal, permissionless, non-adversarial usage patterns of the Intent Gateway's partial-fill and cross-chain redemption features, not an attacker-crafted edge case. This mirrors the GoodEntry root cause exactly: a routine small/zero-liquidity state, not a contrived exploit.

### Recommendation
Add the same zero-amount skip in the Tron `withdraw()` that `IntentsBase._withdraw` already applies on the main EVM contracts: `if (amount == 0) continue;` before the `_orders[...] == 0` check and before performing any transfer, so a placeholder/zero entry in `WithdrawalRequest.tokens` cannot revert delivery of an otherwise valid settlement message.

### Proof of Concept
1. Place a same-chain (or cross-chain equivalent) order on the Tron gateway with two output legs, using only ERC-20 tokens as escrowed inputs (no native-token input).
2. Have the solver fill the order but supply `solverAmount = 0` for one output leg (a legitimate partial-fill quote, as exercised in `_fillSameChain`'s `remaining == 0 || solverAmount == 0` branch) — see the same pattern already tested in [4](#0-3) .
3. This produces `escrowedInputs[i] = TokenInfo({token: bytes32(0), amount: 0})` for that leg, which becomes part of the `WithdrawalRequest.tokens` array dispatched/settled.
4. When `withdraw()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` processes this array, it checks `_orders[body.commitment][address(0)] == 0` — true, since no native token was escrowed — and reverts with `UnknownOrder()`, aborting the entire escrow release/refund for all tokens in the order, not just the zero leg. [3](#0-2)

### Citations

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L73-119)
```text
            uint256 alreadyFilled = _partialFills[commitment][outputToken];
            uint256 remaining = totalRequired - alreadyFilled;
            if (remaining == 0 || solverAmount == 0) {
                if (solverAmount == 0 && remaining > 0) isFullyFilled = false;
                continue;
            }
            uint256 fillAmount;

            uint256 beneficiaryShare = 0;
            uint256 protocolShare = 0;
            if (alreadyFilled == 0 && solverAmount > totalRequired) {
                fillAmount = totalRequired;
                (protocolShare, beneficiaryShare) =
                    _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);
            } else {
                fillAmount = solverAmount > remaining ? remaining : solverAmount;
            }

            uint256 amountFilled = alreadyFilled + fillAmount;
            _partialFills[commitment][outputToken] = amountFilled;
            uint256 beneficiaryTotal = fillAmount + beneficiaryShare;

            if (token == address(0)) {
                if (msgValue < beneficiaryTotal + protocolShare) revert InsufficientNativeToken();
                msgValue -= (beneficiaryTotal + protocolShare);
                // Inline, not `_sendValue`: this loop is at the via-ir stack limit.
                (bool sent,) = beneficiary.call{value: beneficiaryTotal}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, beneficiaryTotal);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }

            if (totalRequired > amountFilled) isFullyFilled = false;
            if (protocolShare > 0) emit DustCollected(token, protocolShare);

            uint256 escrowedAmount;
            if (amountFilled == totalRequired) {
                escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
            } else {
                escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
            }
            escrowedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: escrowedAmount});
            outputFills[i] = TokenInfo({token: outputToken, amount: fillAmount});
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

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L251-262)
```text
        // ── 2. Arm the malicious beneficiary ─────────────────────────────────
        //
        // The reentrant FillOptions passes amount=0 so the re-entered loop's
        // `remaining == 0 || solverAmount == 0` branch is taken — but this
        // code path is never reached because _filled[commitment] is already set.

        TokenInfo[] memory reentrantOutputs = new TokenInfo[](1);
        reentrantOutputs[0] = TokenInfo({token: bytes32(0), amount: 0});

        maliciousBeneficiary.arm(
            order, FillOptions({relayerFee: 0, nativeDispatchFee: 0, validUntil: 0, outputs: reentrantOutputs})
        );
```
