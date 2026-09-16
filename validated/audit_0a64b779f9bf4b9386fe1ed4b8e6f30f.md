### Title
IntentGatewayV2's low-level `token.call(IERC20.transfer.selector, ...)` does not check the ERC20 boolean return value, allowing silent transfer failures to permanently freeze escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`withdraw()` and the `SweepDust` handler in `IntentGatewayV2` release escrowed order funds and swept dust to beneficiaries using a raw `.call()` to the ERC20 `transfer` selector, checking only that the external call did not revert (`success`), never inspecting the actual boolean return value the ERC20 standard specifies. This is the same defect class as the reported `D3Callee()` issue — using plain `transfer` semantics instead of a return-value-checked `safeTransfer` — but manifested here through a manual low-level call that is even more permissive than a naked `IERC20.transfer()` call, since it swallows the returned boolean entirely.

### Finding Description
In `withdraw()`, escrowed input tokens and protocol/relayer fees are released to the beneficiary via: [1](#0-0) 

and dust is swept in the `SweepDust` branch of `onAccept()` the same way: [2](#0-1) 

Both use `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only revert if `success` (the raw call outcome) is false. For any ERC20 token whose `transfer()` implementation returns `false` on failure instead of reverting (a known legacy non-standard-compliant pattern, e.g. certain older tokens), `success` will still be `true` (the call executes and returns `abi.encode(false)`), so the code proceeds as if the transfer succeeded.

Immediately after the unchecked "successful" transfer in `withdraw()`, the escrow accounting is decremented unconditionally: [3](#0-2) 

and the order is marked filled at the top of the function: [4](#0-3) 

Because `_filled[body.commitment]` is set and `_orders[body.commitment][token]` is decremented regardless of whether the tokens actually reached the beneficiary, there is no way to retry or recover the funds: the order is considered settled, the escrow slot is zeroed, but the tokens remain stuck in the `IntentGatewayV2` contract, unreachable by the beneficiary or any recovery path.

### Impact Explanation
This causes permanent freezing/loss of user funds for any input or fee token that follows the non-reverting-`transfer`-returns-`false` pattern: the intent solver/user's escrowed principal (and any relayer/protocol fees) can be wiped out of accounting without ever being delivered, with no fallback since `_filled` and `_orders` are updated as if the transfer succeeded. This satisfies "permanent freezing of funds" for an unprivileged/reachable path (`onAccept` is triggered by a relayed ISMP message following normal fill/refund flow, and `SweepDust` similarly processes relayed instructions), matching Medium/High severity for a fund-safety bug reachable through the normal intents escrow/redeem flow.

### Likelihood Explanation
Likelihood is contingent on which ERC20 tokens are whitelisted/used as intent inputs on this deployment (Tron-side contracts). Since the token address is attacker/solver-controlled at `placeOrder()` time (any arbitrary ERC20 can be specified as `order.inputs[i].token`), a malicious or buggy token contract that returns `false` instead of reverting can be deliberately chosen to trigger this path, making exploitation straightforward once such a token is accepted by the gateway.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` and the `SweepDust` handler with OpenZeppelin's `SafeERC20.safeTransfer()`, which decodes and enforces the boolean return value (and also tolerates non-returning tokens like USDT), consistent with the `safeTransfer`/`safeTransferFrom` usage already applied elsewhere in `placeOrder()` (`evm/tron/contracts/apps/IntentGatewayV2.sol` lines 405, 459, 388).

### Proof of Concept
1. A solver/user calls `placeOrder()` specifying a non-standard ERC20 token (one whose `transfer()` returns `false` on failure rather than reverting, e.g. balance manipulated to insufficient at fill time) as an input asset; tokens are escrowed via `safeTransferFrom` (line 459/321), which succeeds.
2. On fill/refund, a relayed ISMP message triggers `onAccept()` → `withdraw()`.
3. Inside `withdraw()`, `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` is invoked; the token's `transfer()` returns `false` without reverting, so `success == true`.
4. `withdraw()` proceeds: `_filled[commitment] = beneficiary` is already set, `_orders[commitment][token] -= amount` zeroes the escrow record, and `EscrowReleased`/`EscrowRefunded` is emitted — despite the beneficiary receiving zero tokens.
5. The tokens remain locked in the `IntentGatewayV2` contract permanently; the order can never be retried because `_filled` is already set, and there is no residual escrow balance to reclaim.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L692-693)
```text
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L705-722)
```text
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
