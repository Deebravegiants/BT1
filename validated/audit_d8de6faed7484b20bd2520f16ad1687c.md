### Title
Native-token escrow withdrawals in IntentGatewayV2 permanently revert when the beneficiary cannot receive raw ETH, with no ERC20/WETH fallback - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.withdraw()` pays out escrowed native-token (`token == address(0)`) order inputs with a raw `beneficiary.call{value: amount}("")` and reverts the entire withdrawal if that call fails. Unlike the sibling `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` contracts, which explicitly re-wrap failed native pushes into WETH and deliver an ERC20 transfer as a fallback so refunds/deliveries can never be permanently blocked, `IntentGatewayV2` has no such fallback for `RedeemEscrow`/`RefundEscrow` withdrawals.

### Finding Description
`withdraw()` is the internal function invoked from both `onAccept` (for `RedeemEscrow`/`RefundEscrow` incoming requests) and `cancelOrder` (same-chain path). For each escrowed token it does: [1](#0-0) 
If `token == address(0)` (native ETH) and the beneficiary is a contract without a `receive()`/payable `fallback()` (or one that reverts, e.g. a hardened vault/multisig), the `call` fails, `InsufficientNativeToken` is raised, and the **entire** `withdraw` transaction reverts — including the reduction of `_orders[commitment][token]` and the `_filled` mapping update for all other tokens in the same order. Because there is no alternate delivery path (e.g. wrapping to WETH and doing an ERC20 `transfer` as `WrappedHyperFungibleToken.onAccept`/`onPostRequestTimeout` do), the escrowed native funds for that commitment become permanently unwithdrawable through any code path: neither `RedeemEscrow` (successful fill payout) nor `RefundEscrow`/`cancelOrder` (refund) can ever succeed once the beneficiary is fixed and cannot accept a raw value transfer.

Contrast with the explicit mitigation the codebase already applies elsewhere: [2](#0-1) 

### Impact Explanation
Escrowed native ETH/BNB/TRX for an order can become permanently frozen inside `IntentGatewayV2` with no recovery mechanism — neither the original depositor (via `cancelOrder`/`RefundEscrow`) nor the solver who filled the order (via `RedeemEscrow`) can ever retrieve the funds if the destined beneficiary address cannot accept a raw native-value transfer. This is a permanent freezing-of-funds condition reachable from a single order-creation transaction, matching the Medium-severity impact bar.

### Likelihood Explanation
The beneficiary address embedded in the `Order`/`WithdrawalRequest` (`order.user` for refunds, or the filler-specified beneficiary for redemption) is attacker/user-controllable input for orders that escrow native tokens. Any smart-contract beneficiary lacking a payable fallback (intentionally or by oversight, e.g. a Gnosis Safe without a receive hook, or a contract that reverts on plain transfers) will trigger this permanently-reverting path the moment a native-token order routes through it.

### Recommendation
Apply the same fallback pattern already used in `WrappedHyperFungibleToken`: on a failed native `call`, wrap the amount into WETH (or the chain's canonical wrapped-native token) and deliver it via `IERC20.safeTransfer` to the beneficiary instead of reverting the whole withdrawal.

### Proof of Concept
1. Attacker (or unaware user) creates an order with a native-token (`address(0)`) input and sets `beneficiary`/`order.user` to a contract with no `receive()`/payable `fallback()`.
2. Order is escrowed successfully; a solver later fills it, or the order times out.
3. On `RedeemEscrow` or `RefundEscrow`/`cancelOrder`, `withdraw()` executes `beneficiary.call{value: amount}("")`, which fails.
4. `InsufficientNativeToken` reverts the entire transaction; `_orders[commitment][address(0)]` is never decremented and `_filled[commitment]` is never set — the escrowed native tokens are permanently stuck, with no alternative withdrawal path available. [3](#0-2)

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L309-321)
```text
        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
```
