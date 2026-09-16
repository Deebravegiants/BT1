### Title
Fee-on-transfer input tokens cause escrow ledger over-crediting in Tron `IntentGatewayV2.placeOrder` - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.placeOrder` on the Tron variant of the Intent Gateway credits the escrow ledger (`_orders[commitment][token]`) with the nominal (fee-reduced-for-protocol-fee-only) input amount instead of the amount actually received by the contract via `safeTransferFrom`. For deflationary/fee-on-transfer ERC-20 input tokens, this creates a permanent mismatch between the ledger's claimed escrow balance and the contract's real token balance.

### Finding Description
In the non-predispatch escrow path of `placeOrder`: [1](#0-0) 

```
} else {
    for (uint256 i; i < inputsLen;) {
        if (order.inputs[i].amount == 0) revert InvalidInput();
        address token = address(uint160(uint256(order.inputs[i].token)));
        if (token == address(0)) {
            if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
            msgValue -= order.inputs[i].amount;
        } else {
            IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
        }
        // Store reduced amount (after protocol fees) in escrow
        _orders[commitment][token] += reducedInputs[i].amount;
        unchecked { ++i; }
    }
}
```

`safeTransferFrom` is called for `order.inputs[i].amount`, but for a fee-on-transfer token the contract's actual balance increase is less than that amount (the token itself deducts a fee during transfer). The code never measures the actual balance delta — it simply credits `reducedInputs[i].amount` (the requested amount minus the *protocol* fee, unrelated to the token's own transfer fee) to `_orders[commitment][token]`.

This is the same root-cause class as the referenced Connext finding: code assumes `amount requested == amount received` for arbitrary ERC-20 tokens, and performs internal accounting based on the nominal amount rather than the measured balance delta.

Note that the primary (non-Tron) EVM `IntentGatewayV2.sol` was hardened against exactly this bug class — it measures actual received balances before/after transfers and mutates `order.inputs` to the real received amount: [2](#0-1) 

The Tron deployment lacks this fix in its no-predispatch path, and even its predispatch path only checks `balance >= requiredAmount` (revert-on-shortfall) but still credits `_orders` with `reducedInputs[i].amount` rather than the true dust-adjusted received amount, so any shortfall attributable to per-transfer fees is not reflected in escrow accounting.

### Impact Explanation
Because `_orders[commitment][token]` can be inflated beyond the contract's real balance of a fee-on-transfer token, later legitimate withdrawals for other orders denominated in that same token can fail: `_withdraw`/`safeTransfer` calls will revert once the actual token balance is exhausted by earlier escrow releases, permanently freezing the affected users' funds (their escrow entries exist on paper but the underlying tokens are gone). Conversely, because escrow of one order can draw down real token balance that was nominally "owed" to a different order (all fee-on-transfer input tokens share the same contract-wide balance pool), a user's cancel/withdraw could succeed at the expense of another order's escrow becoming unbacked — a straightforward doubling/insolvency of the promised balance, i.e., "theft" of shared pool liquidity between unrelated orders and, in the worst case, permanent loss of funds for whichever order's withdrawal is processed last.

This matches the accepted impact categories: permanent freezing of funds and unbacked/insolvent internal accounting (analogous to unbacked mint), reachable by any unprivileged user submitting an order via `placeOrder` with a fee-on-transfer token — no admin/governance/relayer privilege required.

### Likelihood Explanation
Likelihood is Medium: the bug only manifests for tokens that apply a fee/tax on `transfer`/`transferFrom` (e.g., SafeMoon-style tokens, some reflection/rebasing tokens). Standard tokens (USDC, DAI, WETH, etc.) are unaffected. However, nothing in the contract restricts which ERC-20s can be used as `order.inputs[i].token`, so an attacker (or an unaware integrator) can trivially trigger this by placing an order with any such token, and the accounting corruption is deterministic and always present for that token class — it is not a probabilistic or race-dependent condition.

### Recommendation
Mirror the fix already present in the primary (non-Tron) `IntentGatewayV2.sol`: measure the contract's token balance immediately before and after each `safeTransferFrom` call, use the actual delta as the amount escrowed (and as the basis for `reducedInputs`/commitment calculation), rather than trusting `order.inputs[i].amount`. Apply the same balance-diffing approach to the predispatch sweep path so that `_orders[commitment][token]` is always credited with exactly the token amount the contract can prove it holds.

### Proof of Concept
1. Deploy a fee-on-transfer ERC-20 (e.g., 5% fee burned on every transfer) and use it as `order.inputs[0].token` with `amount = 1000e18` in a call to the Tron `IntentGatewayV2.placeOrder`.
2. `safeTransferFrom(msg.sender, address(this), 1000e18)` executes; the contract's actual token balance increases by only 950e18 (5% burned).
3. `_orders[commitment][token] += reducedInputs[0].amount` credits (assuming 0% protocol fee) the full 1000e18 to the escrow ledger, while the contract only holds 950e18 of that token in total.
4. Repeat with a second, unrelated order using the same fee-on-transfer token. The sum of all `_orders[...][token]` entries across orders now exceeds the contract's real balance of that token by the accumulated transfer-fee amount.
5. When solvers/users withdraw or cancel these orders (`safeTransfer(beneficiary, escrowedAmount)`), the contract eventually cannot satisfy all claims: the last order(s) to be withdrawn revert with an ERC-20 balance-insufficient error, permanently locking those users' nominal escrow, while earlier withdrawals silently consumed value that was, per the ledger, allocated to the still-outstanding orders.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-469)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L313-323)
```text
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }
```
