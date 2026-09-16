## Title
Reentrancy via Violated Checks-Effects-Interactions in `IntentGatewayV2.withdraw` (Tron Variant) - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The external-report's bug class — external calls executed without state finalization happening first, opening a reentrancy window — has a concrete, live analog in the Tron fork of `IntentGatewayV2`. Its `withdraw` function performs the token/native transfer to `beneficiary` *before* decrementing the corresponding escrow balance, whereas the canonical EVM version of the same logic (`IntentsBase._withdraw`) was explicitly hardened to decrement escrow before transferring, and the same class of bug (`fillOrder`) was fixed and regression-tested elsewhere in the repo.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `withdraw` sets `_filled[body.commitment]` up front (CEI on the fill flag) but then, for each token in the withdrawal, makes the external transfer **before** updating the `_orders` escrow accounting: [1](#0-0) 

```solidity
function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
    address beneficiary = address(uint160(uint256(body.beneficiary)));
    _filled[body.commitment] = beneficiary;

    for (uint256 i; i < len;) {
        ...
        if (token == address(0)) {
            (bool sent,) = beneficiary.call{value: amount}("");   // EXTERNAL CALL FIRST
            ...
        } else {
            (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
            ...
        }
        _orders[body.commitment][token] -= amount;                // STATE UPDATE AFTER
        ...
    }
```

Compare this with the canonical, already-hardened version in `IntentsBase._withdraw`, which decrements escrow **before** transferring: [2](#0-1) 

The `fillOrder` path had exactly this class of bug (external call before state finalization) and was fixed with an up-front `_filled[commitment] = msg.sender` CEI pattern, with dedicated regression tests (`IntrinsicIntentsReentrancyTest.sol`) proving the fix blocks reentrant self-fills and fee theft: [3](#0-2) 

The Tron variant's `withdraw` does not carry the equivalent fix for its per-token loop: only the `_filled` flag is CEI-compliant, the `_orders[...]` decrement is not. `withdraw` is reached via `onAccept` when a `RedeemEscrow`/`RefundEscrow` message is delivered by a relayer, and the `beneficiary` for a redeem is the solver who filled the order on the other chain — an address fully controlled by whoever fills orders (an unprivileged, permissionless actor): [4](#0-3) 

### Impact Explanation
When an order's escrow includes a native-token leg, the beneficiary (attacker-controlled solver contract) receives control during the `.call{value: amount}("")` before `_orders[commitment][token]` is decremented. For any order whose withdrawal batches multiple token legs (native + ERC20, or a token appearing more than once across the batch), the escrow bookkeeping for tokens not yet reached in the loop is still at its pre-withdrawal value during the callback window. This breaks the accounting invariant the rest of the contract relies on (`_orders[commitment][token] == 0` is the only guard, not a strict `>=` comparison), and is the exact "state finalized after external call" pattern that upstream (`IntentsBase._withdraw`, `fillOrder`) was hardened against with tests specifically written to catch it.

### Likelihood Explanation
Medium. Reachable only via legitimate protocol flow (a solver fills a cross-chain order, is set as `beneficiary`, and a relayer delivers the resulting `RedeemEscrow`/`RefundEscrow` message) — no admin or privileged access needed. Exploitability depends on the specific shape of `body.tokens` in a given withdrawal (multiple legs including a native-token leg), which is protocol-derived but the beneficiary/attacker fully controls whether it is a malicious contract.

### Recommendation
Apply the same CEI fix used in `IntentsBase._withdraw` and `fillOrder`: decrement `_orders[body.commitment][token]` **before** performing the native/ERC20 transfer inside the per-token loop in `evm/tron/contracts/apps/IntentGatewayV2.sol::withdraw`, and/or add a `nonReentrant` guard consistent with the rest of `IntentGatewayV2`.

### Proof of Concept
1. Attacker fills a cross-chain order (or is named as `order.user`/refund beneficiary) such that the resulting `WithdrawalRequest.tokens` batch includes a native-token entry followed by an ERC20 entry for the same commitment.
2. A relayer delivers the `RedeemEscrow`/`RefundEscrow` `onAccept` message; `withdraw` sets `_filled[commitment]` and begins the loop.
3. On the native-token leg, `beneficiary.call{value: amount}("")` transfers control to the attacker's contract before `_orders[commitment][address(0)] -= amount` executes; at this point `_orders[commitment][ERC20]` is also still un-decremented.
4. Because the only guard on the next loop iteration is `_orders[...] == 0` (not an amount check), and because `_filled` was already set before the loop (blocking `cancelOrder`/`fillOrder` re-entry but not preventing observation/other side effects during the callback), the escrow bookkeeping is transiently inconsistent with the actual (not-yet-debited) balance, contradicting the CEI invariant enforced everywhere else in the codebase for this exact operation.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L623-635)
```text
    /**
     * @notice Executes an incoming post request.
     * @dev This function is called when an incoming post request is accepted.
     * It is only accessible by the host.
     * @param incoming The incoming post request data.
     */
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
