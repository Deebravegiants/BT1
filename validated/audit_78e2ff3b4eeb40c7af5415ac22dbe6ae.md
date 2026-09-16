## Analog Found

The Hats-finance ether-fi report's core defect — an **external call executed before internal accounting is finalized**, opening a reentrancy window that lets an attacker manipulate escrow/shares state before the outer function uses it — has a direct analog in the Tron variant of `IntentGatewayV2`'s `withdraw()` function.

### Title
Checks-Effects-Interactions violation in `IntentGatewayV2.withdraw()` allows reentrant drain of escrowed order tokens - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`withdraw()`, the function that releases escrowed order tokens to a beneficiary after a cross-chain `RedeemEscrow`/`RefundEscrow` message or GET-response is delivered by the host, performs the token/ETH transfer to an attacker-controlled `beneficiary` **before** decrementing the escrow accounting (`_orders[body.commitment][token]`) and **before** validating that the requested `amount` does not exceed what is actually escrowed.

### Finding Description
In `withdraw()`: [1](#0-0) 

the sequence is:
1. `_orders[body.commitment][token] == 0` is checked — but this only verifies the slot is *non-zero*, not that `amount <= _orders[body.commitment][token]`.
2. The full `amount` is sent out immediately via `beneficiary.call{value: amount}("")` (native token) or `token.call(...transfer...)` (ERC-20) — handing execution control to the attacker-controlled `beneficiary`/`token` contract.
3. Only **after** that external call does the code execute `_orders[body.commitment][token] -= amount`, finalizing the accounting.

This is the same bug class as the ether-fi finding: an externally-controlled callback (there, `_safeMint`'s `onERC721Received`; here, the ETH `.call` to `beneficiary` or the malicious-token `transfer` hook) fires **before** the contract's internal share/escrow bookkeeping is updated, so any code the attacker runs during that callback observes stale, not-yet-decremented state.

Critically, unlike the sibling `IntentsBase.sol._withdraw` implementation, this Tron `withdraw()` never re-checks a "filled" guard before or during the loop to block reentrant calls into itself or into other order-management entry points that read `_orders[body.commitment][token]`. The project's own `IntentGatewayV2` (EVM, main branch) had this exact reentrancy class fixed via a CEI pattern (`_filled[commitment] = msg.sender` set *before* any external call, enforced by a `Filled()` guard checked on `fillOrder`), as documented extensively in the dedicated regression test suite: [2](#0-1) [3](#0-2) 

That fix was not propagated to the Tron contract's `withdraw()`, which still transfers value out via low-level `.call` prior to updating `_orders[...]`, and — for multi-token withdrawal requests (`body.tokens.length > 1`) — the first token's external call can reenter before the loop even reaches the accounting update for subsequent tokens/fees in the same `body.commitment`.

### Impact Explanation
An attacker who controls the `beneficiary` address (as set in the cross-chain `WithdrawalRequest`, itself constructed from order data the attacker/solver controls) or who supplies a malicious ERC-20 with a transfer hook can reenter during the payout call. Because the escrow debit (`_orders[body.commitment][token] -= amount`) and the fee debit both occur strictly after the external call, and because the guard only checks non-zero rather than sufficiency, reentrant invocation of any function that reads or mutates `_orders[body.commitment][...]` (or a second iteration of the same `withdraw` loop reached through a crafted reentrant path) can observe/consume the pre-decrement balance, enabling theft of escrowed funds beyond what was legitimately allocated to the commitment — i.e., concrete theft of escrowed protocol/user funds, matching the "unbacked mint / concrete theft" impact bar.

### Likelihood Explanation
`withdraw()` is reached via `onAccept` for `RequestKind.RedeemEscrow`/`RefundEscrow` and via `onGetResponse`, both triggered by a relayer delivering a verified cross-chain message/proof — a standard, unprivileged relay operation within scope. The attacker fully controls the `beneficiary` field of the order (and, for ERC-20 outputs, can choose to route through a token they control if such a token is accepted by the gateway's fee/token allowlist), so triggering the callback requires no special privilege beyond normal solver/user interaction with the intents flow.

### Recommendation
Apply the same CEI fix already used in `evm/src/apps/intentsv2/IntentsBase.sol._withdraw` and `IntrinsicIntents._fillSameChain`: decrement `_orders[body.commitment][token]` (and validate `amount <= escrowed`) *before* making the external transfer call, and/or gate reentry with a `_filled`/lock check enforced at the very top of `withdraw()` prior to any external call.

### Proof of Concept
1. Attacker (as solver/user) places an order whose `beneficiary` is a malicious contract, or whose output token is malicious with a transfer hook.
2. A relayer delivers a valid `RedeemEscrow` message, invoking `onAccept` → `withdraw(body, false)`. [4](#0-3) 
3. Inside `withdraw()`, the ETH `.call`/token `transfer` to `beneficiary` fires before `_orders[body.commitment][token] -= amount` executes. [5](#0-4) 
4. During that callback, the attacker's contract reenters the gateway (e.g., via another order/withdrawal path touching the same commitment/token accounting), reading the stale, un-decremented `_orders[body.commitment][token]` to extract more value than is actually escrowed.

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

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L212-222)
```text
    /**
     * @dev Same-chain fee theft is now blocked by the CEI fix.
     *
     * Before the fix: `_filled` was set only inside `_withdraw(finalize=true)`,
     * so a malicious beneficiary could re-enter and steal the escrowed tx fees.
     *
     * After the fix: `_filled[commitment] = msg.sender` is set at the top of
     * `_fillSameChain`, before the output loop. The reentrant `fillOrder` call
     * therefore hits `Filled()`, propagates through `receive()`, causes the ETH
     * transfer to return false, and the outer call reverts with
     * `InsufficientNativeToken()` — rolling back all state changes.
```
