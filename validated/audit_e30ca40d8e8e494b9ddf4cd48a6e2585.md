### Title
Unchecked ERC20 boolean return value in `IntentGatewayV2.withdraw()` allows escrow to be marked settled without tokens being delivered - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`withdraw()` and the `SweepDust` handler in the Tron variant of `IntentGatewayV2.sol` use a raw low-level `.call()` to invoke `IERC20.transfer` and only check that the *call itself* did not revert, never decoding/validating the boolean success value the ERC20 standard returns. This is the exact bug class from the referenced report (`auraPool.booster.deposit` return value ignored): a call that "succeeds" at the EVM level but signals logical failure via its return data is treated as a successful transfer.

### Finding Description
In `withdraw()`, escrowed tokens (from `RedeemEscrow`/`RefundEscrow` requests processed via `onAccept`) are released using: [1](#0-0) 
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
...
_orders[body.commitment][token] -= amount;
```
The same pattern recurs for the transaction-fee payout and in the `SweepDust` branch of `onAccept`: [2](#0-1) [3](#0-2) 

`success` here only reflects whether the low-level `call` reverted; it does not decode the returned bytes as the ERC20 `bool` result. A token that returns `false` on failure instead of reverting (a common non-standard-but-legal ERC20 implementation pattern, and exactly the class of behavior flagged in the source report for `auraPool.booster.deposit`) will make `success == true` even though no tokens moved. The function then unconditionally decrements the internal escrow accounting (`_orders[body.commitment][token] -= amount`) and marks the order `_filled[body.commitment] = beneficiary`, permanently finalizing the withdrawal despite the beneficiary receiving nothing.

By contrast, elsewhere in the codebase (main EVM `IntentGatewayV2.sol`, `IntentsBase.sol`, `HyperFungibleToken`/`WrappedHyperFungibleToken`) all outbound ERC20 transfers use OpenZeppelin's `SafeERC20.safeTransfer`/`safeTransferFrom`, which correctly decode and enforce the boolean return value: [4](#0-3) 
Only the Tron variant substitutes the raw `.call()` pattern, presumably to accommodate non-standard Tron TRC20 tokens, but in doing so it drops the return-value check entirely rather than just tolerating empty returndata (which is what `SafeERC20` already does safely).

### Impact Explanation
This function is directly on the intents-escrow settlement path: any relayed `RedeemEscrow`/`RefundEscrow` message (or `SweepDust` admin message) reaching `onAccept` triggers `withdraw()`. If the escrowed token is one whose `transfer` implementation returns `false` on failure without reverting (e.g. due to insufficient balance from a prior fee-on-transfer mismatch, blacklist, or paused state), the escrow accounting is wiped out while the beneficiary never receives the funds — a permanent loss of the user's/solver's escrowed tokens with no recovery path, since `_orders[commitment][token]` is already zeroed and `_filled[commitment]` already set, blocking any retry.

### Likelihood Explanation
Likelihood depends on the deployed token's exact `transfer` semantics on Tron. Many TRC20/ERC20-like tokens deployed on Tron are known to deviate from strict EIP-20 semantics (this is likely the very reason the raw `.call()` pattern was introduced instead of `SafeERC20`). Given the intent-escrow flow processes arbitrary user-specified `TokenInfo.token` addresses as inputs/outputs, an attacker or unlucky combination of a non-conforming token and a transient failure condition can trigger silent fund loss without any privileged action required.

### Recommendation
Decode and validate the ERC20 return value instead of trusting call-level success alone, mirroring what `SafeERC20` does (treat empty returndata as success, but if returndata is non-empty, require it decodes to `true`):
```solidity
(bool success, bytes memory data) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success || (data.length != 0 && !abi.decode(data, (bool)))) revert TransferFailed();
```
Alternatively, switch to `SafeERC20.safeTransfer` (already imported and used via `using SafeERC20 for IERC20;` in this file) for the Tron variant as well, since `SafeERC20` already handles the "no return data" case for non-standard tokens.

### Proof of Concept
1. Deploy (or use) a token on Tron whose `transfer(address,uint256)` returns `false` on failure instead of reverting (a legal but non-strict ERC20 behavior).
2. A user places a cross-chain intent order with this token as an input, which gets escrowed in the `IntentGatewayV2` contract via `_orders[commitment][token] += amount`.
3. A relayer delivers a `RedeemEscrow` (or `RefundEscrow`) message that reaches `onAccept` → `withdraw()`.
4. At the moment of settlement, the condition that causes the token's `transfer` to return `false` is triggered (e.g., contract-level pause, blacklist toggle, or any state making the transfer logically fail without reverting).
5. `token.call(...)` returns `(true, abi.encode(false))`; the code's `if (!success) revert TransferFailed();` check passes because `success` (call-level) is `true`.
6. `_orders[body.commitment][token] -= amount;` executes, zeroing the internal escrow record, and `_filled[body.commitment] = beneficiary` is set.
7. The beneficiary never received the tokens, and no further redemption of the escrow is possible — the tokens are permanently stuck/lost from the beneficiary's perspective while the contract believes settlement succeeded.

### Citations

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L52-53)
```text
abstract contract IntentsBase is EIP712 {
    using SafeERC20 for IERC20;
```
