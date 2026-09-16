### Title
Unchecked ERC20 `transfer` return value can permanently strand escrowed and fee funds in `IntentGatewayV2.sol` (Tron) - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2.sol` releases escrowed order funds, dust, and accumulated transaction fees to beneficiaries using a low-level `.call()` to the ERC20 `transfer` selector, but only checks that the call itself did not revert — it never decodes and validates the boolean success value that `transfer` returns. This is the exact bug class described in the referenced report: some ERC20/TRC20 tokens return `false` on a failed transfer instead of reverting, and any contract that treats "the call didn't revert" as "the transfer succeeded" will silently accept failed transfers.

### Finding Description
In `withdraw()`, `onAccept`'s `SweepDust` branch, and the transaction-fee payout inside `withdraw()`, the contract does:

```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
``` [1](#0-0) 

and identically in the `SweepDust` handling: [2](#0-1) 

`success` here only reflects whether the low-level call reverted, not the ABI-decoded boolean returned by `transfer()`. A token that returns `false` on failure (rather than reverting) — a well-known "weird ERC20" behavior, and one commonly encountered among TRC20/Tron tokens — makes `success == true` even though no tokens moved. The code then proceeds to decrement escrow accounting and finalize the order:

```solidity
_orders[body.commitment][token] -= amount;
...
_filled[body.commitment] = beneficiary;
``` [3](#0-2) 

Notably, the same file correctly uses OpenZeppelin's `SafeERC20.safeTransferFrom` when *pulling* tokens into escrow during `placeOrder()`, e.g.: [4](#0-3) 

but the outbound payout paths (`withdraw`, `SweepDust`, and the fee payout) bypass `SafeERC20` and use the unchecked raw-call pattern instead, creating an inconsistency between inbound and outbound transfer safety.

### Impact Explanation
`withdraw()` is reached via `onAccept` when a `RedeemEscrow` or `RefundEscrow` cross-chain settlement message is delivered by any relayer after being authenticated (`authenticate(incoming.request)`), i.e. it is on the standard message-delivery path any unprivileged relayer triggers: [5](#0-4) 

If the escrowed token happens to be one that returns `false` instead of reverting on transfer failure (e.g., due to a paused token, blacklist, or insufficient contract balance from rounding/dust drift elsewhere in the same contract), the contract will:
1. Mark the order as filled (`_filled[body.commitment] = beneficiary`), preventing any retry or cancellation.
2. Decrement the escrow accounting (`_orders[body.commitment][token] -= amount`), destroying the record that tokens are still owed.
3. Emit `EscrowReleased`/`EscrowRefunded`, signaling success to off-chain systems.

None of the tokens actually reach the beneficiary. The funds become permanently stuck in the contract with no accounting path to recover them — a permanent freezing/loss of user and solver funds. The same unchecked pattern in the `SweepDust` handler and the fee-release branch can similarly cause protocol fee sweeps or relayer/solver fee payouts to be recorded as delivered when they were not.

### Likelihood Explanation
Because this affects the Tron deployment of `IntentGatewayV2.sol`, and TRC20 tokens are known to include tokens with non-standard `transfer` semantics (some do not revert but return `false`, mirroring the classic USDT-style "missing/incorrect return value" ERC20 weirdness the referenced report warns about), the likelihood of an integrator listing such a token as an input/output/fee asset is realistic and grows as the set of supported tokens expands, exactly as the original report anticipated for evolving token allowlists.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only check in `withdraw()`, the `SweepDust` handler, and the fee-payout branch with `SafeERC20.safeTransfer`, which is already imported and used elsewhere in the same file (`using SafeERC20 for IERC20;`). `safeTransfer` correctly reverts both on a reverting call and on a call that returns `false` (or non-standard return data), eliminating the silent-failure path.

### Proof of Concept
1. Deploy `IntentGatewayV2.sol` (Tron variant) with an escrow token contract that implements `transfer()` to return `false` on failure instead of reverting (e.g., a token that returns `false` when the recipient is blacklisted, or simply a mock ERC20 that always returns `false`).
2. Place an order via `placeOrder()` escrowing that token; the input is pulled successfully via `safeTransferFrom`.
3. Have the order filled cross-chain and the `RedeemEscrow` message delivered to `onAccept`, invoking `withdraw()`.
4. Configure the mock token so `transfer(beneficiary, amount)` returns `false` at the moment of payout (e.g., temporarily blacklist the beneficiary or simulate insufficient allowance logic that returns `false`).
5. Observe: `(bool success,) = token.call(...)` returns `success == true` (the call itself does not revert), so `TransferFailed` is never triggered; `_orders[commitment][token]` is decremented, `_filled[commitment]` is set, and `EscrowReleased` is emitted — while the beneficiary's token balance is unchanged. The escrowed tokens are now permanently unrecoverable through the contract's normal accounting.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L454-460)
```text
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-722)
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
```
