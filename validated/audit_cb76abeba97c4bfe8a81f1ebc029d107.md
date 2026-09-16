### Title
Missing zero-amount check in `withdraw()` permanently freezes escrowed order funds on tokens that revert on zero-value transfers - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron fork of `IntentGatewayV2.sol`'s `withdraw()` function unconditionally attempts to transfer every escrowed token in a `WithdrawalRequest`, including zero-amount entries, and reverts the entire call if any single transfer fails. Unlike the canonical EVM implementation in `IntentsBase.sol`, this version is missing the `if (amount == 0) continue;` guard, so any escrowed token that reverts on zero-value transfers (a well-known ERC-20 quirk) permanently blocks settlement/refund of the whole order.

### Finding Description
`withdraw()` iterates over `body.tokens` and, for every non-native token, performs a raw low-level call to `transfer`, reverting the whole function with `TransferFailed()` on failure: [1](#0-0) 

There is no check skipping zero-amount transfers before this call, unlike the sibling implementation used by the standard EVM deployment: [2](#0-1) 

which explicitly does `if (amount == 0) continue;` before transferring.

A token amount of zero can legitimately occur in the escrow: `placeOrder()`'s fee-on-transfer handling mutates `order.inputs` to reflect the *actual* balance received by the gateway (which can be reduced to zero for pathological fee-on-transfer/deflationary tokens), and the reduced amount after `protocolFeeBps` can also become zero: [3](#0-2) 

If the escrowed amount for a given input token is (or becomes) zero, and that token is one that reverts on zero-value `transfer()` calls (a documented "weird ERC-20" behavior), then every call to `withdraw()` — whether triggered by `RedeemEscrow` (solver fill settlement) or `RefundEscrow` (cancellation) — will revert at that token's transfer, rolling back the entire withdrawal, including the release of all *other* escrowed tokens and fees for the same order.

The same unguarded pattern also exists in the `SweepDust` handler in the same file: [4](#0-3) 

### Impact Explanation
`withdraw()` is the only code path that releases escrowed order funds back to a solver (on fill) or to the user (on refund/cancel/timeout GET response via `onGetResponse`). Since the failing call is deterministic (same commitment, same token list, same zero amount every retry), there is no way to retry past it — the escrowed tokens for the entire order (not just the offending zero-amount token) become permanently frozen in the contract. This is a genuine, unprivileged-reachable permanent freezing of user/solver funds, matching the classification of the original report (Medium severity, funds-freeze with external token-behavior assumption).

### Likelihood Explanation
Reaching this requires only:
1. A user placing an order whose input includes a token exhibiting fee-on-transfer/deflationary behavior severe enough to zero out the escrowed amount, or any input token that is legitimately escrowed at amount `0`, and
2. That token also reverting on zero-value `transfer()` calls (a real-world, catalogued ERC-20 behavior).

No admin or governance misbehavior is required — this can be triggered by ordinary user order placement using an existing (not necessarily malicious) ERC-20 token, and the settlement/refund message is delivered by any unprivileged relayer via `onAccept()`.

### Recommendation
Add a zero-amount guard before each token transfer in `withdraw()` (and in the `SweepDust` handler), mirroring the fix already present in `IntentsBase.sol::_withdraw`:

```solidity
for (uint256 i; i < len;) {
    address token = address(uint160(uint256(body.tokens[i].token)));
    uint256 amount = body.tokens[i].amount;
    if (_orders[body.commitment][token] == 0) revert UnknownOrder();

    if (amount > 0) {
        if (token == address(0)) {
            (bool sent,) = beneficiary.call{value: amount}("");
            if (!sent) revert InsufficientNativeToken();
        } else {
            (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
            if (!success) revert TransferFailed();
        }
    }

    _orders[body.commitment][token] -= amount;
    unchecked { ++i; }
}
```

### Proof of Concept
1. Deploy a mock ERC-20 that reverts when `transfer(to, 0)` is called (mirrors real-world "revert-on-zero-value-transfers" tokens).
2. User calls `placeOrder()` on the Tron `IntentGatewayV2` with an input using this token, structured (via fee-on-transfer accounting or `protocolFeeBps` = 100%) so the escrowed `_orders[commitment][token]` amount recorded is `0` while `_orders[commitment][token] == 0` check at line 700 (`if (_orders[body.commitment][token] == 0) revert UnknownOrder();`) is bypassed by having at least 1 wei escrowed conceptually but transferring amount 0 in the withdrawal token list (or, more directly, use a token whose fee-on-transfer reduces the recorded input to exactly `0`).
3. Have a solver fill the order (cross-chain) or the user cancel it, triggering a `RedeemEscrow`/`RefundEscrow` message back to this chain.
4. `onAccept()` → `withdraw()` executes the token loop; the zero-value `transfer()` call to the malicious mock ERC-20 reverts, causing `TransferFailed()` and rolling back the entire withdrawal — the escrow entry remains unclaimed indefinitely, and no other combination of retries can succeed since the same zero-amount transfer is attempted every time.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L361-374)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-682)
```text
        } else if (kind == RequestKind.SweepDust) {
            SweepDust memory req = abi.decode(incoming.request.body[1:], (SweepDust));

            uint256 outputsLen = req.outputs.length;
            for (uint256 i; i < outputsLen;) {
                TokenInfo memory info = req.outputs[i];
                address token = address(uint160(uint256(info.token)));
                uint256 amount = info.amount;

                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
                unchecked {
                    ++i;
                }
                emit DustSwept(token, amount, req.beneficiary);
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L455-470)
```text
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
