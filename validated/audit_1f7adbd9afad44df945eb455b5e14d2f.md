### Title
Griefing/DoS via unconditional native-ETH push to attacker-controlled `beneficiary` reverts intent fills - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
The intents escrow contracts (`IntentGatewayV2`, `ExtrinsicIntents`, `IntrinsicIntents`) pay out native ETH to an order's `output.beneficiary` (and refund/escrow release recipients) using a raw `call{value: amount}("")` that **reverts the entire transaction** if the recipient cannot accept ETH. Because `beneficiary` is a fully attacker-controlled `bytes32` field on the order (not restricted to `msg.sender`), a malicious order creator can set it to a contract with no `receive()`/payable `fallback()`, permanently preventing that order from ever being filled and reverting any solver's `fillOrder`/`_fillCrossChain` transaction that attempts to service it.

### Finding Description
`IntentsBase._sendValue` performs an unconditional native transfer and reverts the whole call on failure: [1](#0-0) 

This helper is used to pay the `beneficiary` from escrow-release/refund paths (`_withdraw`, `_sweepDust`): [2](#0-1) 

It is also used directly in the cross-chain fill path, where `beneficiary` comes straight from `order.output.beneficiary`, a value fully controlled by whoever placed the order (not validated to be payable or even correspond to `order.user`): [3](#0-2) 

The same-chain fill path (`IntrinsicIntents.sol`) inlines the identical unconditional-revert pattern for gas reasons: [4](#0-3) 

None of these paths check whether `beneficiary` can actually receive ETH before committing to the transfer, nor do they fall back to a pull-payment/WETH-wrap pattern the way `WrappedHyperFungibleToken.onAccept` does elsewhere in the codebase (which retries via WETH wrap+ERC20 transfer on failure): [5](#0-4) 

### Impact Explanation
An order placer chooses `order.output.assets` to include `token = address(0)` (native ETH) and sets `order.output.beneficiary` to a contract address without a payable receive/fallback function. Any solver who then calls `fillOrder`/`_fillCrossChain` to service that order will have their transaction unconditionally revert inside `_sendValue`/the inline `beneficiary.call`, wasting gas and making the order permanently unfillable by any solver, for as long as the order remains open. This is a denial-of-service on the intents escrow/solver-fill route — the exact bug class in the reported analog (recipient inability to accept ETH causes otherwise-valid transactions to revert), applied here to the reachable, unprivileged `fillOrder` entrypoint rather than a reactor `_fill`.

### Likelihood Explanation
High likelihood of occurrence for any solver naive enough not to pre-simulate the fill, and the condition is trivially and cheaply set up by any order creator (deploy a bare non-payable contract, use its address as `beneficiary`). No special privileges are required — `placeOrder` is a public, unprivileged entrypoint and `output.beneficiary` is not validated.

### Recommendation
- Validate that native-ETH `output.beneficiary` addresses are payable at order-placement time (e.g., a bounded-gas probe `.call{value:0}("")` or requiring EOA/known-payable contracts), or
- Replace the push-based `_sendValue` for native ETH outputs with a pull-payment/escrow-credit pattern (credit an internal balance the beneficiary can withdraw) so a failing transfer cannot block the solver's `fillOrder` transaction, mirroring the WETH-wrap fallback already used in `WrappedHyperFungibleToken.onAccept`/`onPostRequestTimeout`.

### Proof of Concept
1. Attacker deploys `Trap` — a contract with no `receive()`/payable `fallback()`.
2. Attacker calls `placeOrder` with `order.output.assets = [{token: address(0), amount: X}]` and `order.output.beneficiary = address(Trap)`, escrowing legitimate input tokens.
3. Any solver calls `fillOrder`/`_fillCrossChain` with sufficient `msg.value` to cover `X`; execution reaches `_sendValue(beneficiary, ...)` in `IntentsBase.sol:419` (via `ExtrinsicIntents.sol:189` or `IntrinsicIntents.sol:99`), the `call` fails, and the whole fill reverts, refunding nothing to the solver but consuming their gas.
4. The order remains permanently unfillable until it expires and is cancelled by its creator, who set the trap and thus is unaffected (their own refund goes to `order.user`, which they control and made payable).

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L418-422)
```text
    /// @dev Native transfer that reverts with `InsufficientNativeToken` if refused.
    function _sendValue(address to, uint256 amount) internal {
        (bool sent,) = to.call{value: amount}("");
        if (!sent) revert InsufficientNativeToken();
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L186-190)
```text
            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L95-100)
```text
            if (token == address(0)) {
                if (msgValue < beneficiaryTotal + protocolShare) revert InsufficientNativeToken();
                msgValue -= (beneficiaryTotal + protocolShare);
                // Inline, not `_sendValue`: this loop is at the via-ir stack limit.
                (bool sent,) = beneficiary.call{value: beneficiaryTotal}("");
                if (!sent) revert InsufficientNativeToken();
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L316-321)
```text
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
```
