This confirms the vulnerability. The `withdraw()`, `SweepDust`, and fee-redemption paths in `evm/tron/contracts/apps/IntentGatewayV2.sol` use raw low-level `.call()` to invoke `IERC20.transfer`, checking only that the call itself succeeded (`success`) but never decoding/verifying the ABI-encoded boolean return value. This exactly matches the reported bug class even though `SafeERC20` is imported and used elsewhere in the same file (e.g., `placeOrder`'s `safeTransferFrom`), making the inconsistency deliberate-looking but exploitable.

### Title
Escrow withdrawal, dust sweep, and fee redemption in Tron IntentGatewayV2 use unchecked low-level ERC20 `transfer` calls, allowing silent-fail tokens to permanently freeze escrowed funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`withdraw()`, the `SweepDust` handler, and the transaction-fee redemption branch in `evm/tron/contracts/apps/IntentGatewayV2.sol` move ERC20 tokens with `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only check the outer call's `success` boolean, never decoding the ERC20 return value.

### Finding Description
The Tron variant of `IntentGatewayV2` imports and uses `SafeERC20` for the deposit-side flows (`placeOrder` uses `safeTransferFrom`), but the payout-side flows bypass `SafeERC20` entirely:

- `withdraw()`, which is invoked from `onAccept()` for `RedeemEscrow`/`RefundEscrow` requests delivered via relayed Hyperbridge proofs, transfers escrowed input tokens and fee tokens with: [1](#0-0) 
- The `SweepDust` branch of `onAccept()` does the same for protocol dust sweeps: [2](#0-1) 

In each case, the accounting update (`_orders[body.commitment][token] -= amount;` or `delete _orders[body.commitment][TRANSACTION_FEES];`) happens unconditionally right after the `.call()`, regardless of whether the token's `transfer` actually moved funds. Any ERC20 implementation that returns `false` on failure instead of reverting (a long-documented non-standard-but-common pattern, e.g. some deflationary/rebasing/paused tokens) will make `success == true` (the low-level call itself doesn't revert) while the transfer silently fails. The escrow ledger is decremented as if the beneficiary was paid, but the beneficiary receives nothing.

### Impact Explanation
Because the escrow debit happens regardless of the actual transfer outcome, a token that returns `false` on failed transfer causes the corresponding `_orders[commitment][token]` balance to be zeroed/decremented without the solver, user, or protocol treasury actually receiving funds. This is a permanent loss/freezing of escrowed funds for whichever token exhibits this behavior, reachable by any relayer delivering a normal `RedeemEscrow`/`RefundEscrow`/`SweepDust` message through the standard Hyperbridge settlement path — no privileged or malicious actor required, only a token whose `transfer` can return `false` (e.g., paused, blacklisted, or otherwise-failing ERC20 causing the call to return `false` for a specific beneficiary while other reverts occur normally for other calls).

### Likelihood Explanation
Likelihood is Medium: the code path is on the standard, unprivileged settlement flow (`onAccept` → `withdraw`/`SweepDust`), triggered by every cross-chain order fill/cancel and dust sweep. The trigger condition depends on the specific ERC20 token listed as an input/fee/dust token returning `false` rather than reverting under some failure condition (paused, blacklist, insufficient balance in a non-standard implementation) — a known but not universal class of token behavior. Given IntentGatewayV2 is designed to be usable with arbitrary tokens supplied in orders (as evidenced by explicit fee-on-transfer token test coverage in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol`), such tokens are within the expected token universe.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()`, the `SweepDust` handler, and the fee redemption branch with `SafeERC20.safeTransfer`, which is already imported (`using SafeERC20 for IERC20;`) and used elsewhere in this same contract for the deposit side. This ensures both call-level reverts and ERC20 boolean-false failures cause the transaction (and therefore the escrow accounting update) to revert atomically.

### Proof of Concept
1. A user places a cross-chain order escrowing `TokenX` (an ERC20 that returns `false` instead of reverting when, e.g., the recipient is on an internal denylist or the contract is paused) as an input.
2. The order is filled on the destination chain; the source chain's `onAccept()` receives the relayed `RedeemEscrow` message and calls `withdraw()`.
3. Inside `withdraw()`, `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` executes `TokenX.transfer(beneficiary, amount)`, which returns `false` (denylist/paused condition) without reverting.
4. `success` is `true` (the low-level call succeeded), so the `if (!success) revert TransferFailed();` guard does not trigger.
5. `_orders[body.commitment][token] -= amount;` executes, marking the escrow as fully paid out, while `beneficiary` never received `TokenX`. The solver's/user's `TokenX` is permanently lost with no remaining accounting record to recover it.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
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
