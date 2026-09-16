### Title
Tron `IntentGatewayV2.withdraw()` silently finalizes escrow on failed (non-reverting) ERC20 transfers, permanently freezing user/solver funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2` does not use OpenZeppelin's `SafeERC20.safeTransfer` for settling escrowed order tokens. Instead, `withdraw()` performs a raw low-level `.call` and only checks that the *call itself* did not revert (`success`), never decoding/verifying the returned boolean from tokens that follow the non-reverting "return false on failure" pattern. If the underlying token silently fails the transfer, `withdraw()` still marks the order as finalized (`_filled[commitment] = beneficiary`), decrements the internal escrow accounting, and emits `EscrowReleased`/`EscrowRefunded` — even though the tokens never left the contract. Because the commitment is now permanently marked filled/refunded, there is no retry or pull-based recovery path, so the escrowed tokens become permanently stuck in the contract, unreachable by the user or solver.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `withdraw()` is called from `onAccept()` (for `RedeemEscrow`/`RefundEscrow` cross-chain settlement) and from `onGetResponse()` (for source-chain cancellation refunds): [1](#0-0) 

Specifically, the token transfer is done as:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();

_orders[body.commitment][token] -= amount;
```
and the fee transfer:
```solidity
(bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
if (!success) revert TransferFailed();
delete _orders[body.commitment][TRANSACTION_FEES];
```

The `success` boolean returned by `.call()` only indicates whether the low-level call reverted; it does **not** validate the token's own boolean return value encoded in the returndata. Many ERC20-compatible tokens (including some deployed on TRON/TVM-compatible networks) return `false` on a failed transfer instead of reverting. In this contract, such a `false` return goes completely unchecked, so `success` is `true` and execution proceeds as if the transfer succeeded.

Contrast this with the canonical EVM implementation of the same logic (`evm/src/apps/intentsv2/IntentsBase.sol`), which uses `SafeERC20.safeTransfer`, correctly reverting if the token returns `false`: [2](#0-1) 

Once `withdraw()` in the Tron contract proceeds past the unchecked transfer, it unconditionally finalizes state:
- `_orders[commitment][token]` is decremented (or deleted for fees), removing any record that the funds are still owed.
- `_filled[commitment]` is set to the beneficiary, permanently marking the order as settled and preventing any future `RedeemEscrow`/`RefundEscrow` message, `onGetResponse` cancellation-refund, or replay from ever touching this commitment again (`_orders[body.commitment][token] == 0` check in `withdraw()` would revert `UnknownOrder` on retry since the accounting was already zeroed).
- `EscrowReleased`/`EscrowRefunded` is emitted, telling all off-chain trackers the funds were paid out.

The actual ERC20 balance never leaves the gateway contract, and there is no pull-based recovery mechanism (unlike the mainline EVM path's `SafeERC20`-guarded settlement) for the user/solver to reclaim the still-escrowed tokens. This mirrors the referenced Moloch bug class: token transfer failure during a finalize/settlement step is not gated, financial state advances irreversibly, and funds become permanently unrecoverable through normal contract flows.

### Impact Explanation
This is reachable from a single relayed cross-chain settlement message (`onAccept` with `RedeemEscrow`/`RefundEscrow`) or a relayed GET-response cancellation proof (`onGetResponse`) — both externally triggerable delivery paths that any relayer can submit once the underlying ISMP message/proof exists. If the escrowed input token (chosen by the user when placing the order) is one that returns `false` instead of reverting on failure (e.g., due to a blacklist, pause, insufficient allowance/edge case in a non-standard token implementation), the solver or the user permanently loses access to their escrowed funds: the commitment is marked filled/refunded and the escrow accounting is zeroed, with no way to resubmit or retry, and no admin/pull-based path exists to sweep the stuck balance back to the rightful owner. This is a permanent freezing/loss-of-funds condition affecting arbitrary users and solvers using non-standard ERC20 tokens on the Tron deployment.

### Likelihood Explanation
Likelihood depends on encountering a non-reverting ("return false on failure") ERC20 token as an order's escrowed input/fee token, which is plausible on TRON/TVM ecosystems where several widely used tokens (and generally any token not strictly following OpenZeppelin's revert-on-failure semantics) exhibit this behavior. Any user placing an order with such a token, combined with a transient transfer failure condition (blacklist, pause, insufficient balance/allowance edge case triggered mid-flow), triggers the bug deterministically once settlement/cancellation is processed.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` (and the `SweepDust` handling in `onAccept()`) with OpenZeppelin's `SafeERC20.safeTransfer`, exactly as done in the canonical EVM `IntentsBase.sol` implementation. This ensures a token returning `false` (rather than reverting) causes the whole settlement transaction to revert, so `_filled`/`_orders` state is never finalized against an un-executed transfer, and the incoming message remains retryable/replayable rather than silently freezing the escrow.

### Proof of Concept
1. User places a cross-chain order on the Tron gateway using a non-reverting ERC20 token `T` as the escrowed input (`_orders[commitment][T] = amount`).
2. A solver fills the order on the destination chain; the source-chain settlement path eventually invokes `IntentGatewayV2.onAccept()` with `RequestKind.RedeemEscrow`, calling `withdraw(body, false)`.
3. Token `T` is configured/behaves such that `transfer(solver, amount)` returns `false` (e.g., recipient blacklisted) instead of reverting.
4. In `withdraw()`, `token.call(...)` returns `(true, abi.encode(false))` — `success` is `true`, so the `revert TransferFailed()` check is skipped.
5. `_orders[body.commitment][token] -= amount` succeeds, `_filled[body.commitment] = solver` is set, and `EscrowReleased` is emitted — but the gateway's `T` balance is unchanged and the solver never received the tokens.
6. Any retry of the same commitment now reverts with `UnknownOrder` because escrow accounting was already zeroed, and `_filled` is already set — the tokens are permanently stuck in the gateway contract with no recovery path.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-730)
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

        if (isRefund) {
            emit EscrowRefunded({commitment: body.commitment});
        } else {
            emit EscrowReleased({commitment: body.commitment});
        }
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-470)
```text
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
