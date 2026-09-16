Found a concrete analog in the Tron-specific `IntentGatewayV2` contract. Unlike its EVM counterpart (which uses `SafeERC20.safeTransfer`/`safeTransferFrom` throughout), the Tron variant performs escrow payouts with raw low-level `.call()` invocations and only checks the boolean `success` of the call — it never decodes/validates the ABI-encoded return data of the `transfer()` call.

### Title
Unchecked ERC20 `transfer` return value in Tron `IntentGatewayV2` escrow withdrawal/sweep lets silent-failure tokens be marked as paid while funds remain locked - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2` implements escrow payout (`withdraw`) and dust sweeping (`SweepDust` handling inside `onAccept`) using raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only reverts if the low-level call itself reverted (`!success`). It never inspects the returned calldata to confirm the token actually reported `true`. Non-standard-compliant ERC20/TRC20 tokens that return `false` instead of reverting on a failed transfer will cause `success == true` while no tokens are actually moved, yet the contract proceeds as if the transfer succeeded.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the `withdraw()` function (called from `onAccept` for `RedeemEscrow`/`RefundEscrow` requests and from `onGetResponse`) does: [1](#0-0) 

and marks the beneficiary as filled and decrements the internal escrow ledger regardless of whether the token transfer actually succeeded: [2](#0-1) 

The same unchecked-return pattern is used for fee redemption in the same function: [3](#0-2) 

and for the `SweepDust` request handler: [4](#0-3) 

This contract explicitly imports and even applies `using SafeERC20 for IERC20;`, and uses `safeTransferFrom` correctly on the deposit side (`placeOrder`), but reverts to raw, unchecked `.call` for the actual payout paths: [5](#0-4) [6](#0-5) 

Because `success` from a low-level `.call` only reflects whether the callee reverted — not what boolean value it returned — any token whose `transfer()` returns `false` on failure (rather than reverting), a token with unusual fallback semantics, or any token contract that doesn't strictly conform to EIP-20's success flag will let `withdraw()`/`SweepDust` treat a failed transfer as a completed one.

### Impact Explanation
Once `withdraw()` runs past the `.call`, it unconditionally does `_filled[body.commitment] = beneficiary` and `_orders[body.commitment][token] -= amount`, permanently closing out the escrow slot for that commitment/token. If the underlying transfer silently failed, the escrowed tokens remain stuck in the `IntentGatewayV2` contract balance with no accounting entry pointing to them (the escrow mapping has already been zeroed/decremented and `_filled` marks the order as settled), so the beneficiary/solver can never re-claim them — a permanent freezing of funds. The same applies to `SweepDust`, where dust meant for the specified beneficiary can be lost while the event still reports it as swept.

### Likelihood Explanation
This path is reachable by any relayer that finalizes a `RedeemEscrow`/`RefundEscrow` cross-chain message (authenticated only by proof of the source-side dispatch, not privileged) whenever the escrowed token is one of the non-standard-compliant/false-returning ERC20/TRC20 tokens that the order originally used as input — a common occurrence on Tron given the prevalence of legacy TRC20 tokens with EIP-20 return-value quirks. No attacker privilege is required beyond normal relaying of a legitimately dispatched settlement message; the trigger condition is solely the token's transfer semantics, which is outside gateway control once the token is accepted as valid input.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only checks in `withdraw()` and the `SweepDust` handler with OpenZeppelin's `SafeERC20.safeTransfer`, consistent with how deposits already use `safeTransferFrom` in the same file. If avoiding revert-on-failure semantics is intentional for Tron-specific USDT-style behavior, at minimum decode and validate the returned boolean (`success && (data.length == 0 || abi.decode(data, (bool)))`) before mutating escrow state, and revert (or otherwise avoid clearing the escrow) if the decoded return is `false`.

### Proof of Concept
1. A user places an order in `IntentGatewayV2` (Tron variant) using a TRC20/ERC20 token `T` as input, whose `transfer()` implementation returns `false` on failure instead of reverting (e.g., paused, blacklisted recipient, or insufficient allowance edge case defined by the token's own logic) — such tokens are common outside strictly OZ-compliant deployments.
2. The order is filled/cancelled and hyperbridge delivers a `RedeemEscrow`/`RefundEscrow` message; any relayer submits the proof, invoking `onAccept` → `withdraw()`.
3. `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` executes without reverting but the token's internal logic returns `false` (e.g., the beneficiary is blacklisted or the token enforces a cooldown), so `success == true`.
4. `withdraw()` proceeds: `_filled[commitment] = beneficiary` is set and `_orders[commitment][token] -= amount` decrements the escrow record, even though `amount` of `T` never left the gateway's balance.
5. The beneficiary receives nothing; the escrow record no longer reflects the un-transferred `amount`, and since `_filled` is set, retry logic elsewhere (e.g., `onGetResponse` re-check) treats the commitment as already settled — permanently orphaning the tokens inside the contract.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-710)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-722)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```
