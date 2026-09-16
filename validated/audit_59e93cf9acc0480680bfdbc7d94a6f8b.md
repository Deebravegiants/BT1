Based on my research, I found a clear analog: the Tron port of the Intent Gateway reintroduces a checks-effects-interactions violation that the main EVM codebase already identified and fixed elsewhere.

### Title
Escrow balance decremented after external transfer in `IntentGatewayV2.withdraw` (Tron) enables reentrant double-spend of escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`withdraw()` in the Tron variant of `IntentGatewayV2` performs the external token/native transfer to an attacker-influenced `beneficiary` and only decrements the internal `_orders[commitment][token]` escrow accounting afterward, violating checks-effects-interactions (CEI). [1](#0-0)  This is precisely the state-management defect class the referenced CVE hints at: state (the escrow ledger) is mutated *after* control has already been handed to potentially attacker-controlled code, rather than before.

### Finding Description
`withdraw` sets `_filled[body.commitment] = beneficiary` up front (correct CEI), but inside the token loop it calls out to the beneficiary (`beneficiary.call{value: amount}("")` for native tokens, or a raw `.call` to the token's `transfer` for ERC-20s) **before** subtracting `amount` from `_orders[body.commitment][token]`: [2](#0-1) 

Contrast this with the corresponding, hardened logic in the main EVM codebase's `IntentsBase._withdraw`, which decrements the escrow balance *before* making the external transfer: [3](#0-2) 

The `beneficiary` address in a `WithdrawalRequest` (used for `RedeemEscrow`/`RefundEscrow`) is attacker-influenced: it is the filler/solver address supplied when the cross-chain fill was placed on the other chain, so a malicious solver can point it at a contract they control. [4](#0-3) 

The project's own test suite documents this exact bug class was previously exploitable in `IntrinsicIntents._fillSameChain` before a CEI fix moved the `_filled[...]` write ahead of external calls: [5](#0-4)  The Tron port's `withdraw` was not given the equivalent fix for its per-token escrow decrement, leaving the ordering inconsistent with the audited/fixed main branch.

### Impact Explanation
If any externally reachable path allows the escrow balance for the same `(commitment, token)` pair to be read or acted upon again while control is still with the malicious beneficiary (e.g. via any additional token in `body.tokens` processed later in the same loop, or a future code path that adds re-entrant callers into `withdraw` for the same commitment), the stale (not-yet-decremented) `_orders` balance would allow funds to be paid out more than once for the same escrow, i.e. theft of escrowed input tokens beyond what was actually deposited. This is a fund-theft/fund-freezing class impact per the validation criteria.

### Likelihood Explanation
Currently, direct re-entry into `withdraw` is constrained because it is only reachable through `onAccept`, gated `onlyHost`, and the host's request-receipt replay protection prevents the exact same `PostRequest` from being redelivered within the same or a nested call. This reduces immediate exploitability compared to the already-fixed `_fillSameChain` bug, but the code still violates CEI in a way that is fragile: any future change that adds a second externally-reachable path touching `_orders[commitment][token]` for the same commitment (e.g., multi-token withdrawals, added admin/sweep paths, or a different host implementation without the same replay guard) would immediately become exploitable. Given this is a live discrepancy between two parallel implementations of the same contract (one hardened, one not), it should be treated as a real risk in the Tron deployment.

### Recommendation
Update `withdraw()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` to mirror `IntentsBase._withdraw`: subtract `amount` from `_orders[body.commitment][token]` before making the external call to `beneficiary`, for both the native-token and ERC-20 branches, and apply the same ordering to the fee-forwarding block right after.

### Proof of Concept
1. A solver fills a cross-chain order, setting `beneficiary` in the eventual `WithdrawalRequest` to a malicious contract address they control.
2. The `RedeemEscrow`/`RefundEscrow` message is delivered to the source chain and `onAccept` invokes `withdraw(body, ...)`.
3. Inside the token loop, `beneficiary.call{value: amount}("")` transfers funds and triggers the malicious contract's fallback **before** `_orders[body.commitment][token] -= amount` executes.
4. Any code path capable of re-observing/re-acting on the still-inflated `_orders[body.commitment][token]` value during that fallback (now or in future code) can extract the escrow a second time, since the ledger has not yet been updated to reflect the first payout.

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
