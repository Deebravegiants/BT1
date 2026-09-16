### Title
Unchecked ERC20 `transfer` return value in `IntentGatewayV2.withdraw` (Tron) allows escrow accounting to desync from actual token delivery - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed intent funds using a raw low-level `.call()` to the token's `transfer` selector and only checks that the call itself did not revert (`success`), never decoding/validating the returned boolean. This is the same bug class as the reported `_transfer`/`_safeTransfer` issue: a "fire-and-forget" transfer primitive is used on a path that must guarantee actual asset delivery, while the rest of the codebase (e.g. `evm/src/apps/intentsv2/IntentsBase.sol`) correctly uses OpenZeppelin's `SafeERC20.safeTransfer`, which reverts on a `false` return.

### Finding Description
In `withdraw()`, escrowed input tokens and transaction fees are released to the beneficiary/solver via: [1](#0-0) 

Specifically:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```
and the equivalent for fee-token release. The contract already imports and aliases `SafeERC20` (`using SafeERC20 for IERC20;`) and uses `safeTransferFrom` for inbound escrow (`placeOrder`), but the outbound `withdraw()` path bypasses `SafeERC20` and instead performs a raw `.call`, checking only that the low-level call did not revert.

Per the ERC20 standard, a compliant `transfer` may return `false` instead of reverting when a transfer cannot be completed (e.g., paused tokens, blocklisted recipients, insufficient balance edge cases in non-standard implementations). A raw `.call()` succeeds (returns `success = true`) in this scenario since no revert occurred — the function only fails to bubble up the boolean `false`. As a result:
1. `_orders[body.commitment][token] -= amount;` (escrow accounting) is decremented as if the transfer succeeded.
2. No tokens are actually delivered to the beneficiary.
3. `EscrowReleased`/`EscrowRefunded` is emitted, marking the order permanently filled/settled (`_filled[body.commitment] = beneficiary`).

This mirrors the reported vulnerability class exactly: using an "unsafe" transfer primitive (`_transfer`/raw `.call` without return-data validation) on a critical settlement path instead of a primitive that enforces success (`_safeTransfer`/`SafeERC20.safeTransfer`).

### Impact Explanation
This is on the intents-escrow settlement path reachable by any relayer delivering a `RedeemEscrow`/`RefundEscrow` ISMP message that triggers `onAccept` → `withdraw`. If the escrowed token silently returns `false` rather than reverting under any condition (e.g., temporary pause, denylist, insufficient allowance edge case, or a non-standard/rebasing token), the escrowed tokens remain permanently locked in the `IntentGatewayV2` contract while the internal accounting treats them as already paid out and the order as finalized. The rightful beneficiary (solver or user, depending on refund/release) permanently loses the escrowed funds with no path to re-claim them, since the order's `_orders` mapping has already been zeroed and `_filled` marks it complete. This is a concrete permanent freezing/loss-of-funds condition on token bridge/intents escrow settlement.

### Likelihood Explanation
Likelihood depends on interacting with a non-strictly-compliant ERC20 (or one that can return `false` under adverse conditions such as a pause or blocklist) being used as an intent input/fee token on the Tron deployment. Given IntentGatewayV2 is permissionless with respect to which ERC20 tokens users can escrow (`order.inputs[i].token` is attacker/user supplied), and Tron's own native TRC20 token ecosystem is known for non-standard token behavior, this condition is realistically reachable without any privileged actor — it only requires a relayer to deliver a legitimate settlement message for an order that escrowed such a token.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` (and the fee-token release beside it) with `IERC20(token).safeTransfer(beneficiary, amount)` (already imported via `using SafeERC20 for IERC20`), consistent with the non-Tron `IntentsBase._withdraw` implementation. If Tron-specific tokens (e.g., a USDT variant that doesn't return a boolean) require special handling, decode the return data defensively (accept both no-return-data and `true`-returning calls) rather than ignoring it outright, so a `false` return still reverts.

### Proof of Concept
1. Attacker/user deploys or uses an ERC20 token `T` on Tron whose `transfer` function returns `false` (instead of reverting) when e.g. the caller is blocklisted or the contract is paused, per the ERC20 spec's optional-boolean-return semantics.
2. User calls `placeOrder` escrowing `T` as an input token; `IntentGatewayV2` receives the tokens via `safeTransferFrom` (succeeds normally).
3. Solver fills the order on the destination chain; the source chain's `onAccept` is invoked with a `RedeemEscrow` request, calling `withdraw(body, false)`.
4. If token `T` is paused/blocklisted at settlement time (attacker/governance-controlled on `T`, or transient chain condition), `token.call(...transfer...)` returns `success = true` with encoded `false` payload; the check `if (!success) revert TransferFailed();` does not catch this.
5. `_orders[commitment][token] -= amount` executes, `_filled[commitment] = beneficiary` is set, `EscrowReleased` emitted — but the beneficiary never received token `T`. The escrowed `T` is now permanently stuck in the `IntentGatewayV2` contract with no accounting path to recover it. [2](#0-1)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-723)
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

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }
```
