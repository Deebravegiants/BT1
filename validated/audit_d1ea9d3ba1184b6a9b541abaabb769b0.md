### Title
Unclaimed native ETH/ARB escrow can become permanently locked in `IntentGatewayV2.sol` withdrawal path when the beneficiary/order.user is a non-payable contract - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The `withdraw()` function used to settle both cross-chain order fills (`RedeemEscrow`) and refunds (`RefundEscrow`/cancel) pays out escrowed native tokens via `beneficiary.call{value: amount}("")` and hard-reverts the entire settlement if the call fails, exactly the bug class described in the report (a `_to.call{value: ...}("")` transfer that reverts when the recipient contract has no `receive`/`fallback`).

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the internal `withdraw(WithdrawalRequest memory body, bool isRefund)` function iterates escrowed tokens and, for the native-token case, does: [1](#0-0) 

```
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
}
```

This function is reached from two message-driven, unprivileged paths:
1. `onAccept()` when handling an incoming `RedeemEscrow`/`RefundEscrow` ISMP `PostRequest` delivered by any relayer after Hyperbridge settlement: [2](#0-1) 
2. `onGetResponse()`, called by the host after a relayer submits the storage-membership proof for a source-side cancellation: [3](#0-2) 

The `beneficiary` in the `RedeemEscrow` case is the solver address supplied by whoever filled the order on the destination chain, and in the `RefundEscrow`/cancel case it is `order.user`, the address that placed the order. Neither of these is validated to be capable of receiving native ETH before escrow is locked at `placeOrder()` time. If the solver (or the original order placer) is a smart-contract wallet without a `receive()`/payable `fallback()`, the `.call{value: amount}("")` will always fail, causing `withdraw()` to revert on every invocation of `onAccept`/`onGetResponse` for that commitment.

Because `_filled[commitment]` is only set inside `withdraw()` (line 693) — after the point where the reverting call occurs — and the whole transaction reverts, `_filled` is never actually persisted and the escrowed native tokens recorded in `_orders[commitment][token]` remain locked in the contract indefinitely. There is no owner/governance sweep function for this state (the `SweepDust` handler only sweeps tokens reported via `SweepDust` requests for accounting dust, not stuck order escrow), and the message itself (the `RedeemEscrow`/`RefundEscrow` post or the GET response) cannot be redelivered with a different beneficiary since it is derived from the immutable `order` fields hashed into the commitment.

### Impact Explanation
Any order whose native-ETH input is meant to be released to a solver's or user's contract account without receive/fallback support becomes permanently frozen escrow inside `IntentGatewayV2`. This is direct, permanent loss of user/solver funds (native ETH/ARB) with no recovery path — matching the "permanent freezing of funds" acceptance criterion. The trigger requires no privileged action: any solver can be a non-payable contract, or any user placing/cancelling an order can use a non-payable smart-contract wallet, and the settlement message is delivered by an ordinary unprivileged relayer.

### Likelihood Explanation
Likelihood is realistic but not universal: it requires the order's `beneficiary` (solver) in `RedeemEscrow`, or `order.user` in `RefundEscrow`/cancel, to be a contract without payable fallback. Given the growing use of smart-contract wallets, multisigs, and account-abstraction wallets (including the SDK's own `SolverAccount` ERC-4337/7702 wallet referenced elsewhere in the codebase) for both order placement and solving, this is a plausible real-world scenario rather than a purely theoretical one, and once triggered, it is unrecoverable.

### Recommendation
Do not let a failed native-token push permanently revert settlement. Options:
- Wrap the native token into WETH and deliver it via a standard `IERC20.transfer`/`safeTransfer` when the direct `call` fails, mirroring the fallback pattern already implemented in the newer `WrappedHyperFungibleToken.onAccept`/`onPostRequestTimeout` (`(bool sent,) = beneficiary.call{value: amount}(""); if (!sent) { IWETH(...).deposit{value: amount}(); IERC20(...).safeTransfer(beneficiary, amount); }`), and apply the same fallback in `IntentGatewayV2.withdraw()`/`_withdraw()`.
- Alternatively, credit the failed amount to an internal pull-based claim balance for the beneficiary so the settlement (and `_filled` bookkeeping) still finalizes, and allow the beneficiary (or anyone on their behalf) to later claim the WETH-wrapped or raw ETH amount separately.

### Proof of Concept
1. Solver contract `S` (no `receive`/payable `fallback`) fills a cross-chain order whose output requires `S` to later be paid escrowed native ETH via `RedeemEscrow`.
2. The fill dispatches a `RedeemEscrow` POST request back to the source chain with `beneficiary = S`.
3. A relayer delivers the request; the source `IntentGatewayV2.onAccept` calls `withdraw(body, false)`.
4. Inside `withdraw`, `token == address(0)` branch executes `S.call{value: amount}("")`, which fails because `S` has no payable fallback.
5. `withdraw()` reverts with `InsufficientNativeToken()`; the transaction reverts entirely, so `_filled[commitment]` is never set and `_orders[commitment][address(0)]` retains the escrowed amount.
6. Because the `RedeemEscrow` message is bound to the immutable order/commitment and cannot be redelivered with a different beneficiary, and there is no governance sweep for order escrow, the ETH is permanently locked in `IntentGatewayV2`.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```
