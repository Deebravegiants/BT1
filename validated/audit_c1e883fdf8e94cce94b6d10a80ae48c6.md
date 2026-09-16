### Title
Escrow withdrawal in `IntentGatewayV2.sol` (Tron) treats a non-reverting failed ERC20 `transfer` as success, permanently freezing user/solver funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.sol` releases escrowed order tokens using a raw low-level `.call()` to `IERC20.transfer`, checking only that the *call itself* did not revert (`success`), never decoding/validating the ERC20's returned boolean. Tokens that signal failure by returning `false` instead of reverting (the exact bug class cited in the referenced Sherlock report) will cause `success` to be `true` even though no tokens were actually moved, while the internal escrow accounting is unconditionally decremented and the order is marked filled/refunded. This permanently strands the escrowed collateral in the contract and gives the beneficiary nothing, without any error being surfaced.

### Finding Description
`withdraw()` releases escrowed order tokens to a beneficiary reachable from any `RedeemEscrow`/`RefundEscrow` cross-chain message (fill/cancel flow) or from a `GET` response callback: [1](#0-0) 

```solidity
function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
    ...
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
        ...
    }
    ...
}
```

The `success` boolean here is the result of the low-level `call` itself — it is `true` whenever the target contract's code executes without reverting, *regardless of what the ERC20's `transfer` function actually returns*. Per EIP-20, well-behaved contracts return a `bool` indicating success, and some real-world tokens (the report's canonical example is ZRX) intentionally return `false` on failure instead of reverting. Because the returned data is discarded (`(bool success,) = ...`), such a `false` return is silently treated as a successful transfer.

The exact same pattern is repeated for fee redemption and for `SweepDust` in the same file: [2](#0-1) [3](#0-2) 

Once `success` is (incorrectly) accepted, `_orders[body.commitment][token] -= amount;` unconditionally decrements the escrow, `_filled[body.commitment] = beneficiary;` marks the order as settled, and an `EscrowReleased`/`EscrowRefunded` event fires — all while the token balance never moved. There is no subsequent state that can be used to retry or recover the stuck balance: the commitment is now considered fully settled.

By contrast, the equivalent EVM (non-Tron) implementation in `IntentsBase.sol`/`IntentGatewayV2.sol` correctly uses OpenZeppelin's `SafeERC20.safeTransfer`, which decodes and validates the return value: [4](#0-3) 

This confirms the Tron contract's raw `.call()` + selector pattern is a regression/divergence from the safe pattern used elsewhere in the same protocol, and is precisely the bug class described in the referenced report (no return-value check on ERC20 `transfer`).

### Impact Explanation
Any ERC20 registered as an order input/output token on the Tron IntentGateway that returns `false` on a failed transfer (rather than reverting) — a documented and non-exotic ERC20 behavior — causes:
- The user's or solver's escrowed collateral to be permanently locked in the `IntentGatewayV2` contract (funds are debited from internal accounting but never delivered).
- The associated order/commitment to be marked as filled/refunded, so there is no legitimate on-chain path to retry or reclaim the funds.
- This applies to the core settlement path (`withdraw`, called from `onAccept` for `RedeemEscrow`/`RefundEscrow` and from `onGetResponse`), as well as to protocol fee disbursement and `SweepDust`.

This is a permanent freezing-of-funds condition reachable via the normal cross-chain settlement flow that every user/solver interacting with the gateway depends on — satisfying the "Medium" bar for concrete, permanent loss of funds.

### Likelihood Explanation
The vulnerability triggers automatically whenever a token registered in an order behaves this way — no attacker action or malicious governance is required; it fires on the standard settlement path (`RedeemEscrow`/`RefundEscrow` message delivery or GET-response driven refund), which is reachable by any solver filling an order or any user cancelling one, using a token that the protocol has not restricted to a known-safe allowlist. Given the intent gateway is designed to support arbitrary ERC20 tokens across chains, likelihood of encountering such a token is realistic.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` (lines ~702-708, ~719-721) and in the `SweepDust` handler (lines ~670-676) with OpenZeppelin's `SafeERC20.safeTransfer`, consistent with the non-Tron `IntentGatewayV2`/`IntentsBase.sol` implementations, which already import `SafeERC20` (`using SafeERC20 for IERC20;`) but do not apply it to these transfer sites.

### Proof of Concept
1. Register a token (e.g. mimicking ZRX's `transfer` behavior: returns `false` on failure without reverting, such as when transferring to a blacklisted/paused-for address or under an internal condition) as an order's input token.
2. A user places an order escrowing this token via `placeOrder`; a solver fills it on the destination chain, triggering a `RedeemEscrow` settlement message back to the Tron chain.
3. `onAccept` → `withdraw()` executes `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))`. The token's `transfer` returns `false` but the call itself does not revert, so `success == true`.
4. `_orders[commitment][token] -= amount` succeeds, `_filled[commitment] = beneficiary` is set, `EscrowReleased` is emitted — yet `beneficiary`'s token balance is unchanged; the tokens are permanently stuck in the `IntentGatewayV2` contract with no remaining code path to recover them.

### Citations

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
