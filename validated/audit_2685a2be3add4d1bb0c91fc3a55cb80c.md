## Analysis

The reported bug class — token transfers whose success/failure is not properly validated, leading to state being finalized as if the transfer succeeded — has a direct analog in the Tron variant of the Intent Gateway contract.

### Title
Unchecked ERC20 return value in `IntentGatewayV2.withdraw()` / dust-sweep path allows escrow to be marked released without tokens actually moving - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
In the Tron build of `IntentGatewayV2`, token transfers to solvers/beneficiaries are performed with a raw low-level `.call` to the ERC20 `transfer` selector, and only the boolean `success` of the *call itself* is checked — not the ABI-decoded return value of `transfer`. Tokens that signal failure by returning `false` (rather than reverting) will make `success == true` even though no tokens moved, causing escrow state to be decremented and `EscrowReleased`/`EscrowRefunded`/`DustSwept` events to be emitted despite the transfer silently failing. This mirrors the `Fund.finalizeGrant` / `Org.cashOutOrg` bug class in the referenced report, where transfer results are trusted without verification.

### Finding Description
The Tron `IntentGatewayV2.sol`'s `withdraw()` function (invoked by `onAccept`/`onGetResponse` when settling cross-chain `RedeemEscrow`/`RefundEscrow` messages) does: [1](#0-0) 

```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
_orders[body.commitment][token] -= amount;
```

and the exact same pattern is used for fee redemption and for the `SweepDust` request handler: [2](#0-1) 

In both cases `success` only reflects whether the external call reverted, not whether the token's own `transfer` logic returned `true`. Non-compliant or legacy ERC20 tokens (e.g. tokens following the original ERC20 spec loosely, or ones that return `false` on insufficient balance instead of reverting) will cause the call to return `success = true` with `returndata` decoding to `false`. The contract has no `balanceOf` pre-check and does not decode/validate the returned boolean, so:
- `_orders[body.commitment][token] -= amount` still executes, permanently clearing escrow accounting for tokens that were never actually paid out.
- `_filled[body.commitment] = beneficiary` is already set before the transfer loop, marking the order filled/cancelled regardless of transfer outcome.
- `EscrowReleased`/`EscrowRefunded`/`DustSwept` events fire, signalling successful settlement to indexers, relayers, and downstream consumers.

This directly parallels the referenced bug: transfer completion is inferred from the low-level call success rather than the actual ERC20 return value, and no balance is checked beforehand.

By contrast, the canonical EVM Intent contracts (`evm/src/apps/intentsv2/IntentsBase.sol`) use OpenZeppelin's `SafeERC20.safeTransfer`, which does decode and enforce the boolean return value: [3](#0-2) 

The Tron variant reimplements the same escrow-release logic without that protection.

### Impact Explanation
If a non-standard/return-false ERC20 token is ever used as an intent input/output asset on the Tron deployment, a solver settling a cross-chain `RedeemEscrow` can have their fill "succeed" on-chain (escrow decremented, order marked filled, event emitted) while never actually receiving the tokens — a silent, permanent loss for the solver, and desynchronization between recorded escrow state and actual token custody in the gateway. Because `_filled`/`_orders` are updated unconditionally alongside the flawed check, there is no retry path once this occurs; the escrowed balance is written off. This is a fund-loss / accounting-integrity issue in the token-bridge/intents settlement path.

### Likelihood Explanation
This requires the deployment to whitelist or accept an ERC20 token whose `transfer` can return `false` without reverting (some older/legacy tokens on Tron/TRC20 ecosystems behave this way, and Tron's TRC20 standard historically has more such tokens than mainstream EVM chains). Given IntentGateway is permissionless with respect to which tokens users specify as `inputs`/`outputs` at order-placement time, an attacker or unaware integrator could construct or use such a token to trigger this path. Likelihood is Medium given it depends on token choice, but the reachable trigger (a single `fillOrder`/settlement call) requires no special privileges.

### Recommendation
Replace the raw `token.call(...)` + `success`-only check pattern in `withdraw()` and the `SweepDust` handler with OpenZeppelin's `SafeERC20.safeTransfer`, matching the approach already used in `evm/src/apps/intentsv2/IntentsBase.sol`. This decodes and enforces the ERC20 return value (treating missing/false return data as failure) and reverts the whole state transition — including `_orders` decrements and `_filled` marking — if the transfer did not genuinely succeed.

### Proof of Concept
1. Deploy (or use) an ERC20/TRC20 token whose `transfer(address,uint256)` returns `false` on failure (e.g., insufficient balance) instead of reverting.
2. Place and escrow an order in `IntentGatewayV2` using this token as an input.
3. Drain the gateway's balance of that token through another path (e.g., protocol dust sweep or fee redemption emptying available balance) so the token's internal balance check fails on the next transfer attempt.
4. Trigger settlement (`onAccept` with a `RedeemEscrow` body, or `onGetResponse` refund) so `withdraw()` calls `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))`.
5. The low-level call returns `success = true` with return data `false` (per the token's non-reverting failure semantics); the code proceeds to decrement `_orders[...][token]`, set `_filled[...]`, and emit `EscrowReleased` — despite the beneficiary never receiving the tokens. [4](#0-3)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-683)
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
    }
```

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
