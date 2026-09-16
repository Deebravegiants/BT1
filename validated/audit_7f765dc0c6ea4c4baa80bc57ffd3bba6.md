### Title
Interactions-before-effects in `IntentGatewayV2.withdraw` allows a malicious escrow token to re-enter before escrow accounting is finalized - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of the Intent Gateway (`evm/tron/contracts/apps/IntentGatewayV2.sol`) contains an internal `withdraw()` function that performs external token transfers via low-level `.call` **before** updating the escrow accounting mapping `_orders`, unlike the hardened mainline implementation in `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw`, which was specifically fixed (and regression-tested) to follow checks-effects-interactions (CEI).

### Finding Description
`withdraw()` iterates over the withdrawal request's token list and, for each token, performs the external transfer first and decrements the per-commitment escrow balance afterward: [1](#0-0) 

Compare this to the CEI-safe mainline implementation, which decrements `_orders` **before** performing the transfer: [2](#0-1) 

The mainline codebase even ships a dedicated regression suite (`IntrinsicIntentsReentrancyTest.sol`) explicitly documenting that `_filled[commitment]` must be set, and escrow state finalized, *before* any external call, precisely to prevent a malicious beneficiary/token from re-entering during the transfer: [3](#0-2) 

The Tron variant's `withdraw()` also uses raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only checks the boolean `success` (not the actual returned bool/return-data per ERC20's ambiguous transfer semantics), instead of `SafeERC20.safeTransfer` used elsewhere in the file's own `_execute`/`_splitSurplus` helpers.

`withdraw()` is reached from every finalization path: same-chain `cancelOrder` (`evm/tron/contracts/apps/IntentGatewayV2.sol:516-539`), `onAccept` for `RedeemEscrow`/`RefundEscrow` (`evm/tron/contracts/apps/IntentGatewayV2.sol:629-635`), and `onGetResponse` (`evm/tron/contracts/apps/IntentGatewayV2.sol:738-743`). Because `order.inputs` (the escrowed tokens) are fully attacker-controlled at `placeOrder` time, an attacker can escrow a malicious ERC20/hook-token as an input, then trigger a refund/cancel that calls `withdraw()`. During the malicious token's `transfer` callback, `_orders[body.commitment][token]` for that token has not yet been decremented, leaving a window where the escrow bookkeeping is inconsistent with the on-chain balance actually moved.

### Impact Explanation
While `_filled[body.commitment]` is set at the very top of `withdraw()` (before the loop), which blocks a second full top-level re-entry through `cancelOrder`'s `Filled()` check, the per-token escrow accounting (`_orders[commitment][token]`) itself is only updated after the external call within the same execution. This is a direct violation of checks-effects-interactions for state that gates fund movement, and it is the same bug class as the reported `CouncilMember.claim()` issue: an external transfer is made to a potentially malicious/attacker-controlled contract before the ledger entry backing that transfer is finalized. Any future code path, upgrade, or duplicate-token entry in `body.tokens` that reads `_orders[commitment][token]` between the transfer and the decrement — or any interaction that doesn't route through the `_filled` guard — can result in double payout of the same escrowed balance, i.e., theft of escrowed funds from `IntentGatewayV2`.

### Likelihood Explanation
Reachable from a single, unprivileged, user-submitted transaction: any user can call `placeOrder` with an attacker-controlled malicious token as an input, and then trigger `cancelOrder`/refund flow that calls `withdraw()` on that same order, giving the attacker's token contract control of execution mid-withdrawal. The `_filled` guard reduces — but does not eliminate — the risk, since it only protects the top-level entrypoints and not the per-token loop's own interactions-before-effects ordering.

### Recommendation
Rewrite `withdraw()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` to mirror `IntentsBase.sol::_withdraw`: decrement `_orders[body.commitment][token]` (and clear `TRANSACTION_FEES`) **before** performing any external call, use `SafeERC20.safeTransfer` instead of raw `.call`, and add a `nonReentrant` guard as defense-in-depth around `withdraw`/`cancelOrder`/`onAccept`/`onGetResponse`.

### Proof of Concept
1. Attacker deploys a malicious ERC20-like token whose `transfer()` re-enters the gateway (or performs arbitrary side effects) before returning.
2. Attacker calls `placeOrder` on the Tron `IntentGatewayV2`, escrowing the malicious token as `order.inputs[0]`.
3. Attacker (owner) calls `cancelOrder` (same-chain) or drives the cross-chain refund flow, which calls `withdraw(body, true)`.
4. Inside `withdraw`, `token.call(transfer(...))` executes and control passes to the malicious token before `_orders[body.commitment][token] -= amount` runs (`evm/tron/contracts/apps/IntentGatewayV2.sol:702-710`), demonstrating the interactions-before-effects window that departs from the CEI-hardened reference implementation.

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
