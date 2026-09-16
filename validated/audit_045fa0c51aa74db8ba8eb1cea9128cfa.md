### Title
Reentrant/CEI-violating escrow withdrawal in `IntentGatewayV2.withdraw` (Tron deployment) — external transfer before state update, no reentrancy guard - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron fork of the Intent Gateway contract implements escrow settlement (`withdraw`) with the exact anti-pattern flagged in the Juicebox report: it performs a low-level external call to an attacker-influenced `beneficiary` address for each escrowed token *before* decrementing the corresponding escrow accounting entry, and the file imports no `ReentrancyGuard` and applies no `nonReentrant` modifier anywhere.

### Finding Description
`withdraw()` in [1](#0-0)  sets `_filled[body.commitment] = beneficiary` once at the top, then loops over `body.tokens[]`, and for each token sends funds to `beneficiary` via a raw `.call{value: amount}("")` (native) or `.call(...IERC20.transfer...)` (ERC20) — and only *after* that external call does it execute `_orders[body.commitment][token] -= amount`: [2](#0-1) 

This is the identical checks/effects/interactions ordering flaw described in the Juicebox report (`_transferFrom` inside a loop, before internal accounting is finalized), and unlike the main, actively-maintained EVM contract, this file contains **no** `ReentrancyGuard` import and **no** `nonReentrant` modifier anywhere (confirmed absent via search across `evm/tron/**`).

By contrast, the canonical `evm/src/apps/IntentGatewayV2.sol`/`IntrinsicIntents.sol`/`ExtrinsicIntents.sol` implementation was hardened against exactly this bug class: `fillOrder` carries `nonReentrant` [3](#0-2) , and `_filled[commitment]` is now set *before* any external transfer in the output-fill loop, with a dedicated regression test suite (`IntrinsicIntentsReentrancyTest.sol`) explicitly verifying that a malicious beneficiary's `receive()` reentrant call is blocked by the `Filled()` guard [4](#0-3) . The Tron variant was not brought in line with this fix: `withdraw()` performs the external send-then-decrement per token inside a loop with no equivalent guard preventing a reentrant re-invocation of settlement logic (via `onAccept`/`onGetResponse`, both `onlyHost`) from observing stale, not-yet-decremented `_orders[commitment][token]` state.

### Impact Explanation
If `beneficiary` (attacker-controlled, since it is set from the `WithdrawalRequest.beneficiary` populated by whichever address filled the order on the destination chain) is a contract whose `receive()`/token-callback can trigger a nested processing of another already-verified ISMP delivery for the same commitment before the first token's escrow decrement completes, the escrow for that commitment can be paid out more than once, draining the gateway's locked funds — a direct theft-of-funds / broken-accounting outcome, matching the report's core impact category (bad calculations from un-completed effects, funds drained via reentrant external calls).

### Likelihood Explanation
Reachable from a single relayed/delivered settlement message (`RedeemEscrow`/`RefundEscrow`) whose beneficiary is fully attacker-chosen (the solver who filled the order, or the order's declared beneficiary). No privileged role is required to become that beneficiary; the only remaining question — which I could not fully verify given tool exhaustion — is whether the `IsmpHost`/`onAccept` call path on the Tron deployment permits a second in-flight delivery of a request touching the same commitment to be processed before the first `withdraw()` call finishes its loop (i.e., whether receipt-marking on the host precedes or follows module dispatch). This determines whether the CEI violation is trivially reentrant-exploitable today or merely a latent bug awaiting a future code path (e.g., a race between fill/redeem and cancel/refund) that reaches it. The underlying code defect itself — external call before effects, no reentrancy guard — is concretely present and verifiable in the file as-is.

### Recommendation
Bring `evm/tron/contracts/apps/IntentGatewayV2.sol` in line with the hardened main contract:
- Decrement `_orders[body.commitment][token]` (and mark `_filled`) strictly before performing any external transfer in `withdraw()`.
- Add `ReentrancyGuard`/`nonReentrant` to any externally-reachable entry points that route into `withdraw` (directly, or transitively through `onAccept`/`onGetResponse`), matching the pattern already applied to `fillOrder` in `evm/src/apps/IntentGatewayV2.sol`.
- Add a regression test mirroring `IntrinsicIntentsReentrancyTest.sol` for the Tron deployment.

### Proof of Concept
Concrete code-level PoC of the CEI violation (not yet confirmed against the host's receipt-ordering, which requires further investigation of the ISMP host/handler code path for this deployment):
1. Attacker acts as solver, fills an order on the destination chain, setting `beneficiary` to a malicious contract they control.
2. The resulting `RedeemEscrow` message is relayed to the source chain; `onAccept` invokes `withdraw(body, false)`.
3. `withdraw` iterates `body.tokens`; for the native-token entry it calls `beneficiary.call{value: amount}("")` before executing `_orders[body.commitment][token] -= amount` [5](#0-4) .
4. If the malicious `beneficiary` contract's fallback can trigger another verified delivery touching the same commitment (e.g. a duplicate/second relayed proof, or a racing `RefundEscrow`) before step 3's decrement lands, `_orders[commitment][token]` is still read as its pre-decrement (nonzero) value on re-entry, allowing the same escrow to be paid out twice.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L443-443)
```text
    function fillOrder(Order calldata order, FillOptions calldata options) public payable nonReentrant {
```

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L74-83)
```text
    /// @notice Triggered by the ETH transfer inside the fill loop.
    ///         Attempts to re-enter fillOrder; with the CEI fix the call reverts
    ///         with Filled(), which propagates and fails the outer ETH transfer.
    receive() external payable {
        if (armed && !reentered) {
            reentered = true;
            gateway.fillOrder(storedOrder, storedOptions);
        }
    }
}
```
