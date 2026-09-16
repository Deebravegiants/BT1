### Title
Unchecked ERC20 return-value in `IntentGatewayV2.withdraw` / `SweepDust` permanently locks escrowed funds - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`evm/tron/contracts/apps/IntentGatewayV2.sol` redeems escrowed order tokens (and the fee token) using a raw low-level `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only checks the outer `success` boolean of the call, never decoding/validating the ABI-encoded `bool` return value that `transfer()` is supposed to return. This is the same class of unsafe-transfer bug flagged in the external report (blind reliance on a transfer primitive without robust failure handling), except here the failure mode is a non-reverting `false` return rather than an out-of-gas revert. The counterpart production contract `evm/src/apps/IntentGatewayV2.sol` instead uses OpenZeppelin's `SafeERC20.safeTransfer`, which correctly reverts on both revert and `false`-return failures — confirming the Tron variant diverged from the safe pattern.

### Finding Description
`withdraw()` is the single internal function that releases escrowed order inputs/output tokens to either the order's `beneficiary` (successful fill) or back to `order.user` (refund), and is reached from the unprivileged, message-driven paths `fillOrder`/`onGetResponse` (cross-chain refund) and `cancelOrder` same-chain flow. Before transferring any token it immediately marks the order as settled: [1](#0-0) 

Then, for each ERC20 token leg (and again for the accrued fee-token amount), it performs: [2](#0-1) [3](#0-2) 

The same unchecked pattern is repeated in the `SweepDust` handler: [4](#0-3) 

A low-level `.call()` returns `success = true` as long as the callee doesn't revert — it says nothing about the ABI-encoded return data. Non-reverting ERC20 implementations that return `false` on failure (e.g. legacy/non-compliant tokens, tokens with transfer restrictions/blocklists, paused tokens that return `false` instead of reverting) will make this code path treat the transfer as successful even though no tokens moved. Since `_filled[body.commitment]` is set unconditionally at the top of `withdraw()` before the token loop, and the function is `internal` with no retry entry point, any failure of this kind permanently marks the order/commitment as settled while the beneficiary never receives the underlying assets — the escrowed tokens remain custodied by the contract with no code path to reclaim them.

This directly contrasts with the sibling production contract, which uses the audited `SafeERC20.safeTransfer` (verified present via `using SafeERC20 for IERC20;` and imports in the same file), correctly reverting on a `false` return so the whole transaction (and the `_filled` write) rolls back atomically.

### Impact Explanation
Because the `_filled` map (settlement state) is written before the token transfer and is never rolled back on a merely `false`-returning transfer, this is a permanent freezing of escrowed intent funds: the settlement record shows the order as filled/refunded, but the beneficiary receives nothing and there is no fallback withdrawal function to retry. This satisfies "concrete... permanent freezing of funds" for any TRC/ERC20 token integrated with `IntentGatewayV2` on the Tron deployment that does not strictly revert on transfer failure. Given TRON's TRC20 ecosystem includes tokens with non-standard transfer semantics (some historically return `false` rather than reverting, and TRON also has native TRC10 tokens with different call semantics), this is a realistically reachable class of tokens rather than a purely theoretical one.

### Likelihood Explanation
Likelihood is medium: it requires the intent-gateway deployer/solver ecosystem to whitelist or use as `order.inputs`/`order.output.assets`/fee token a non-standard ERC20 that can return `false` on `transfer` without reverting (rather than a fully OZ-compliant token). This is plausible in a permissionless intents marketplace where arbitrary tokens can be specified as order inputs/outputs by users/solvers, and does not require any privileged or malicious actor — a single ordinary `fillOrder`/`cancelOrder`/cross-chain refund transaction with such a token as an asset triggers the bug.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` and the `SweepDust` handler with OpenZeppelin's `SafeERC20.safeTransfer` (already imported and aliased via `using SafeERC20 for IERC20;` in this same file, and already used correctly in `evm/src/apps/IntentGatewayV2.sol`), which decodes and validates the boolean return value (or handles tokens with no return data) and reverts the whole transaction — including the `_filled` state write — on any transfer failure.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) with a TRC20/ERC20 token whose `transfer()` returns `false` on failure instead of reverting (e.g. a mock `NonRevertingFailToken`).
2. Place a cross-chain order with `order.inputs`/`order.output.assets` using that token, escrowing tokens into the gateway.
3. Trigger the fill/refund path so `withdraw()` is invoked with a scenario that causes the mock token's `transfer` to return `false` (e.g. simulate a blocklist/paused condition on the token contract, or simply have the mock always return `false`).
4. Observe that `withdraw()` completes without reverting: `_filled[commitment]` is set, `EscrowReleased`/`EscrowRefunded` is emitted, `_orders[commitment][token]` is decremented — yet `token.balanceOf(beneficiary)` never increased and the tokens remain stuck in the `IntentGatewayV2` contract with no remaining withdrawal path for that commitment.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-693)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L705-708)
```text
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L717-722)
```text
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```
