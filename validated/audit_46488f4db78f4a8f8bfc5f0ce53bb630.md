## Finding

### Title
Unchecked ERC-20 return value in Tron `IntentGatewayV2.withdraw`/`SweepDust` allows silent transfer failures that permanently freeze escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of the Intent Gateway settles escrow releases and dust sweeps using a raw low-level `.call()` to the ERC-20 `transfer` function and only checks that the *call itself* did not revert, never decoding/validating the returned boolean. This is the exact "no revert on failure, returns `false`" weird-ERC20 pattern from the referenced report, and it lets escrow accounting be finalized (and the order marked filled/refunded) even though tokens never left the contract.

### Finding Description
`withdraw()` in the Tron gateway releases escrowed input tokens (and fee tokens) to a beneficiary via: [1](#0-0) 

```solidity
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}

_orders[body.commitment][token] -= amount;
```

The same unchecked pattern appears again for `SweepDust`: [2](#0-1) 

Here `success` only indicates that the low-level `call` did not revert — it says nothing about the ABI-decoded return value. Per the ERC-20 "no revert on failure" weird-token class (e.g. `ZRX`, `BAT`, `EURS`, older `BNB`), `transfer()` can execute and return `false` on failure without reverting the call. Under that condition:
- `success` is `true` (the call target executed and returned data, whether `true` or `false`, with no revert),
- the code proceeds as if the transfer succeeded,
- `_filled[body.commitment]` is set and `_orders[body.commitment][token] -= amount` is applied,
- but the beneficiary never actually receives the tokens.

This directly contrasts with the shared base used by the canonical EVM gateway, `IntentsBase._withdraw` and `_sweepDust`, which correctly use OpenZeppelin's `SafeERC20.safeTransfer` (which decodes and enforces the boolean return value or absence thereof): [3](#0-2) [4](#0-3) 

The Tron implementation reimplements this logic independently (rather than inheriting `IntentsBase`) and dropped the safe-transfer guarantee for the two outbound paths (`withdraw`, `onAccept`'s `SweepDust` branch), even though `placeOrder`'s inbound legs correctly use `safeTransferFrom`: [5](#0-4) 

### Impact Explanation
`withdraw()` is invoked from `onAccept()` whenever a relayed ISMP `RedeemEscrow` or `RefundEscrow` message arrives — reachable by any relayer submitting a proof for a legitimately dispatched settlement message, with no privileged role required. If a user or solver places (or is dealt) an order whose input token silently returns `false` on `transfer` under some condition (e.g., a paused/blacklist/edge-case state that a griefer can trigger, or simply a token which is known to return false without reverting for certain balances/recipients), the escrow's internal accounting (`_orders`) is decremented and the order is irreversibly marked as `_filled`/finalized while the actual tokens remain stuck in the `IntentGatewayV2` contract. Because `_filled` is now set and `_orders` is already zeroed, there is no remaining code path to retry or recover the transfer — this is a permanent freezing of the escrowed funds for the affected beneficiary (either the solver who was owed the input tokens on a fill, or the user who was owed a refund on cancellation).

### Likelihood Explanation
This requires only that a "no revert on failure" ERC-20 be usable as an input/escrow token in the Intent Gateway (a class of tokens explicitly called out as a known weird-ERC20 risk, and nothing in `placeOrder`/`_validateParams` restricts input tokens to a safe allowlist). Any unprivileged user constructing an order with such a token, or any actor able to induce a transient `false`-return condition in an otherwise normal token, can trigger the silent failure once settlement/refund is delivered through the normal, permissionless relayer flow.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` and the `SweepDust` branch of `onAccept()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` with OpenZeppelin's `SafeERC20.safeTransfer`, mirroring the safe implementation already used in `evm/src/apps/intentsv2/IntentsBase.sol`'s `_withdraw`/`_sweepDust`. This ensures the returned boolean (when present) is decoded and enforced, reverting the whole message-processing transaction on genuine transfer failure instead of silently finalizing broken escrow state.

### Proof of Concept
1. Governance/user registers or a user places an order on the Tron `IntentGatewayV2` whose input token is a "no revert on failure" ERC-20 (returns `false` instead of reverting under some failure condition, e.g. an allowance/blacklist edge case).
2. The order is filled (or expires and is cancelled), and the cross-chain settlement message (`RedeemEscrow`/`RefundEscrow`) is relayed and delivered to `onAccept()`, invoking `withdraw()`.
3. Inside `withdraw()`, the low-level `token.call(...)` to `transfer(beneficiary, amount)` executes without reverting but returns `false` (per the token's documented weird behavior).
4. `success` is `true`, so the code does not revert; `_orders[body.commitment][token] -= amount` executes and `_filled[body.commitment]` is set.
5. The beneficiary receives no tokens, and because the order is now finalized/zeroed, the escrowed tokens are permanently stuck in the `IntentGatewayV2` contract with no code path to reclaim them.

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-722)
```text
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

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-469)
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L639-656)
```text
    function _sweepDust(SweepDust memory req) internal {
        uint256 outputsLen = req.outputs.length;
        for (uint256 i; i < outputsLen;) {
            TokenInfo memory info = req.outputs[i];
            address token = address(uint160(uint256(info.token)));
            uint256 amount = info.amount;

            if (token == address(0)) {
                _sendValue(req.beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(req.beneficiary, amount);
            }
            unchecked {
                ++i;
            }
            emit DustSwept(token, amount, req.beneficiary);
        }
    }
```
