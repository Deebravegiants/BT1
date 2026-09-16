### Title
Checks-Effects-Interactions violation in Tron `IntentGatewayV2.withdraw()` allows escrow-accounting to be decremented after the external token transfer - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron fork of `IntentGatewayV2` reintroduces the exact bug class described in the `_paymentAH()` report: state that should be committed *before* an external interaction is instead updated *after* it. In `withdraw()`, the escrow accounting (`_orders[commitment][token]`) is decremented only after the token/native transfer has already executed, and the pre-transfer check only verifies the balance is non-zero rather than sufficient. This is the same "storage update dropped/misordered relative to the effect it is supposed to guard" pattern flagged in `LienToken._paymentAH()`.

### Finding Description
Compare the two implementations of the withdrawal/release logic:

- Main EVM contract (`IntentsBase._withdraw`) correctly applies the effect before the interaction: [1](#0-0) 

- Tron contract (`IntentGatewayV2.withdraw`) does the opposite — it calls out to the token/beneficiary first and only decrements `_orders` afterward, and the earlier check only guards against a fully-zeroed slot, not against `amount` exceeding what is actually escrowed: [2](#0-1) 

`withdraw()` is reached from `onAccept()` (processing `RedeemEscrow`/`RefundEscrow` cross-chain messages relayed through Hyperbridge) and from `onGetResponse()` (processing cancellation proofs) — both attacker/relayer-reachable paths that ultimately move real escrowed funds: [3](#0-2) [4](#0-3) 

Because the transfer (`token.call(...)` / `beneficiary.call{value: amount}("")`) happens before `_orders[body.commitment][token] -= amount`, any escrowed asset that can execute code during transfer (a token the order's own creator selects, e.g. an ERC-777-style or otherwise callback-capable token, or a beneficiary contract for native transfers) gains a window in which the escrow ledger still reflects the pre-withdrawal amount. This is the same defect class as `_paymentAH()`: an accounting mutation that is supposed to happen atomically with (and protect) the payout is instead ordered after it, so the invariant it's meant to enforce doesn't hold at the moment the funds actually move.

### Impact Explanation
If exploited via reentrancy (e.g. a malicious token with transfer hooks used as an order input, or a native-token beneficiary contract), an attacker can leverage the stale `_orders` balance during the external call window to drive additional withdrawal/refund logic against the same commitment before the ledger is corrected, risking loss of escrowed user/protocol funds beyond what was legitimately owed. This is a High-severity fund-safety defect in the escrow release path of the intents/bridge system.

### Likelihood Explanation
The path is reachable by any user who places an order using a token they control (a standard, unprivileged action), combined with a relayer delivering the resulting cross-chain message — no privileged role is required. The main EVM contract already fixes this ordering, indicating the Tron variant is a regression that was not carried over from the audited fix, increasing the likelihood this specific deployment remains vulnerable if used.

### Recommendation
Mirror the fixed pattern already used in `IntentsBase._withdraw`: decrement `_orders[body.commitment][token]` (checked against `amount`, not merely non-zero) before performing the external transfer, and prefer `SafeERC20.safeTransfer` (already imported via `using SafeERC20 for IERC20`) over raw low-level `.call` for token transfers. Apply the same effects-before-interactions ordering to the fee payout and `SweepDust` handling in the same file.

### Proof of Concept
1. Attacker deploys a callback-capable token `X` (e.g., implementing ERC-777-like hooks) and places a cross-chain order on the Tron gateway with `X` as an input, escrowing `amount` via `placeOrder` (real `safeTransferFrom` into the gateway).
2. A solver fills the order on the destination chain; Hyperbridge relays a `RedeemEscrow` message back to the Tron gateway.
3. `onAccept` → `withdraw` is invoked: at [5](#0-4) 
the contract calls `X.transfer(beneficiary, amount)` before `_orders[commitment][X] -= amount` executes.
4. During `X.transfer`'s callback, `_orders[commitment][X]` still shows the pre-withdrawal balance, letting the attacker trigger any code path that reads or acts on that stale escrow value before it is corrected, undermining the accounting invariant the ledger is meant to guarantee.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```
