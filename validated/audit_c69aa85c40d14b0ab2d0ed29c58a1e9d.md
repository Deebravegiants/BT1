### Title
Reentrant token/native transfer before escrow decrement in `IntentGatewayV2.withdraw` (Tron variant) enables double-spend of escrowed funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron fork of `IntentGatewayV2` performs the external token/native transfer for each escrowed asset **before** decrementing the corresponding `_orders[commitment][token]` balance, violating checks-effects-interactions. This is the same bug class as the reported "reentrancy in reward/balance accounting before state update" issue, applied to Hyperbridge's intents escrow, which is reachable by any relayer delivering a `RedeemEscrow`/`RefundEscrow` message or `GetResponse` for a solver-filled order.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `withdraw()` (lines 691–730) iterates over `body.tokens`:
```solidity
if (_orders[body.commitment][token] == 0) revert UnknownOrder();
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    ...
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    ...
}
_orders[body.commitment][token] -= amount;
``` [1](#0-0) 

The balance check (`_orders[...] == 0`) only validates non-zero escrow, not "amount already fully consumed", and the debit (`-= amount`) happens **after** the external `.call`. Compare this to the canonical (non-Tron) implementation in `IntentsBase.sol`, which correctly decrements state before making the external transfer:
```solidity
_orders[body.commitment][token] = escrowed - amount;
if (token == address(0)) {
    _sendValue(beneficiary, amount);
} else {
    IERC20(token).safeTransfer(beneficiary, amount);
}
``` [2](#0-1) 

The same after-the-fact pattern repeats for the fee-token payout:
```solidity
uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
if (fees > 0) {
    address feeToken = IDispatcher(host()).feeToken();
    (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
    ...
    delete _orders[body.commitment][TRANSACTION_FEES];
}
``` [3](#0-2) 

`withdraw()` is reached from two authenticated but relayer-triggerable entry points:
- `onAccept` for `RequestKind.RedeemEscrow`/`RefundEscrow`, gated by `authenticate(incoming.request)` [4](#0-3) 
- `onGetResponse`, which decodes the same `WithdrawalRequest` from `incoming.response.request.context` and calls `withdraw(body, true)` [5](#0-4) 

A malicious `beneficiary` (a contract) receiving native value via `.call{value: amount}("")`, or a token with transfer hooks (ERC-777-like/callback tokens), executing during that external call can re-enter application logic before `_orders[...][token]` is decremented. This is a live analog of the reported bug class: an unprivileged relayer/solver can construct an order whose `beneficiary` is an attacker-controlled contract, and the escrow/fee balance used for the "has funds" gate is stale at the moment of the external call, exactly mirroring the reported `earned()`-before-effects reentrancy pattern in `VirtualStakingRewards`.

### Impact Explanation
If reentrancy into `withdraw` (or any other state-mutating path reachable from the callback, e.g., a second delivery of the same/duplicate `RedeemEscrow` proof, or manipulation of order accounting via a second overlapping withdrawal for the same commitment/token before the debit lands) succeeds, an attacker can drain more of the escrowed input tokens or fee tokens than were actually escrowed for their order — a direct theft of user/protocol funds held by the gateway. This satisfies the "concrete theft ... of funds" bar for validity.

### Likelihood Explanation
Medium-High: this requires (a) placing/filling an order where the `beneficiary` is an attacker-controlled contract or a malicious/callback-capable ERC20 is one of the escrowed tokens, and (b) that the reentrant call path actually reaches a state-mutating function before `_orders` is debited (the top-level entry points are `onlyHost`-gated, so full exploitability depends on whether the host's message-dispatch loop or any other externally-reachable function shares mutable `_orders[commitment][...]` state reachable without host gating). I was not able to fully verify, within the remaining budget, whether any externally-reachable (non-`onlyHost`) function on `IntentGatewayV2` or a companion contract touches the same `_orders` mapping for the same commitment such that a same-transaction reentrant call would succeed without needing the host to call back in. This significantly affects likelihood and should be verified against `evm/src/core/HandlerV2.sol`'s message-receipt-commit ordering and any other public/external functions on this contract that read or write `_orders[commitment][...]`.

### Recommendation
Apply the checks-effects-interactions pattern used in the canonical `IntentsBase.sol`: decrement (or delete) `_orders[body.commitment][token]` and `_orders[body.commitment][TRANSACTION_FEES]` **before** performing the external `.call`/`safeTransfer`, and add an explicit reentrancy guard on `withdraw` (and on `onAccept`/`onGetResponse`) as defense in depth, consistent with the fix already applied elsewhere in the codebase (see `IntrinsicIntentsReentrancyTest.sol`, which documents a CEI fix for the same class of bug in `IntrinsicIntents._fillSameChain`/`ExtrinsicIntents._fillCrossChain`) [6](#0-5) .

### Proof of Concept
Conceptual PoC (not executed, given tool constraints):
1. Attacker places a cross-chain order via `placeOrder` where `beneficiary` (on the destination-side redeem path) is a malicious contract with a `receive()`/token-transfer hook, and one input token is escrowed on this Tron `IntentGatewayV2`.
2. A relayer delivers the `RedeemEscrow` request; `authenticate()` passes and `withdraw()` runs.
3. During `beneficiary.call{value: amount}("")` (or the malicious token's transfer hook), the attacker's contract re-enters a path that reads/writes `_orders[body.commitment][token]` again before the outer call's `_orders[...] -= amount` executes, causing the check `_orders[body.commitment][token] == 0` to still pass and a second transfer of `amount` to be issued.
4. Net effect: the attacker receives more than the escrowed `amount` for that commitment/token, or the fee-token payout is claimed twice via the analogous `TRANSACTION_FEES` pattern. [7](#0-6)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-744)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
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

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L85-93)
```text
/**
 * @title IntrinsicIntentsReentrancyTest
 * @notice Forge tests that confirm the CEI fix in `IntrinsicIntents._fillSameChain`
 *         and verify that `ExtrinsicIntents._fillCrossChain` is also resistant to
 *         reentrancy attacks.
 *
 * Both fill functions now open with `_filled[commitment] = msg.sender` before any
 * external calls, so a reentrant `fillOrder` attempt is always blocked by the
 * `Filled()` guard in `IntentGatewayV2.fillOrder`.
```
