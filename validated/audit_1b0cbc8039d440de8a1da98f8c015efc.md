## Finding

### Title
Unchecked ERC20 return value in Tron `IntentGatewayV2.withdraw()` and `SweepDust` handler can permanently strand escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` uses `SafeERC20`/`safeTransferFrom` consistently when *pulling* tokens into escrow (`placeOrder`), but when *paying out* escrowed tokens in `withdraw()` and in the `SweepDust` branch of `onAccept()`, it bypasses `SafeERC20` and instead performs a raw low-level `call` to `IERC20.transfer`, checking only that the call itself did not revert (`success`) without inspecting or requiring the returned boolean.

### Finding Description
`withdraw()` releases escrowed tokens like this: [1](#0-0) 

and the `SweepDust` request handler does the same: [2](#0-1) 

Both only check `success` from the low-level `.call`, never decoding/validating the returned boolean. This differs from `SafeERC20.safeTransfer` (used everywhere else in the contract, e.g. for `safeTransferFrom` when escrowing funds) which additionally requires that, if return data is present, it decodes to `true`.

An ERC20/TRC20 token that signals a failed transfer by returning `false` (rather than reverting) — a legitimate, still-observed pattern for some tokens — will make the low-level `call` succeed (`success == true`) while the actual token balance is never moved to the beneficiary. Because the code doesn't check the boolean, it proceeds as if the transfer succeeded: [3](#0-2) 

The escrow accounting (`_orders[body.commitment][token] -= amount`) is unconditionally decremented and `_filled[body.commitment]` is set to the beneficiary regardless of whether the tokens actually left the contract.

### Impact Explanation
Once `withdraw()` runs to completion for a commitment, the order is marked filled/refunded and the corresponding escrow balance is zeroed out — there is no other function in the contract that can re-trigger payout for that commitment. If the underlying token silently returns `false` instead of reverting on a failed transfer (e.g. blacklist enforcement, paused state, or any token with this legacy behavior), the tokens remain trapped in the `IntentGatewayV2` contract's balance with no accounting path or recovery mechanism to release them to the rightful beneficiary — a permanent freezing of user/solver funds. This reaches the "permanent freezing of funds" bar required by the validation criteria.

### Likelihood Explanation
This path is reached on every cross-chain settlement/refund/dust-sweep delivered via ISMP `onAccept`, triggered by any relayer completing message delivery — an ordinary, permissionless part of the intents flow (not requiring any privileged role). The trigger condition (a token that returns `false` instead of reverting) is dependent on the specific TRC20 token listed for intents; it is plausible for stablecoins/pausable or blacklist-capable tokens on Tron, mirroring exactly the non-standard-return-value class flagged in the source report, just manifesting as an unchecked failure rather than an unconditional revert.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` and the `SweepDust` handler with `SafeERC20.safeTransfer`, consistent with the rest of the contract (and with the non-Tron `IntentsBase.sol`/`IntentGatewayV2.sol`, which already use `safeTransfer`/`safeTransferFrom` throughout, e.g. `IntentsBase._withdraw`): [4](#0-3) 

### Proof of Concept
1. A TRC20 token is registered for use with `IntentGatewayV2` on Tron that, on transfer failure, returns `false` rather than reverting (e.g. due to a paused/blacklist check written using the older OpenZeppelin-style boolean-returning guard).
2. A user places an order escrowing this token via `placeOrder` (uses `safeTransferFrom`, succeeds normally).
3. The order is filled/cancelled and settlement is relayed, triggering `onAccept` → `withdraw()`.
4. At the moment of payout the token transfer internally fails and returns `false` (e.g., the beneficiary address became blacklisted between escrow and settlement, or transfer amount briefly exceeds an internal cap enforced without reverting).
5. `token.call(...)` returns `success == true` (the call executed without reverting) even though `false` was returned as data; the code does not check this data.
6. `_orders[body.commitment][token] -= amount` executes, `_filled[commitment]` is set, and `EscrowReleased`/`EscrowRefunded` is emitted — even though the beneficiary never received the tokens.
7. The tokens remain in the `IntentGatewayV2` contract's balance indefinitely with no function able to reference or release them again for that commitment.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-676)
```text
                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
