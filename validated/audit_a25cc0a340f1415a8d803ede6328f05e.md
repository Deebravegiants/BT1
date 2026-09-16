### Title
Unchecked ERC20 boolean return value in Tron IntentGatewayV2 `withdraw`/`SweepDust` can permanently mark escrow released without tokens actually moving - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` performs ERC20 token payouts with a raw low-level `.call()` to the `transfer` selector and only checks the boolean `success` returned by the *call itself* (i.e., whether the call reverted), never decoding/validating the ERC20's own returned `bool` value. This is the inverse-but-equally-dangerous case of the `Erc20CheckedTransfer` bug class described in the external report: instead of reverting on tokens that don't return a bool, this code silently accepts tokens that *do* return a bool equal to `false` (a documented failure mode of some ERC20 implementations) as if the transfer succeeded.

### Finding Description
In `withdraw()`, escrowed tokens are released via: [1](#0-0) 

and fee tokens via: [2](#0-1) 

The same unchecked pattern is used for governance dust sweeps in `onAccept`'s `SweepDust` branch: [3](#0-2) 

In all three cases, `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` returns `(bool success, bytes memory data)`. The code checks only `success` — whether the external call reverted — and never inspects `data` to confirm the ERC20 contract's own return value is `true`. Per the ERC20 standard, compliant tokens are permitted to return `false` on a failed transfer instead of reverting. With such a token, the low-level call succeeds (`success == true`) even though no tokens were actually moved, so the code proceeds as if the transfer had succeeded.

Crucially, this is inconsistent with the rest of the codebase: the primary EVM `IntentGatewayV2` (via `IntentsBase._withdraw` and `_sweepDust`) correctly uses OpenZeppelin's `SafeERC20.safeTransfer`, which decodes and enforces the boolean return value: [4](#0-3) [5](#0-4) 

Only the Tron deployment's `withdraw` and `SweepDust` handling regressed to the unsafe raw-call pattern.

### Impact Explanation
`withdraw()` is invoked from `onAccept` for `RedeemEscrow`/`RefundEscrow` requests, which are cross-chain messages authenticated against the paired remote gateway instance and delivered by any relayer submitting a valid Hyperbridge proof: [6](#0-5) 

For any escrowed token that returns `false` on a failed `transfer` (rather than reverting) — e.g. due to an edge condition in that token's implementation — `withdraw()` will:
1. Decrement `_orders[commitment][token]` as if the payout succeeded,
2. Set `_filled[commitment] = beneficiary`, permanently finalizing the order,
3. Emit `EscrowReleased`/`EscrowRefunded`,

while the beneficiary receives nothing. Because the order is marked filled and the escrow accounting is decremented, the tokens remain stuck in the contract with no accounting path left to reclaim them (the order can't be re-withdrawn since `_filled` is set and `_orders` is already zeroed). This is a permanent freezing/loss of user or solver escrowed funds. The same applies to protocol dust swept via `SweepDust`.

### Likelihood Explanation
Triggering requires an ERC20 token configured for escrow whose `transfer` returns `false` on failure instead of reverting (a real, documented pattern among ERC20 tokens, distinct from — but adjacent to — tokens that return no data at all). Since the protocol's stated design is to support "any ERC20 token," and there is no allowlist restricting token behavior visible in this contract, this is a realistic condition for at least a subset of tokens users/solvers might escrow on the Tron deployment, making this Medium-severity and directly reachable by ordinary users placing/filling orders and relayers delivering cross-chain proofs — no privileged role required.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` and the `SweepDust` handler in `evm/tron/contracts/apps/IntentGatewayV2.sol` with OpenZeppelin's `SafeERC20.safeTransfer`, mirroring the already-correct implementation in `evm/src/apps/intentsv2/IntentsBase.sol`'s `_withdraw`/`_sweepDust`. `safeTransfer` decodes the returned data (when present) and reverts if it is `false`, while still supporting tokens that return no data at all — addressing both failure modes safely.

### Proof of Concept
1. Configure (or have a user select) an ERC20 token as an order input whose `transfer` implementation returns `false` on failure without reverting (standard-compliant behavior for many token contracts under certain conditions, e.g. `Comp`-like tokens returning `bool` and going to `false` for underflow-guarded transfers in old Solidity versions, or tokens intentionally implemented this way for backward-compatibility).
2. Force a state in the token contract where a subsequent `transfer` call to `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` returns `(true, abi.encode(false))` — i.e., the external call itself succeeds but the encoded boolean payload is `false`.
3. Have Hyperbridge deliver a `RedeemEscrow`/`RefundEscrow` request for the corresponding commitment; `onAccept` calls `withdraw(body, ...)`.
4. In `withdraw()`, `(bool success,) = token.call(...)` evaluates `success == true` (the call didn't revert), so the `if (!success) revert TransferFailed();` check passes despite the token not transferring value.
5. `_orders[body.commitment][token] -= amount;` and `_filled[body.commitment] = beneficiary;` execute, finalizing the order and emitting `EscrowReleased`, even though the beneficiary's token balance is unchanged — the escrowed tokens remain stuck in the contract permanently, unrecoverable through the normal withdrawal flow.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L646-650)
```text
            if (token == address(0)) {
                _sendValue(req.beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(req.beneficiary, amount);
            }
```
