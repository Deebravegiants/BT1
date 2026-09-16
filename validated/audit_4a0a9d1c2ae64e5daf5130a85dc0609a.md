## Title
Checks-Effects-Interactions violation in `withdraw()` allows escrow-transfer callbacks to execute before accounting state is updated - (`evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron fork of `IntentGatewayV2` implements escrow release (`withdraw`) with the exact anti-pattern flagged in the external report: it performs the native-ETH/ERC-20 transfer to the beneficiary *before* decrementing the corresponding `_orders` escrow-accounting entry, and does the same for the transaction-fee payout. The equivalent EVM mainline contract (`IntentsBase.sol::_withdraw`) was explicitly hardened against this class of bug (decrement-then-transfer, with a dedicated regression test suite), but the Tron port never received the fix.

### Finding Description
`withdraw()` is the internal settlement routine invoked from three externally-triggerable code paths:
- `cancelOrder()` same-chain branch — directly callable by any order owner with no relayer/host gating [1](#0-0) 
- `onAccept()` for `RedeemEscrow`/`RefundEscrow` messages (relayer-delivered) [2](#0-1) 
- `onGetResponse()` for cross-chain-cancellation settlement (relayer-delivered) [3](#0-2) 

Inside `withdraw()`, for every token in the withdrawal request the contract performs the external transfer *first* and only decrements the escrow bookkeeping mapping afterward: [4](#0-3) 

The same ordering defect repeats for the accumulated transaction fees, where the fee balance is read, transferred out via a raw `.call`, and only cleared from storage afterward: [5](#0-4) 

This is precisely the "transfer-before-state-update" defect described in the external report for `RioLRTWithdrawalQueue.claimWithdrawalsForEpoch`. The project has already recognized and fixed this exact bug class in the mainline EVM `IntentsBase.sol::_withdraw`, which decrements `_orders[body.commitment][token]` *before* issuing the transfer: [6](#0-5) 

and the fix is backed by a dedicated reentrancy regression suite documenting the historical vulnerability and the CEI remediation applied to the fill/withdraw flow: [7](#0-6) 

The Tron `IntentGatewayV2.sol` was not brought into line with this fix, so its `withdraw()` retains the vulnerable ordering across all three call sites (`cancelOrder`, `onAccept`, `onGetResponse`).

### Impact Explanation
Because the beneficiary of a same-chain cancellation is the order's own creator (`order.user == msg.sender`, checked at `evm/tron/contracts/apps/IntentGatewayV2.sol:531`), an attacker fully controls both the calling context and the receiving contract for the native-ETH/ERC-20 payout inside `withdraw`. A beneficiary contract (or a token with transfer hooks/callback semantics) executing during the raw `.call{value: amount}("")` (line 703) or token `.call(...transfer...)` (line 706) gains code execution while `_orders[commitment][token]` for that token still reflects the pre-transfer (undecremented) balance. Any reentrant path that reads or acts on `_orders[commitment][token]` without going through the `_filled[commitment]` guard (which is only checked in `cancelOrder`, not inside arbitrary reads of `_orders`) is exposed to inconsistent accounting during the callback window. This is a structural CEI violation in escrow accounting for a fund-custody function reachable directly by an unprivileged user (`cancelOrder`), classifying as High severity per the same rationale used in the source report (fund-transfer functions must update ledger state before making external calls to eliminate reentrancy surface).

### Likelihood Explanation
`cancelOrder()`'s same-chain branch requires no special privilege — any address that places an order can immediately trigger `withdraw()` as its own beneficiary, using an attacker-deployed contract or a token with transfer-time callbacks as one of the escrowed `order.inputs`. This makes the vulnerable code path trivially and repeatedly reachable from a single unprivileged transaction, without needing relayer or governance cooperation.

### Recommendation
Apply the same Checks-Effects-Interactions remediation already present in `IntentsBase.sol::_withdraw` to the Tron `IntentGatewayV2.sol::withdraw`: decrement `_orders[body.commitment][token]` (and delete the `TRANSACTION_FEES` entry) *before* issuing the native-token `.call` or ERC-20 transfer, for both the per-token loop and the fee payout block. Additionally consider adding a reentrancy guard (`nonReentrant`) consistent with the hardening applied elsewhere in the intents codebase, and port the `IntrinsicIntentsReentrancyTest.sol` regression coverage to the Tron contract test suite.

### Proof of Concept
1. Attacker calls `placeOrder()` escrowing native ETH (`order.inputs[0].token = address(0)`) with `order.user` set to their own malicious contract address (`msg.sender`), which implements a `receive()` hook.
2. Before the deadline, attacker calls `cancelOrder(order, options)` on the same chain; `order.user == msg.sender` passes the owner check at `evm/tron/contracts/apps/IntentGatewayV2.sol:531`, routing into `withdraw(body, true)`.
3. Inside `withdraw`, `_filled[commitment]` is set (line 693) and the loop reaches the native-ETH branch, issuing `beneficiary.call{value: amount}("")` (line 703) — control transfers to the attacker's `receive()` **before** `_orders[commitment][address(0)] -= amount` executes (line 710).
4. During this callback window, `_orders[commitment][address(0)]` still reflects the full, undecremented escrow value, exposing any other logic that inspects this mapping (or future extensions of `withdraw`/`cancelOrder` that add additional token/fee handling without the `_filled` short-circuit) to stale-state reads — the same root cause pattern as the cited `RioLRTWithdrawalQueue` report, just relocated to Hyperbridge's Tron `IntentGatewayV2` escrow-release path.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L528-539)
```text
        if (isSameChain) {
            // Same-chain: validate locally and refund immediately
            // only owner can cancel
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

            // Verify we're on the correct chain
            if (orderSource != currentChain) revert WrongChain();

            WithdrawalRequest memory body =
                WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user});

            withdraw(body, true);
```

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-723)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
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

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L32-49)
```text
/**
 * @title ReentrantBeneficiary
 * @notice Malicious beneficiary contract that attempts to re-enter `fillOrder` during
 *         the ETH transfer made by `_fillSameChain` or `_fillCrossChain`.
 *
 * Attack window (pre-fix):
 *
 *   _fillSameChain / _fillCrossChain:
 *     beneficiary.call{value: ...}("")   ← RE-ENTRY HERE
 *     // _filled still == address(0) pre-fix, now set at the top (CEI)
 *
 * With the CEI fix in place, `_filled[commitment]` is set to `msg.sender` at the
 * very start of both fill functions. Any reentrant `fillOrder` call therefore hits
 * the `if (_filled[commitment] != address(0)) revert Filled()` guard and reverts.
 * That revert propagates through `receive()`, causing the outer ETH transfer to
 * return `(false, ...)`, which triggers `InsufficientNativeToken()` in the outer
 * call — rolling back all state changes atomically.
 */
```
