### Title
Unchecked ERC20 boolean return value in `withdraw`/`onAccept` fund-transfer paths permanently strands escrowed user funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.sol` (Tron variant) settles escrowed intent funds using a raw low-level `.call()` to the ERC20 `transfer` selector and only checks that the *external call itself* did not revert (`success`). It never decodes/validates the ERC20 boolean return value, unlike the `SafeERC20.safeTransfer` used elsewhere in the codebase (e.g. `IntentsBase.sol`). A token that returns `false` on failure instead of reverting will be treated as a successful transfer.

### Finding Description
In `withdraw()` and in the `SweepDust` branch of `onAccept()`, token payouts are performed as: [1](#0-0) [2](#0-1) [3](#0-2) 

The pattern `(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount)); if (!success) revert TransferFailed();` only asserts that the low-level call did not revert. It ignores the returned `bytes` payload entirely — it never decodes it as a `bool` nor checks its value. This differs from the safe pattern used by `SafeERC20.safeTransfer` (via OpenZeppelin's `_callOptionalReturn`), which additionally requires `returndata.length == 0 || abi.decode(returndata, (bool))` to be true. That safer pattern is in fact used correctly elsewhere in the same protocol, e.g. `IntentsBase.sol`'s `_withdraw`: [4](#0-3) 

For any ERC20 implementation that signals failure by returning `false` (rather than reverting) — a legitimate and historically common pattern (e.g. tokens implementing pre-EIP20 "safe math" checks, or custom pausable/blacklist tokens that return `false` instead of reverting on a blocked recipient) — the low-level `.call` still reports `success = true` because the call executed without reverting. `withdraw()` then unconditionally decrements the escrow accounting as if the transfer succeeded: [5](#0-4) 

This mirrors the audit-report bug class (unchecked `transfer` return value in `MarginTrading.sol::cleanToken`), but here the consequence is materially worse: rather than just an incorrect log event, the escrow ledger `_orders[body.commitment][token]` is decremented and `_filled[body.commitment]` is marked as settled even though the beneficiary received nothing.

### Impact Explanation
Because `_orders[...]` is zeroed/decremented and `_filled[commitment]` is set regardless of whether the ERC20 actually moved tokens, the beneficiary's claim on the escrowed funds is destroyed on-chain state while the tokens themselves remain stuck in the `IntentGatewayV2` contract with no accounting path to reclaim them (the escrow record no longer reflects an outstanding balance). This is a permanent freezing/loss-of-funds condition for solvers/users relying on `RedeemEscrow`/`RefundEscrow` fulfillment or dust sweeps on the Tron deployment, satisfying the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Reachable by any relayer delivering a legitimate `RedeemEscrow`/`RefundEscrow`/`SweepDust` ISMP message once a whitelisted intent token happens to be (or becomes) a non-reverting-on-failure ERC20 — no attacker privilege is required beyond normal relaying of a cross-chain message, and no malicious governance/admin action is needed. The likelihood is bounded by whether such a token is configured in `order.inputs`/`body.tokens`, which is plausible for arbitrary user-supplied intent tokens on Tron (TRC20 tokens commonly diverge from strict EIP-20 revert semantics).

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only check with `SafeERC20.safeTransfer` (as already used in `IntentsBase.sol`), or explicitly decode and require the boolean return value in addition to `success`, in all three locations: `withdraw()`'s escrow-token loop, `withdraw()`'s fee-token payout, and the `SweepDust` handler in `onAccept()`.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron) with an ERC20/TRC20 whose `transfer` implementation returns `false` on failure (e.g., due to a blacklist or paused state) instead of reverting.
2. A user creates and escrows an order using this token; `_orders[commitment][token]` is credited.
3. Later, a relayer delivers a `RedeemEscrow` request for a beneficiary who is (or becomes) blacklisted by the token, so `transfer` returns `false` but the underlying call does not revert.
4. `withdraw()` observes `success == true` from the low-level call, decrements `_orders[commitment][token] -= amount`, and marks `_filled[commitment] = beneficiary`.
5. The beneficiary never receives tokens (transfer silently failed), yet the escrow accounting shows the order as filled/zeroed — the tokens remain locked in the contract with no code path referencing them, permanently freezing those funds.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L700-710)
```text
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
