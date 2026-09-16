## Title
Unchecked ERC20 `transfer()` return value in `IntentGatewayV2.withdraw()` / `SweepDust` allows escrow to be marked settled without tokens actually moving - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` still uses raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` calls when paying out escrowed funds, checking only that the call itself did not revert (`success`) but never decoding/validating the ABI-encoded `bool` return value of `transfer()`. This is the exact bug class from the external report (ERC-20 standard permits `transfer`/`transferFrom` to return `false` instead of reverting on failure, and callers "MUST handle false from returns"). The rest of the codebase (the mainline EVM `IntentGatewayV2.sol`, `ExtrinsicIntents.sol`, `IntrinsicIntents.sol`, `WrappedHyperFungibleToken.sol`) has already been hardened with OpenZeppelin's `SafeERC20`/`safeTransfer`/`safeTransferFrom` wrappers [1](#0-0) , but the Tron fork was not updated to match.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the `withdraw()` function — which releases escrowed order inputs to a beneficiary once a `RedeemEscrow`/`RefundEscrow` message is authenticated, or once a cancellation GET-response confirms the order was never filled — pays out tokens like this:

```solidity
function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
    ...
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
        ...
``` [2](#0-1) 

The fee payout inside the same function has an identical pattern:
```solidity
(bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
if (!success) revert TransferFailed();
``` [3](#0-2) 

And the protocol-controlled `SweepDust` handler in `onAccept()`:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
if (!success) revert TransferFailed();
``` [4](#0-3) 

In all three sites, `success` only reflects whether the low-level `.call` reverted — it does **not** decode the return data to confirm `transfer()` actually returned `true`. Per the ERC-20 spec, a token is permitted to return `false` on failure instead of reverting, and "callers MUST NOT assume that false is never returned." Because `token` is arbitrary and fully attacker-controlled (it is whatever `order.inputs[i].token` the order creator chose when calling `placeOrder`), an order can be created using a token whose `transfer()` implementation returns `false` (or simply no-ops and returns nothing decodable as `true`, or is non-standard) while still returning `success = true` from the raw `.call`. The escrow accounting (`_orders[body.commitment][token] -= amount`, and `_filled[commitment] = beneficiary`) is unconditionally updated as if the payment succeeded, even though no tokens were actually transferred to the beneficiary.

### Impact Explanation
This breaks the invariant that escrow release state and actual token custody stay in sync. The contract's internal book-keeping (`_orders`) is decremented/zeroed and the order is marked `_filled`/finalized as though the beneficiary was paid, while the tokens can remain permanently stuck in the `IntentGatewayV2` contract (permanent freezing/loss for the intended beneficiary — the solver who filled a cross-chain order, or the user reclaiming a refund), since the same commitment cannot be withdrawn twice (`UnknownOrder` revert on the next attempt). Any relayer or solver interacting with such an order is affected; this reachable purely by an unprivileged order creator picking a non-standard token as the escrowed input asset. This matches the "permanent freezing of funds" / "unauthorized app action" categories called out in the validation criteria, and directly mirrors the reported bug class (unchecked ERC20 return values on the payout leg of an escrow/auction settlement, allowing settlement bookkeeping to advance without the underlying transfer succeeding).

### Likelihood Explanation
Likelihood is Medium-High: any unprivileged user can call `placeOrder` with an arbitrary `token` address for `order.inputs`, including a purpose-built contract whose `transfer()` returns `false`/garbage instead of reverting. No special privileges, governance, or off-chain component compromise are required — only a single `placeOrder` call plus the normal cross-chain fill/redeem or cancel/refund flow that triggers `withdraw()`.

### Recommendation
Replace all raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` payout patterns in `evm/tron/contracts/apps/IntentGatewayV2.sol` (`withdraw()` token loop, `withdraw()` fee payout, and the `SweepDust` branch of `onAccept()`) with OpenZeppelin's `SafeERC20.safeTransfer`, exactly as already done in the mainline EVM `IntentGatewayV2.sol` / `IntentsBase.sol`. This ensures a `false` return value reverts the entire transaction instead of allowing escrow state to advance without a successful transfer.

### Proof of Concept
1. Deploy a malicious ERC20-like token whose `transfer(address,uint256)` function returns `false` (or returns no data that decodes to `true`) but does not revert, while `transferFrom` behaves normally (or is unused since placement inputs still use `safeTransferFrom`, so the token appears to onboard normally).
2. Call `placeOrder` on Tron `IntentGatewayV2` with this token as `order.inputs[0].token`; the deposit into escrow via `safeTransferFrom` succeeds (attacker actually deposits, or in a refund/cancel scenario the same token can be reused since accounting only depends on the token's `transfer` behavior at payout time).
3. Trigger the corresponding `RedeemEscrow`/`RefundEscrow` flow (e.g., cancel after expiry, or complete a cross-chain fill) so `withdraw()` is invoked.
4. Observe `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` returns `success = true` (call did not revert) even though the token's internal logic returned `false`/moved no funds; `_orders[body.commitment][token] -= amount` executes and the order is marked filled/refunded, permanently locking the escrowed balance in the contract with no recorded claim left for the true beneficiary.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L674-676)
```text
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-722)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```
