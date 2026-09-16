Confirmed: `_sendValue` at `evm/src/apps/intentsv2/IntentsBase.sol:419-422` reverts the entire call on a failed native transfer (`if (!sent) revert InsufficientNativeToken();`). This is used by `_withdraw` (`IntentsBase.sol:451-470`), the function invoked when a `RedeemEscrow`/`RefundEscrow` request is delivered to release a filled or refunded order's escrowed tokens to `beneficiary`.

### Title
Permanent freezing of intent escrow when beneficiary cannot receive native token in `_withdraw` - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`_withdraw` reverts the entire withdrawal (both native and ERC20 legs, plus fee payout and `_filled` bookkeeping) if a single native-token transfer to `beneficiary` fails, with no fallback path (e.g., pull-payment/escrow-for-later) to recover the funds. If the `beneficiary` address can never accept plain ETH transfers (e.g., a contract with no `receive`/fallback, or one whose fallback always reverts/exceeds gas), the escrowed assets for that order become permanently unrecoverable.

### Finding Description
`_withdraw` at [1](#0-0)  loops over `body.tokens`, and for native token entries calls `_sendValue(beneficiary, amount)`. `_sendValue` is defined as an unconditional-revert-on-failure helper: [2](#0-1) .

This function is reached from `onAccept` handling of `RedeemEscrow`/`RefundEscrow` request kinds (confirmed in the Tron variant of the gateway, which shares the same design): [3](#0-2)  and the corresponding `withdraw` implementation there similarly reverts on a failed native send: [4](#0-3) .

Crucially, `EvmHost.dispatchIncoming` treats an `onAccept` revert as "retryable" — it deletes the request receipt and returns without reverting the whole batch: [5](#0-4) . This is by design for normal transient failures (documented as intentional in `docs/content/protocol/ismp/requests.mdx:113-115`). However, when the failure is *deterministic* — i.e., `beneficiary` can never accept a bare ETH transfer — every future replay of the same message hits the exact same revert. The escrow can never be released, and because `_filled`/fee bookkeeping is also inside the same all-or-nothing `_withdraw` call, there is no partial recovery (e.g., ERC20 legs of the same order also never settle, and accumulated transaction fees are never paid out).

This mirrors the reported bug class (`VUSD.processWithdrawals`): a single stuck recipient blocks/loses value that should belong to that recipient, because there is no isolation between one failing payout and the rest of the withdrawal logic, and no persistent record that lets the failing leg be retried differently or skipped in favor of forward progress. In `VUSD` the loop *skips forward past* the failed withdrawal and forgets it; here the entire `_withdraw` reverts and is retried at the message-delivery layer with identical inputs, producing an infinite failure loop with the same net effect — the beneficiary's (and, transitively, the whole order's) funds are permanently stuck.

### Impact Explanation
Funds legitimately owed to an order's beneficiary (solver's fill proceeds, or a user's refund on order failure) become permanently locked in the `IntentGatewayV2`/`IntentsBase`-derived contract with no governance or user-triggered recovery path, since the destination address is attacker- or user-controlled (an order's `beneficiary` is set by whoever constructs the order/fill). This satisfies "permanent freezing of funds" — Medium/High severity depending on whether beneficiary can be chosen adversarially by a third party to grief an honest solver's payout, or is simply a smart-contract wallet that lacks a `receive()`.

### Likelihood Explanation
Likelihood is realistic: any order or fill whose `beneficiary` resolves to a smart-contract address without a payable fallback (a common integration mistake, or an intentional griefing vector against solvers who fill orders with a contract-controlled payout address) triggers this deterministically on the very first delivery attempt and on every subsequent retry.

### Recommendation
Isolate the native-token transfer failure from the rest of `_withdraw`'s bookkeeping: use a try/catch or low-level call with an explicit failure branch that stores the amount in a per-beneficiary "credit" balance (pull-payment pattern) instead of reverting the whole function, then finalize `_filled`/fee accounting regardless of whether the individual native leg succeeded. Provide a separate `withdrawCredit(address beneficiary)`-style function the beneficiary (or anyone, permissionlessly, paying out to that fixed address) can call to retry that leg, mirroring `VUSD`'s own recommended fix of keeping the failed entry retryable rather than reverting/skipping the entire transaction.

### Proof of Concept
1. Deploy a `beneficiary` contract with no `receive()`/`fallback()` (or one that always reverts).
2. Create/fill an order (via `IntentGatewayV2`/`ExtrinsicIntents`) with `output.beneficiary` (or `order.user` for a refund) set to this contract's address, including a native-token component in `body.tokens`.
3. Deliver the `RedeemEscrow` or `RefundEscrow` request to `onAccept`; `_withdraw` → `_sendValue` reverts with `InsufficientNativeToken`.
4. Per `EvmHost.dispatchIncoming` ( [6](#0-5) ), the receipt is deleted so the message is "retryable" — but every subsequent redelivery attempt fails identically, since the contract can never accept ETH. The escrowed tokens (native and ERC20 legs alike, plus fees) remain locked in the gateway indefinitely.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L418-422)
```text
    /// @dev Native transfer that reverts with `InsufficientNativeToken` if refused.
    function _sendValue(address to, uint256 amount) internal {
        (bool sent,) = to.call{value: amount}("");
        if (!sent) revert InsufficientNativeToken();
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-708)
```text
            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }
```

**File:** evm/src/core/EvmHost.sol (L794-818)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```
