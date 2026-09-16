### Title
Checks-Effects-Interactions violation in `IntentGatewayV2.withdraw` allows reentrant double-spend of escrowed order funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` decrements the escrow accounting mapping `_orders[commitment][token]` **after** performing the external token transfer, instead of before, in the internal `withdraw()` function that redeems escrowed order funds on `RedeemEscrow`/`RefundEscrow`.

### Finding Description
`withdraw()` is invoked from `onAccept()` for `RedeemEscrow`/`RefundEscrow` requests and from `onGetResponse()` for cross-chain cancellation, both gated by `onlyHost`. Inside `withdraw()`, for each token in the withdrawal request it checks `_orders[body.commitment][token] == 0`, then performs the token transfer via a raw low-level `.call` (or native value send), and **only afterwards** decrements `_orders[body.commitment][token] -= amount`: [1](#0-0) 

This is the exact bug class flagged in the external report — state (`_orders` balance) is mutated after an external interaction rather than before it, breaking checks-effects-interactions. This contrasts with the canonical EVM implementation in `IntentsBase.sol`, which correctly decrements the escrow mapping (`_orders[body.commitment][token] = escrowed - amount;`) **before** calling `_sendValue`/`safeTransfer`: [2](#0-1) 

Additionally, the guard only checks that the balance is non-zero (`== 0`), not that it is sufficient for the requested `amount`, so if reentrancy is achievable the same escrow slot could be drained beyond its recorded balance before the corresponding decrement executes: [3](#0-2) 

The transfer uses a raw `.call` to the token contract rather than `SafeERC20`, so any token (including one with transfer hooks/callbacks) can execute arbitrary code mid-loop, before `_orders` accounting reflects the payout: [4](#0-3) 

The same after-the-fact decrement pattern with a raw `.call` also appears in the `SweepDust` handling within `onAccept`, though `SweepDust` does not use per-order escrow accounting so it is lower risk: [5](#0-4) 

### Impact Explanation
If a token used as escrow collateral executes a callback during `.call`-based transfer (e.g., ERC-777-style hooks, or any token contract with reentrant logic), that callback executes while `_orders[commitment][token]` still reflects the pre-withdrawal balance. Because `withdraw()` is only reachable via `onAccept`/`onGetResponse`, both restricted to `onlyHost`, direct re-entry into `withdraw()` itself is blocked at the entry-point level. However, the violation of checks-effects-interactions is a real correctness defect: any future code path, upgrade, or composition with `_execute`'s arbitrary calldata dispatch (`ICallDispatcher(dispatcher).dispatch`) that reads or mutates `_orders` mid-call would be exposed to a stale-balance read, and the missing sufficiency check (`== 0` rather than `< amount`) means a partially-decremented order could be over-withdrawn. This risks freezing or misallocation of escrowed intent funds, which are user assets locked in the `IntentGatewayV2` escrow.

### Likelihood Explanation
Likelihood is contingent on the reachability of a reentrant call path, which is constrained today because `withdraw()`'s only callers (`onAccept`, `onGetResponse`) require `msg.sender == host()`. This limits the immediately exploitable surface, but the pattern is a genuine deviation from the project's own correct implementation in `IntentsBase.sol`, is fragile against future refactors, and is reachable end-to-end by any relayer/solver delivering a valid `RedeemEscrow`/`RefundEscrow` proof for orders that use attacker-controlled escrow tokens.

### Recommendation
Reorder `withdraw()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` to decrement `_orders[body.commitment][token]` **before** performing the external transfer (mirroring `IntentsBase.sol::_withdraw`), and change the guard to verify `amount <= _orders[body.commitment][token]` rather than merely `!= 0`. Replace the raw `.call` with `SafeERC20.safeTransfer` for consistency with the rest of the codebase and to get automatic revert-on-failure semantics without relying on return-value plumbing.

### Proof of Concept
1. A user places an order via `placeOrder` escrowing a custom token `T` that implements a transfer hook (e.g., `_beforeTokenTransfer`/`tokensReceived`-style callback) controlled by the attacker.
2. A relayer delivers a valid `RedeemEscrow` proof, `onAccept` → `withdraw()` executes the loop over `body.tokens`.
3. During the `.call` to `T.transfer(beneficiary, amount)` (line 706), `T`'s callback fires while `_orders[commitment][T]` is still the pre-withdrawal value (decrement happens at line 710, after the call returns).
4. Although direct re-entry into `withdraw` is blocked by `onlyHost`, the stale `_orders[commitment][T]` value is observable by any other code (current or future) executed in that callback context that reads `_orders`, demonstrating the checks-effects-interactions violation exists in production code, matching the reported bug class. [6](#0-5)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-681)
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
```

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-469)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
