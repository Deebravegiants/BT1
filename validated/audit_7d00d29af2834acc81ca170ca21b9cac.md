## Title
Unchecked ERC20 return value in `IntentGatewayV2.withdraw` (Tron variant) permanently strands escrowed funds instead of reverting - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

## Summary
The Tron deployment of `IntentGatewayV2` re-implements token transfers with raw low-level `.call(...)` and only checks that the *call itself* did not revert, never inspecting the returned ABI-encoded boolean. This deviates from the mainline EVM contract, which uses OpenZeppelin's `SafeERC20.safeTransfer` (imported and aliased via `using SafeERC20 for IERC20` in the very same file) everywhere except this bespoke path. Any ERC20/TRC20 token that signals failure by returning `false` rather than reverting — a well-known non-standard pattern common on Tron — will pass this check even though no tokens actually moved, while the contract has already decremented escrow accounting and finalized the order.

## Finding Description
`IntentGatewayV2.withdraw` (internal, invoked from `onAccept` on `RedeemEscrow`/`RefundEscrow` and from `onGetResponse`) releases escrowed input tokens to a beneficiary (the filling solver, or the user on refund): [1](#0-0) 

For every non-native token it does:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```
and then unconditionally decrements `_orders[body.commitment][token] -= amount;` and marks `_filled[body.commitment] = beneficiary` for finalization. `success` only reflects whether the external call reverted — it does not decode/verify the returned `bool`. A token whose `transfer()` returns `false` on failure (insufficient balance in the gateway due to prior fee-on-transfer mismatches, blacklist/pause logic, or any non-compliant TRC20) will make this call "succeed" while transferring zero tokens. The escrow bookkeeping is nonetheless permanently decremented and the order is marked filled/refunded, so the entitled solver or user can never claim the tokens — the ISMP-verified settlement message that funded this call cannot be replayed (the order is already `_filled`), and the underlying tokens remain irretrievably stuck in the gateway.

This same unchecked `.call(...IERC20.transfer.selector...)` pattern recurs in `SweepDust` handling later in the same file, and the contract's own `using SafeERC20 for IERC20` (imported specifically to avoid exactly this class of bug) is never applied to these code paths — a clear internal inconsistency between the audited mainline EVM contract (which uses `IERC20.safeTransfer` throughout `IntentsBase._withdraw`) and this custom Tron re-implementation. [2](#0-1) 

## Impact Explanation
This is reachable from the standard, permissionless cross-chain settlement flow: a relayer delivers a legitimately Hyperbridge-verified `RedeemEscrow`/`RefundEscrow` POST request (or a GET response for source-chain cancellation), and `onAccept`/`onGetResponse` call `withdraw` with attacker-uninfluenced but token-dependent behavior. Whenever the escrowed token belongs to the class of non-reverting-on-failure ERC20/TRC20 tokens, the result is permanent freezing of the escrowed input funds: the order is irreversibly finalized (`_filled` set, escrow balance zeroed) but the beneficiary never receives the tokens. This is a direct, unauthorized loss of user/solver funds meeting the "permanent freezing of funds" bar.

## Likelihood Explanation
No attacker action or privilege is required beyond normal solver/user participation in the Intent Gateway market on Tron; the trigger condition is simply that the escrowed asset is a non-standard-return TRC20 token (common on Tron) or that the gateway's balance for that token is momentarily insufficient for any reason. Given Tron's TRC20 ecosystem includes multiple tokens historically known for these non-reverting semantics, and given the Intent Gateway is designed to be permissionlessly usable with arbitrary listed tokens, this is a realistically reachable and repeatable condition, not a contrived edge case.

## Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` invocations in `withdraw` (and `SweepDust`) with `IERC20(token).safeTransfer(beneficiary, amount)`, consistent with the `using SafeERC20 for IERC20` declaration already present in the file and with the mainline `IntentsBase._withdraw` implementation. This ensures a token that signals failure via a `false` return (rather than reverting) causes the whole settlement call to revert, keeping the escrow accounting and finalization state consistent with actual token movement.

## Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) with a TRC20 token `T` implementing `transfer` to return `false` on failure instead of reverting (e.g., a paused/blacklisted or balance-insufficient state internally handled without revert — a widely-seen TRC20 pattern).
2. User places an order escrowing `T` as input; solver fills the order cross-chain in the normal flow.
3. Induce `T.transfer(beneficiary, amount)` to return `false` for the gateway's call (e.g., temporarily pause/blacklist the gateway or beneficiary address inside `T`, then unpause after settlement is finalized to demonstrate funds are unrecoverable).
4. The relayer delivers the verified `RedeemEscrow` message; `withdraw()` executes, `success` is `true` (call didn't revert), no tokens move, yet `_orders[commitment][T] -= amount` and `_filled[commitment] = beneficiary` execute.
5. Confirm `T.balanceOf(beneficiary)` is unchanged while `_orders(commitment, T)` is now zero and `_filled(commitment)` is set — the escrowed `T` is permanently stuck in the gateway with no code path to reclaim it.

### Citations

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
