### Title
Unchecked ERC20 return value in `withdraw` / `SweepDust` causes silent transfer failure and permanent freezing of escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2.withdraw()` and the `SweepDust` branch of `onAccept()` in the Tron variant of `IntentGatewayV2.sol` perform raw low-level `.call` invocations of `IERC20.transfer` and only check the boolean `success` return of the *call itself*, never decoding or validating the ABI-encoded return data. This is the same silent-failure bug class described in the external report, but strictly worse: the referenced report's `_safeTransfer` at least attempted to decode the boolean; this code does not decode it at all.

### Finding Description
`withdraw()` releases escrowed order tokens to a `beneficiary` after a `RedeemEscrow`/`RefundEscrow` message is delivered via Hyperbridge, or after a GET-response timeout query confirms the order was not filled: [1](#0-0) 

The `SweepDust` handler transfers accumulated protocol dust the same way: [2](#0-1) 

And the transaction-fee redemption path likewise: [3](#0-2) 

In all three sites, the pattern is:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```
No check is made on the returned `bytes` — neither `data.length == 0` (no-return-value tokens) nor `abi.decode(data, (bool))` (explicit `false` return). For a token that returns `false` on failed transfer without reverting (a documented ERC20 pattern, and notably the behavior of Tron's own TRC20 USDT contract, which this contract is explicitly built to interact with per its `pragma`/comment "Implements the IntentGatewayV2 contract for Tron"), `success` will be `true` even though the transfer moved zero tokens. The code will then unconditionally decrement `_orders[body.commitment][token] -= amount` and emit `EscrowReleased`/`EscrowRefunded`/`DustSwept` as if funds were paid out, permanently marking the order as settled while the beneficiary receives nothing.

Notably, this same file already imports and aliases OpenZeppelin's `SafeERC20` (`using SafeERC20 for IERC20;`) and correctly uses `safeTransferFrom` for escrow deposits elsewhere in the contract: [4](#0-3) [5](#0-4) 

confirming the payout path (`withdraw`/`SweepDust`) was left using the unsafe raw-call pattern instead of `safeTransfer`.

### Impact Explanation
This is directly reachable by an unprivileged relayer simply relaying a valid `RedeemEscrow`/`RefundEscrow` message (produced by a normal cross-chain intent fill/cancel) or a GET-response timeout proof — no special privilege is required to trigger `onAccept`/`onGetResponse` beyond delivering a legitimately authenticated ISMP message, which any relayer can submit. If the escrowed/output token behaves like Tron's USDT (returns `false`/no revert on failed transfer, e.g., due to a blacklist, paused state, or insufficient balance edge case), `withdraw()` will silently "succeed": `_orders[...] -= amount` is decremented, `_filled[commitment]` is set, and events are emitted, while the beneficiary's tokens are never actually delivered. This constitutes a permanent freezing/loss of escrowed user funds — the commitment is marked settled/filled so it cannot be retried, and the tokens remain stuck in the contract with no accounting path to recover them for that beneficiary.

### Likelihood Explanation
Medium-to-High likelihood: USDT-on-Tron (TRC20) is the canonical example of a token that does not revert but can return `false`/no boolean on failure, and this exact code target is Tron. Any condition causing the destination token's `transfer` to return `false` without reverting (blacklisting, pausing, or non-standard token failure semantics) will trigger the bug on the very first delivered escrow-redemption or sweep-dust message for that token.

### Recommendation
Replace the raw `.call` + `success`-only check in `withdraw()`, the `SweepDust` branch of `onAccept()`, and the fee-redemption block with `SafeERC20.safeTransfer`, which the contract already imports and uses elsewhere:
```solidity
IERC20(token).safeTransfer(beneficiary, amount);
```
This correctly reverts on both non-reverting `false` returns and non-standard/no-return-value tokens.

### Proof of Concept
1. An order is created and escrowed with a token `T` whose `transfer` implementation returns `false` (instead of reverting) on failure (e.g., TRC20 USDT with a blacklisted/paused beneficiary or an edge-case internal failure).
2. A solver fills the order on the destination chain; the source chain `IntentGatewayV2` eventually receives a `RedeemEscrow` message via `onAccept` and calls `withdraw(body, false)` at `evm/tron/contracts/apps/IntentGatewayV2.sol:691-730`.
3. Inside `withdraw`, `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` returns `(success=true, data=abi.encode(false))` because `T.transfer` returns `false` without reverting.
4. The `if (!success) revert TransferFailed();` check passes (since `success == true`), `_orders[body.commitment][token] -= amount` executes, `_filled[body.commitment] = beneficiary` is set, and `EscrowReleased` is emitted — even though the beneficiary's token balance did not change.
5. The commitment is now permanently marked as filled with no remaining code path to redeliver the tokens; the escrowed `T` balance is stuck in the contract while accounting shows it was already paid out.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-56)
```text
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L404-406)
```text
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L705-710)
```text
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L719-722)
```text
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```
